#include "VehicleDataReceiver.h"
#include <QDebug>
#include <QJsonDocument>
#include <QJsonObject>
#include <QNetworkRequest>
#include <QUrl>

namespace {
// Адрес ESP32 в режиме SoftAP
const QString kEspUrl = QStringLiteral("http://192.168.4.1/data");
constexpr int kPollIntervalMs = 100;   // опрашивать 10 раз в секунду

// Значения-заглушки «нет данных» из CAN-матрицы. Если ESP прислал их —
// сигнал невалиден, значение не обновляем (оставляем последнее валидное).
constexpr int kNoDataU16 = 65535;
constexpr int kNoDataU8  = 255;
}

VehicleDataReceiver::VehicleDataReceiver(QObject *parent)
    : QObject(parent)
{
    connect(&m_network, &QNetworkAccessManager::finished,
            this, &VehicleDataReceiver::onReplyFinished);

    connect(&m_pollTimer, &QTimer::timeout,
            this, &VehicleDataReceiver::requestData);

    m_pollTimer.start(kPollIntervalMs);

    qInfo() << "VehicleDataReceiver: polling" << kEspUrl
            << "every" << kPollIntervalMs << "ms";
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
    if (obj.contains("cruise")) {
        setCruiseSpeed(obj.value("cruise").toInt());
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
    flag("espActive",     m_espActive,     [this](bool v){ m_espActive = v;     emit espActiveChanged(); });
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

void VehicleDataReceiver::setCruiseSpeed(int v)
{
    if (m_cruiseSpeed == v) return;
    m_cruiseSpeed = v;
    emit cruiseSpeedChanged();
}

void VehicleDataReceiver::setConnected(bool v)
{
    if (m_connected == v) return;
    m_connected = v;
    qInfo() << "VehicleDataReceiver: connected =" << v;
    emit connectedChanged();
}
