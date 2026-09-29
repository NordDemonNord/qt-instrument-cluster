#ifndef VEHICLEDATARECEIVER_H
#define VEHICLEDATARECEIVER_H

#include <QElapsedTimer>
#include <QObject>
#include <QNetworkAccessManager>
#include <QNetworkReply>
#include <QString>
#include <QTimer>

// Приёмник данных приборки. Отдаёт сигналы CAN-матрицы Lada Vesta NG
// в QML как свойства объекта VehicleData.
//
// Источник данных выбирается переменной окружения VEHICLE_DATA_SOURCE:
//   http (или не задана) - опрос ESP32 по HTTP (/data), плоский JSON;
//   demo                 - синтетические данные: стрелки ходят по шкалам,
//                          сигнализаторы мигают. Для проверки отрисовки
//                          без реального автомобиля.
class VehicleDataReceiver : public QObject
{
    Q_OBJECT

    // --- Аналоговые значения ---
    Q_PROPERTY(int speed        READ speed        NOTIFY speedChanged)
    Q_PROPERTY(int rpm          READ rpm          NOTIFY rpmChanged)
    Q_PROPERTY(int coolant      READ coolant      NOTIFY coolantChanged)
    Q_PROPERTY(int externalTemp READ externalTemp NOTIFY externalTempChanged)
    Q_PROPERTY(int odometer     READ odometer     NOTIFY odometerChanged)
    Q_PROPERTY(int fuelLevel    READ fuelLevel    NOTIFY fuelLevelChanged)
    Q_PROPERTY(int gear         READ gear         NOTIFY gearChanged)
    Q_PROPERTY(int trip         READ trip         NOTIFY tripChanged)
    Q_PROPERTY(int hours        READ hours        NOTIFY hoursChanged)
    Q_PROPERTY(int minutes      READ minutes      NOTIFY minutesChanged)

    // --- Сигнализаторы кузова и света (0x600) ---
    Q_PROPERTY(bool turnLeft    READ turnLeft    NOTIFY turnLeftChanged)
    Q_PROPERTY(bool turnRight   READ turnRight   NOTIFY turnRightChanged)
    Q_PROPERTY(bool highBeam    READ highBeam    NOTIFY highBeamChanged)
    Q_PROPERTY(bool lowBeam     READ lowBeam     NOTIFY lowBeamChanged)
    Q_PROPERTY(bool position    READ position    NOTIFY positionChanged)
    Q_PROPERTY(bool frontFog    READ frontFog    NOTIFY frontFogChanged)
    Q_PROPERTY(bool rearFog     READ rearFog     NOTIFY rearFogChanged)
    Q_PROPERTY(bool seatbelt    READ seatbelt    NOTIFY seatbeltChanged)
    Q_PROPERTY(bool doorOpen    READ doorOpen    NOTIFY doorOpenChanged)
    Q_PROPERTY(bool hoodOpen    READ hoodOpen    NOTIFY hoodOpenChanged)
    Q_PROPERTY(bool trunkOpen   READ trunkOpen   NOTIFY trunkOpenChanged)

    // --- Лампы неисправностей (0x601) ---
    Q_PROPERTY(bool checkEngine READ checkEngine NOTIFY checkEngineChanged)
    Q_PROPERTY(bool oilPressure READ oilPressure NOTIFY oilPressureChanged)
    Q_PROPERTY(bool overheat    READ overheat    NOTIFY overheatChanged)
    Q_PROPERTY(bool absFault    READ absFault    NOTIFY absFaultChanged)
    Q_PROPERTY(bool espFault    READ espFault    NOTIFY espFaultChanged)
    Q_PROPERTY(bool espBlink    READ espBlink    NOTIFY espBlinkChanged)
    Q_PROPERTY(bool espOff      READ espOff      NOTIFY espOffChanged)
    Q_PROPERTY(bool brakeFault  READ brakeFault  NOTIFY brakeFaultChanged)
    Q_PROPERTY(bool steeringFault READ steeringFault NOTIFY steeringFaultChanged)
    Q_PROPERTY(bool airbagFault  READ airbagFault  NOTIFY airbagFaultChanged)
    Q_PROPERTY(bool battery      READ battery      NOTIFY batteryChanged)
    Q_PROPERTY(bool parkBrake    READ parkBrake    NOTIFY parkBrakeChanged)
    Q_PROPERTY(bool pressBrake   READ pressBrake   NOTIFY pressBrakeChanged)
    Q_PROPERTY(bool fuelLow      READ fuelLow      NOTIFY fuelLowChanged)

    // --- Связь ---
    Q_PROPERTY(bool connected   READ connected   NOTIFY connectedChanged)
    // Имя активного источника для строки статуса: "ESP32" или "DEMO".
    Q_PROPERTY(QString sourceName READ sourceName CONSTANT)

public:
    explicit VehicleDataReceiver(QObject *parent = nullptr);

    int speed()        const { return m_speed; }
    int rpm()          const { return m_rpm; }
    int coolant()      const { return m_coolant; }
    int externalTemp() const { return m_externalTemp; }
    int odometer()     const { return m_odometer; }
    int fuelLevel()    const { return m_fuelLevel; }
    int gear()         const { return m_gear; }
    int trip()    const { return m_trip; }      // в десятых км
    int hours()   const { return m_hours; }
    int minutes() const { return m_minutes; }

    bool turnLeft()  const { return m_turnLeft; }
    bool turnRight() const { return m_turnRight; }
    bool highBeam()  const { return m_highBeam; }
    bool lowBeam()   const { return m_lowBeam; }
    bool position()  const { return m_position; }
    bool frontFog()  const { return m_frontFog; }
    bool rearFog()   const { return m_rearFog; }
    bool seatbelt()  const { return m_seatbelt; }
    bool doorOpen()  const { return m_doorOpen; }
    bool hoodOpen()  const { return m_hoodOpen; }
    bool trunkOpen() const { return m_trunkOpen; }

    bool checkEngine()   const { return m_checkEngine; }
    bool oilPressure()   const { return m_oilPressure; }
    bool overheat()      const { return m_overheat; }
    bool absFault()      const { return m_absFault; }
    bool espFault()      const { return m_espFault; }
    bool espBlink()      const { return m_espBlink; }
    bool espOff()        const { return m_espOff; }
    bool brakeFault()    const { return m_brakeFault; }
    bool steeringFault() const { return m_steeringFault; }
    bool airbagFault()   const { return m_airbagFault; }
    bool battery()       const { return m_battery; }
    bool parkBrake()     const { return m_parkBrake; }
    bool pressBrake()    const { return m_pressBrake; }
    bool fuelLow()       const { return m_fuelLow; }

    bool connected() const { return m_connected; }
    QString sourceName() const { return m_sourceName; }

signals:
    void speedChanged();
    void rpmChanged();
    void coolantChanged();
    void externalTempChanged();
    void odometerChanged();
    void fuelLevelChanged();
    void gearChanged();
    void tripChanged();
    void hoursChanged();
    void minutesChanged();

    void turnLeftChanged();
    void turnRightChanged();
    void highBeamChanged();
    void lowBeamChanged();
    void positionChanged();
    void frontFogChanged();
    void rearFogChanged();
    void seatbeltChanged();
    void doorOpenChanged();
    void hoodOpenChanged();
    void trunkOpenChanged();

    void checkEngineChanged();
    void oilPressureChanged();
    void overheatChanged();
    void absFaultChanged();
    void espFaultChanged();
    void espBlinkChanged();
    void espOffChanged();
    void brakeFaultChanged();
    void steeringFaultChanged();
    void airbagFaultChanged();
    void batteryChanged();
    void parkBrakeChanged();
    void pressBrakeChanged();
    void fuelLowChanged();

    void connectedChanged();

private slots:
    // Источник http
    void requestData();
    void onReplyFinished(QNetworkReply *reply);

    // Источник demo
    void updateDemo();

private:
    // Запуск выбранного источника (вызывается из конструктора).
    void startHttpSource();
    void startDemoSource();

    // Общий сеттер для сигнализатора: пишет поле и эмитит его сигнал,
    // только если значение изменилось.
    void setFlag(bool &field, bool value, void (VehicleDataReceiver::*changed)());

    // Включить или выключить все сигнализаторы разом (для demo).
    void setAllTellTales(bool on);

    // Сеттеры для значений (эмитят сигнал только при изменении).
    void setSpeed(int v);
    void setRpm(int v);
    void setCoolant(int v);
    void setExternalTemp(int v);
    void setOdometer(int v);
    void setFuelLevel(int v);
    void setGear(int v);
    void setTrip(int v);
    void setHours(int v);
    void setMinutes(int v);
    void setConnected(bool v);

    QString m_sourceName;

    // Источник http
    QNetworkAccessManager m_network;
    QTimer m_pollTimer;

    // Источник demo
    QTimer m_demoTimer;
    QElapsedTimer m_demoClock;

    // Значения
    int m_speed        = 0;
    int m_rpm          = 0;
    int m_coolant      = 0;
    int m_externalTemp = 0;
    int m_odometer     = 0;
    int m_fuelLevel    = 0;
    int m_gear         = 0;   // 0=P,1=R,2=N,3=D,4=M
    int m_trip    = 0;   // десятые км
    int m_hours   = 0;
    int m_minutes = 0;

    // Сигнализаторы
    bool m_turnLeft  = false;
    bool m_turnRight = false;
    bool m_highBeam  = false;
    bool m_lowBeam   = false;
    bool m_position  = false;
    bool m_frontFog  = false;
    bool m_rearFog   = false;
    bool m_seatbelt  = false;
    bool m_doorOpen  = false;
    bool m_hoodOpen  = false;
    bool m_trunkOpen = false;

    bool m_checkEngine   = false;
    bool m_oilPressure   = false;
    bool m_overheat      = false;
    bool m_absFault      = false;
    bool m_espFault      = false;
    bool m_espBlink      = false;
    bool m_espOff        = false;
    bool m_brakeFault    = false;
    bool m_steeringFault = false;
    bool m_airbagFault   = false;
    bool m_battery       = false;
    bool m_parkBrake     = false;
    bool m_pressBrake    = false;
    bool m_fuelLow       = false;

    bool m_connected = false;
};

#endif // VEHICLEDATARECEIVER_H
