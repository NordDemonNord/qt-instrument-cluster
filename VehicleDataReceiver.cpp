#include "VehicleDataReceiver.h"
#include <QCanBus>
#include <QCanBusFrame>
#include <QDebug>
#include <QJsonDocument>
#include <QJsonObject>
#include <QNetworkRequest>
#include <QUrl>
#include <QtMath>

namespace {
// Адрес ESP32 в режиме SoftAP
const QString kEspUrl = QStringLiteral("http://192.168.4.1/data");
constexpr int kPollIntervalMs = 100;   // опрашивать 10 раз в секунду

// Значения-заглушки «нет данных» из CAN-матрицы. Если ESP прислал их —
// сигнал невалиден, значение не обновляем (оставляем последнее валидное).
constexpr int kNoDataU16 = 65535;
constexpr int kNoDataU8  = 255;

// Частота обновления demo-данных: ~30 кадров в секунду.
constexpr int kDemoIntervalMs = 33;

// --- Источник can ---
// Интерфейс SocketCAN по умолчанию. Можно переопределить переменной
// окружения VEHICLE_CAN_INTERFACE (например, vcan0 для тестов без железа).
const QString kCanInterface = QStringLiteral("can0");

// Кадр скорости: ID 0x1A0, 2 байта, uint16, 0.01 км/ч на бит, Motorola.
constexpr quint32 kSpeedFrameId    = 0x1A0;
constexpr int     kSpeedFrameLen   = 2;
constexpr int     kSpeedRawPerKmh  = 100;   // 1 км/ч = 100 единиц сырого значения

// Если кадров нет дольше этого времени - связь потеряна.
// STM сейчас шлёт кадр раз в 500 мс, поэтому берём с запасом.
constexpr int kCanTimeoutMs = 1000;
}

VehicleDataReceiver::VehicleDataReceiver(QObject *parent)
    : QObject(parent)
{
    // По умолчанию - http, чтобы проекты, которые не знают про эту
    // переменную, продолжали работать как раньше.
    const QString source = qEnvironmentVariable("VEHICLE_DATA_SOURCE", "http").toLower();

    if (source == QLatin1String("demo")) {
        startDemoSource();
    } else if (source == QLatin1String("can")) {
        startCanSource();
    } else {
        if (source != QLatin1String("http")) {
            qWarning() << "VehicleDataReceiver: unknown VEHICLE_DATA_SOURCE" << source
                       << "- falling back to http";
        }
        startHttpSource();
    }
}

void VehicleDataReceiver::startHttpSource()
{
    m_sourceName = QStringLiteral("ESP32");

    connect(&m_network, &QNetworkAccessManager::finished,
            this, &VehicleDataReceiver::onReplyFinished);

    connect(&m_pollTimer, &QTimer::timeout,
            this, &VehicleDataReceiver::requestData);

    m_pollTimer.start(kPollIntervalMs);

    qInfo() << "VehicleDataReceiver: source = http, polling" << kEspUrl
            << "every" << kPollIntervalMs << "ms";
}

void VehicleDataReceiver::startDemoSource()
{
    m_sourceName = QStringLiteral("DEMO");

    connect(&m_demoTimer, &QTimer::timeout,
            this, &VehicleDataReceiver::updateDemo);

    m_demoClock.start();
    m_demoTimer.start(kDemoIntervalMs);

    // Данные генерируются локально - "связь" есть всегда.
    setConnected(true);

    qInfo() << "VehicleDataReceiver: source = demo, update every"
            << kDemoIntervalMs << "ms";
}

void VehicleDataReceiver::startCanSource()
{
    m_sourceName = QStringLiteral("CAN");

    const QString interfaceName = qEnvironmentVariable("VEHICLE_CAN_INTERFACE", kCanInterface);

    // QCanBus - фабрика: по имени плагина ("socketcan") создаёт объект
    // устройства и отдаёт указатель на него. Если плагина нет (не установлен
    // qtserialbus-plugins), вернёт nullptr и опишет причину в errorString.
    QString errorString;
    m_canDevice = QCanBus::instance()->createDevice(
        QStringLiteral("socketcan"), interfaceName, &errorString);

    if (!m_canDevice) {
        qWarning() << "VehicleDataReceiver: cannot create CAN device:" << errorString;
        return;   // связи нет, m_connected остаётся false
    }

    // Родитель - этот объект: Qt сам удалит устройство вместе с ним.
    m_canDevice->setParent(this);

    // Устройство подаёт сигнал framesReceived, когда в его очереди есть кадры.
    connect(m_canDevice, &QCanBusDevice::framesReceived,
            this, &VehicleDataReceiver::onCanFramesReceived);

    connect(m_canDevice, &QCanBusDevice::errorOccurred,
            this, [this](QCanBusDevice::CanBusError) {
                // Пишем в лог только ошибки при живой связи, иначе при
                // отсутствии can0 лог забьётся повторными попытками раз в секунду.
                if (m_connected) {
                    qWarning() << "VehicleDataReceiver: CAN error:" << m_canDevice->errorString();
                }
            });

    // Сторож: однократный таймер, каждый пришедший кадр запускает его заново.
    // Если он всё-таки сработал - кадров не было kCanTimeoutMs.
    m_canWatchdog.setSingleShot(true);
    m_canWatchdog.setInterval(kCanTimeoutMs);
    connect(&m_canWatchdog, &QTimer::timeout,
            this, &VehicleDataReceiver::onCanTimeout);

    // Открыть сокет и привязать его к интерфейсу. Если can0 ещё нет
    // (slcand не запущен), не страшно: сторож будет пробовать снова.
    if (!m_canDevice->connectDevice()) {
        qWarning() << "VehicleDataReceiver: cannot connect to" << interfaceName
                   << ":" << m_canDevice->errorString() << "- will retry";
    }

    m_canWatchdog.start();

    qInfo() << "VehicleDataReceiver: source = can, interface" << interfaceName
            << ", speed frame ID" << Qt::hex << kSpeedFrameId
            << Qt::dec << ", timeout" << kCanTimeoutMs << "ms";
}

void VehicleDataReceiver::onCanFramesReceived()
{
    // Забрать из очереди все накопившиеся кадры разом.
    const QList<QCanBusFrame> frames = m_canDevice->readAllFrames();

    for (const QCanBusFrame &frame : frames) {
        // Пропускаем служебные кадры (ошибки шины, remote-запросы)
        // и кадры с расширенным 29-битным ID.
        if (!frame.isValid()
            || frame.frameType() != QCanBusFrame::DataFrame
            || frame.hasExtendedFrameFormat()) {
            continue;
        }

        // Любой нормальный кадр значит, что связь есть: сбросить сторожа.
        setConnected(true);
        m_canWatchdog.start();

        if (frame.frameId() == kSpeedFrameId) {
            const QByteArray data = frame.payload();
            if (data.size() != kSpeedFrameLen) {
                qWarning() << "VehicleDataReceiver: speed frame with DLC" << data.size()
                           << "instead of" << kSpeedFrameLen;
                continue;
            }

            // QByteArray хранит char. На x86 char знаковый: байт 0xE0 был бы -32.
            // Поэтому сначала приводим каждый байт к беззнаковому quint8.
            const quint8 high = static_cast<quint8>(data[0]);   // Motorola: старший байт первым
            const quint8 low  = static_cast<quint8>(data[1]);
            const quint16 raw = static_cast<quint16>((high << 8) | low);

            // Сырое значение в сотых км/ч -> целые км/ч с округлением.
            setSpeed(qRound(static_cast<double>(raw) / kSpeedRawPerKmh));
        }
        // Остальные ID пока не разбираем.
    }
}

void VehicleDataReceiver::onCanTimeout()
{
    // Кадров нет kCanTimeoutMs. Как в настоящей приборке: стрелку в ноль,
    // индикатор "нет связи". Выдуманные данные при потере связи не показываем.
    if (m_connected) {
        qWarning() << "VehicleDataReceiver: no CAN frames for" << kCanTimeoutMs << "ms";
    }
    setConnected(false);
    setSpeed(0);

    // Переподключиться: если slcand перезапустили, can0 создан заново,
    // и старый сокет к нему уже не привязан.
    // disconnectDevice/connectDevice ругаются в лог, если вызвать их не в том
    // состоянии, поэтому сначала проверяем state().
    if (m_canDevice->state() == QCanBusDevice::ConnectedState) {
        m_canDevice->disconnectDevice();
    }
    if (m_canDevice->state() == QCanBusDevice::UnconnectedState) {
        m_canDevice->connectDevice();
    }

    // Проверить снова через kCanTimeoutMs.
    m_canWatchdog.start();
}

void VehicleDataReceiver::updateDemo()
{
    // Время с запуска в секундах - из него считаются все значения.
    const double t = m_demoClock.elapsed() / 1000.0;

    // Плавная волна 0..1..0 с заданным периодом.
    // cos() даёт 1..-1..1, поэтому (1 - cos) / 2 начинается с 0 -
    // стрелки стартуют с нуля, как при включении зажигания.
    auto wave = [t](double periodSec) {
        return (1.0 - qCos(2.0 * M_PI * t / periodSec)) / 2.0;
    };

    setSpeed(qRound(220.0 * wave(10.0)));            // 0..220 км/ч за 10 с
    setRpm(qRound(800.0 + 6200.0 * wave(4.0)));      // 800..7000 об/мин за 4 с
    setCoolant(qRound(50.0 + 80.0 * wave(20.0)));    // 50..130 °C за 20 с
    setFuelLevel(qRound(100.0 * wave(30.0)));        // 0..100 % за 30 с
    setExternalTemp(qRound(-20.0 + 50.0 * wave(60.0)));
    setOdometer(123456 + static_cast<int>(t));       // +1 км в секунду
    setTrip(2340 + static_cast<int>(t * 10.0));      // десятые км: +1 км в секунду
    setHours(18);
    setMinutes(static_cast<int>(t / 60.0) % 60);     // «часы» идут, 1 мин = 1 мин
    setGear(static_cast<int>(t / 3.0) % 5);          // P R N D M, по 3 с

    // Сигнализаторы: 2 с горят, 2 с не горят.
    const bool on = static_cast<int>(t / 2.0) % 2 == 0;
    setAllTellTales(on);
}

void VehicleDataReceiver::setFlag(bool &field, bool value,
                                  void (VehicleDataReceiver::*changed)())
{
    if (field == value) return;
    field = value;
    emit (this->*changed)();
}

void VehicleDataReceiver::setAllTellTales(bool on)
{
    setFlag(m_turnLeft,  on, &VehicleDataReceiver::turnLeftChanged);
    setFlag(m_turnRight, on, &VehicleDataReceiver::turnRightChanged);
    setFlag(m_highBeam,  on, &VehicleDataReceiver::highBeamChanged);
    setFlag(m_lowBeam,   on, &VehicleDataReceiver::lowBeamChanged);
    setFlag(m_position,  on, &VehicleDataReceiver::positionChanged);
    setFlag(m_frontFog,  on, &VehicleDataReceiver::frontFogChanged);
    setFlag(m_rearFog,   on, &VehicleDataReceiver::rearFogChanged);
    setFlag(m_seatbelt,  on, &VehicleDataReceiver::seatbeltChanged);
    setFlag(m_doorOpen,  on, &VehicleDataReceiver::doorOpenChanged);
    setFlag(m_hoodOpen,  on, &VehicleDataReceiver::hoodOpenChanged);
    setFlag(m_trunkOpen, on, &VehicleDataReceiver::trunkOpenChanged);

    setFlag(m_checkEngine,   on, &VehicleDataReceiver::checkEngineChanged);
    setFlag(m_oilPressure,   on, &VehicleDataReceiver::oilPressureChanged);
    setFlag(m_overheat,      on, &VehicleDataReceiver::overheatChanged);
    setFlag(m_absFault,      on, &VehicleDataReceiver::absFaultChanged);
    setFlag(m_espFault,      on, &VehicleDataReceiver::espFaultChanged);
    setFlag(m_espBlink,      on, &VehicleDataReceiver::espBlinkChanged);
    setFlag(m_espOff,        on, &VehicleDataReceiver::espOffChanged);
    setFlag(m_brakeFault,    on, &VehicleDataReceiver::brakeFaultChanged);
    setFlag(m_steeringFault, on, &VehicleDataReceiver::steeringFaultChanged);
    setFlag(m_airbagFault,   on, &VehicleDataReceiver::airbagFaultChanged);
    setFlag(m_battery,       on, &VehicleDataReceiver::batteryChanged);
    setFlag(m_parkBrake,     on, &VehicleDataReceiver::parkBrakeChanged);
    setFlag(m_pressBrake,    on, &VehicleDataReceiver::pressBrakeChanged);
    setFlag(m_fuelLow,       on, &VehicleDataReceiver::fuelLowChanged);
}

void VehicleDataReceiver::requestData()
{
    QNetworkRequest request{QUrl(kEspUrl)};
    m_network.get(request);
}

void VehicleDataReceiver::onReplyFinished(QNetworkReply *reply)
{
    reply->deleteLater();

    if (reply->error() != QNetworkReply::NoError) {
        qWarning() << "VehicleDataReceiver: request failed:" << reply->errorString();
        setConnected(false);
        return;
    }

    setConnected(true);

    const QByteArray payload = reply->readAll();

    QJsonParseError parseError;
    const QJsonDocument doc = QJsonDocument::fromJson(payload, &parseError);

    if (parseError.error != QJsonParseError::NoError || !doc.isObject()) {
        qWarning() << "VehicleDataReceiver: bad JSON:" << payload;
        return;
    }

    const QJsonObject obj = doc.object();

    // --- Аналоговые (с фильтром «нет данных») ---
    if (obj.contains("speed")) {
        int v = obj.value("speed").toInt();
        if (v != kNoDataU16) setSpeed(v);
    }
    if (obj.contains("rpm")) {
        int v = obj.value("rpm").toInt();
        if (v != kNoDataU16) setRpm(v);
    }
    if (obj.contains("coolant")) {
        int v = obj.value("coolant").toInt();
        if (v != kNoDataU8) setCoolant(v);
    }
    if (obj.contains("temp")) {
        int v = obj.value("temp").toInt();
        if (v != kNoDataU8) setExternalTemp(v);
    }
    if (obj.contains("odometer")) {
        setOdometer(obj.value("odometer").toInt());
    }
    if (obj.contains("fuel")) {
        setFuelLevel(obj.value("fuel").toInt());
    }
    if (obj.contains("gear")) {
        int v = obj.value("gear").toInt();
        if (v != kNoDataU8) setGear(v);
    }
    if (obj.contains("trip")) {
        setTrip(obj.value("trip").toInt());
    }
    if (obj.contains("hours")) {
        setHours(obj.value("hours").toInt());
    }
    if (obj.contains("minutes")) {
        setMinutes(obj.value("minutes").toInt());
    }

    // --- Сигнализаторы кузова/света (0x600) ---
    auto flag = [&obj](const char *key, bool cur, auto setter) {
        if (obj.contains(key)) {
            bool v = obj.value(key).toInt() != 0;
            if (v != cur) setter(v);
        }
    };
    flag("turnLeft",  m_turnLeft,  [this](bool v){ m_turnLeft = v;  emit turnLeftChanged(); });
    flag("turnRight", m_turnRight, [this](bool v){ m_turnRight = v; emit turnRightChanged(); });
    flag("highBeam",  m_highBeam,  [this](bool v){ m_highBeam = v;  emit highBeamChanged(); });
    flag("lowBeam",   m_lowBeam,   [this](bool v){ m_lowBeam = v;   emit lowBeamChanged(); });
    flag("position",  m_position,  [this](bool v){ m_position = v;  emit positionChanged(); });
    flag("frontFog",  m_frontFog,  [this](bool v){ m_frontFog = v;  emit frontFogChanged(); });
    flag("rearFog",   m_rearFog,   [this](bool v){ m_rearFog = v;   emit rearFogChanged(); });
    flag("seatbelt",  m_seatbelt,  [this](bool v){ m_seatbelt = v;  emit seatbeltChanged(); });
    flag("doorOpen",  m_doorOpen,  [this](bool v){ m_doorOpen = v;  emit doorOpenChanged(); });
    flag("hoodOpen",  m_hoodOpen,  [this](bool v){ m_hoodOpen = v;  emit hoodOpenChanged(); });
    flag("trunkOpen", m_trunkOpen, [this](bool v){ m_trunkOpen = v; emit trunkOpenChanged(); });

    // --- Лампы неисправностей (0x601) ---
    flag("checkEngine",   m_checkEngine,   [this](bool v){ m_checkEngine = v;   emit checkEngineChanged(); });
    flag("oilPressure",   m_oilPressure,   [this](bool v){ m_oilPressure = v;   emit oilPressureChanged(); });
    flag("overheat",      m_overheat,      [this](bool v){ m_overheat = v;      emit overheatChanged(); });
    flag("absFault",      m_absFault,      [this](bool v){ m_absFault = v;      emit absFaultChanged(); });
    flag("espFault",      m_espFault,      [this](bool v){ m_espFault = v;      emit espFaultChanged(); });
    flag("espBlink",      m_espBlink,      [this](bool v){ m_espBlink = v;      emit espBlinkChanged(); });
    flag("espOff",        m_espOff,        [this](bool v){ m_espOff = v;        emit espOffChanged(); });
    flag("brakeFault",    m_brakeFault,    [this](bool v){ m_brakeFault = v;    emit brakeFaultChanged(); });
    flag("steeringFault", m_steeringFault, [this](bool v){ m_steeringFault = v; emit steeringFaultChanged(); });
    flag("airbagFault",   m_airbagFault,   [this](bool v){ m_airbagFault = v;   emit airbagFaultChanged(); });
    flag("battery",       m_battery,       [this](bool v){ m_battery = v;       emit batteryChanged(); });
    flag("parkBrake",     m_parkBrake,     [this](bool v){ m_parkBrake = v;     emit parkBrakeChanged(); });
    flag("pressBrake",    m_pressBrake,    [this](bool v){ m_pressBrake = v;    emit pressBrakeChanged(); });
    flag("fuelLow",       m_fuelLow,       [this](bool v){ m_fuelLow = v;       emit fuelLowChanged(); });
}

// --- Сеттеры аналоговых ---
void VehicleDataReceiver::setSpeed(int v)
{
    if (m_speed == v) return;
    m_speed = v;
    emit speedChanged();
}

void VehicleDataReceiver::setRpm(int v)
{
    if (m_rpm == v) return;
    m_rpm = v;
    emit rpmChanged();
}

void VehicleDataReceiver::setCoolant(int v)
{
    if (m_coolant == v) return;
    m_coolant = v;
    emit coolantChanged();
}

void VehicleDataReceiver::setExternalTemp(int v)
{
    if (m_externalTemp == v) return;
    m_externalTemp = v;
    emit externalTempChanged();
}

void VehicleDataReceiver::setOdometer(int v)
{
    if (m_odometer == v) return;
    m_odometer = v;
    emit odometerChanged();
}

void VehicleDataReceiver::setFuelLevel(int v)
{
    if (m_fuelLevel == v) return;
    m_fuelLevel = v;
    emit fuelLevelChanged();
}

void VehicleDataReceiver::setGear(int v)
{
    if (m_gear == v) return;
    m_gear = v;
    emit gearChanged();
}

void VehicleDataReceiver::setTrip(int v)
{
    if (m_trip == v) return;
    m_trip = v;
    emit tripChanged();
}

void VehicleDataReceiver::setHours(int v)
{
    if (m_hours == v) return;
    m_hours = v;
    emit hoursChanged();
}

void VehicleDataReceiver::setMinutes(int v)
{
    if (m_minutes == v) return;
    m_minutes = v;
    emit minutesChanged();
}

void VehicleDataReceiver::setConnected(bool v)
{
    if (m_connected == v) return;
    m_connected = v;
    qInfo() << "VehicleDataReceiver: connected =" << v;
    emit connectedChanged();
}
