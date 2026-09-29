#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>

#include "VehicleDataReceiver.h"

int main(int argc, char *argv[])
{
    QGuiApplication app(argc, argv);

    QQmlApplicationEngine engine;

    auto *vehicleData = new VehicleDataReceiver(&app);
    engine.rootContext()->setContextProperty(QStringLiteral("VehicleData"), vehicleData);

    QObject::connect(
        &engine,
        &QQmlApplicationEngine::objectCreationFailed,
        &app,
        []() { QCoreApplication::exit(-1); },
        Qt::QueuedConnection);
    engine.loadFromModule("DashBoard", "Main");

    return app.exec();
}
