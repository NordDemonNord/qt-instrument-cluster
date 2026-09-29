cmake_minimum_required(VERSION 3.16)

project(DashBoard VERSION 0.1 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Quick Svg Core5Compat Network)

qt_standard_project_setup(REQUIRES 6.8)

file(GLOB DASHBOARD_ICONS CONFIGURE_DEPENDS
    RELATIVE "${CMAKE_CURRENT_SOURCE_DIR}"
    assets/icons/*.svg
)

qt_add_executable(appDashBoard
    main.cpp
    VehicleDataReceiver.cpp
    VehicleDataReceiver.h
)

qt_add_qml_module(appDashBoard
    URI DashBoard
    QML_FILES
        Main.qml
        Speedometer.qml
        Needle.qml
        ProgressArc.qml
        BarGauge.qml
        ScaleGaugeLabel.qml
        PanelUnitLabel.qml
        MileageReadout.qml
        TellTaleIndicator.qml
    RESOURCES
        assets/panel.svg
        assets/panel_scale_labels.svg
        assets/needle.svg
        assets/needle_tach.svg
        assets/fonts/D-DIN.ttf
        assets/fonts/D-DIN-Bold.ttf
        assets/fonts/D-DINExp.ttf
        assets/fonts/Oxanium.ttf
        ${DASHBOARD_ICONS}
    )

# Qt for iOS sets MACOSX_BUNDLE_GUI_IDENTIFIER automatically since Qt 6.1.
# If you are developing for iOS or macOS you should consider setting an
# explicit, fixed bundle identifier manually though.
set_target_properties(appDashBoard PROPERTIES
#    MACOSX_BUNDLE_GUI_IDENTIFIER com.example.appDashBoard
    MACOSX_BUNDLE_BUNDLE_VERSION ${PROJECT_VERSION}
    MACOSX_BUNDLE_SHORT_VERSION_STRING ${PROJECT_VERSION_MAJOR}.${PROJECT_VERSION_MINOR}
    MACOSX_BUNDLE TRUE
    WIN32_EXECUTABLE TRUE
    QT_ANDROID_PACKAGE_SOURCE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/android"
)

target_link_libraries(appDashBoard
    PRIVATE Qt6::Quick Qt6::Svg Qt6::Core5Compat Qt6::Network
)

include(GNUInstallDirs)
install(TARGETS appDashBoard
    BUNDLE DESTINATION .
    LIBRARY DESTINATION ${CMAKE_INSTALL_BINDIR}
    RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR}
)
