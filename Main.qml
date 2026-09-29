import QtQuick

Window {
    width: 1920
    height: 1080
    visibility: Window.FullScreen
    visible: true
    title: qsTr("Lada Vesta NG — приборная панель")
    color: "#0a0c10"

    // Oxanium — шрифт цифр скорости и передачи.
    FontLoader { id: oxanium; source: "assets/fonts/Oxanium.ttf" }

    // Поле приборки. Внутри всё размечено в координатах panel.svg
    // (1418×1028), но сам рисунок занимает только часть холста.
    // Масштабируем так, чтобы в окно вписалась именно видимая часть
    // (crop), а не весь холст с пустыми полями. Масштаб одинаковый по
    // обеим осям, поэтому круги шкал остаются кругами.
    Item {
            id: cluster

            // Видимая часть panel.svg в координатах SVG:
            // bounding box рисунка (323..1101 × 301..590) плюс поля 10 px.
            readonly property real cropX: 313
            readonly property real cropY: 291
            readonly property real cropW: 798
            readonly property real cropH: 309

            // Во сколько раз увеличить SVG, чтобы crop целиком влез в окно.
            readonly property real fitScale: Math.min(parent.width / cropW,
                                                      parent.height / cropH)

            // Весь холст SVG в этом масштабе...
            width: 1418 * fitScale
            height: 1028 * fitScale
            // ...сдвинутый так, чтобы crop оказался по центру окна.
            // Пустые поля холста уходят за края окна.
            x: (parent.width  - cropW * fitScale) / 2 - cropX * fitScale
            y: (parent.height - cropH * fitScale) / 2 - cropY * fitScale

        // Центры чёрных хабов (path188-3 / ellipse191 в panel.svg).
        readonly property real hubCenterYSvg: 447.21094
        readonly property real speedoHubXSvg: 939.97607
        readonly property real tachHubXSvg: 481.32196

        // Статичная приборка (иконки, деления, рамки; без цифр над шкалами — они в QML).
        Image {
            id: screen
            z: 0
            anchors.fill: parent
            source: "assets/panel.svg"
            sourceSize: Qt.size(width, height)
            fillMode: Image.PreserveAspectFit
            smooth: true
            layer.enabled: true
            layer.smooth: true
        }

        // Интерактивные шкалы — между panel.svg и цифрами.
        BarGauge {
            id: coolantGauge
            z: 1
            anchors.fill: parent
            panelWidth: cluster.width
            panelHeight: cluster.height
            barLeftSvg: 417.04
            barRightSvg: 540.08
            barCenterYSvg: 548.5
            barHeightSvg: 6
            segmentCount: 8
            segmentGapSvg: 1
            warningBorderAtEnd: 1.5
            warningBorderColor: cluster.gaugeDangerColor
            // Шкала ОЖ размечена 50…130 °C — нормируем температуру в 0…1.
            value: Math.max(0, Math.min(1, (VehicleData.coolant - 50) / (130 - 50)))
        }

        BarGauge {
            id: fuelGauge
            z: 1
            anchors.fill: parent
            panelWidth: cluster.width
            panelHeight: cluster.height
            barLeftSvg: 880.42
            barRightSvg: 1003.70
            barCenterYSvg: 548.5
            barHeightSvg: 6
            segmentCount: 8
            segmentGapSvg: 1
            warningBorderAtStart: 1.5
            warningBorderColor: cluster.gaugeDangerColor
            // Уровень топлива 0…100 % → 0…1.
            value: Math.max(0, Math.min(1, VehicleData.fuelLevel / 100))
        }

        readonly property real tellTaleCenterYSvg: 569.8435
        readonly property real tellTaleIconSizeSvg: 24

        // Индикаторы №1–4, 6–8, 10 — иконки в panel.svg, подписи в QML.
        // Индикаторы №13–16, 18, 20 — в panel.svg (размещение в Inkscape).

        // Индикаторы №24–30: цвет по ISO / ECE (пока все включены, без мигания).
        // centerYOffsetSvg — поправка оптического центра пиктограммы в viewBox.
        TellTaleIndicator {
            z: 3
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: 826.94163
            centerYSvg: cluster.tellTaleCenterYSvg
            centerYOffsetSvg: 2.5
            iconSource: "assets/icons/hood_open.svg"
            iconSizeSvg: cluster.tellTaleIconSizeSvg
            active: VehicleData.hoodOpen
            color: "#f5b800"
        }
        TellTaleIndicator {
            z: 3
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: 856.76822
            centerYSvg: cluster.tellTaleCenterYSvg
            centerYOffsetSvg: 1.0
            iconSource: "assets/icons/door_open.svg"
            iconSizeSvg: cluster.tellTaleIconSizeSvg
            active: VehicleData.doorOpen
            color: "#f5b800"
        }
        TellTaleIndicator {
            z: 3
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: 888.5948
            centerYSvg: cluster.tellTaleCenterYSvg
            centerYOffsetSvg: 2.5
            iconSource: "assets/icons/trunk_open.svg"
            iconSizeSvg: cluster.tellTaleIconSizeSvg
            active: VehicleData.trunkOpen
            color: "#f5b800"
        }
        TellTaleIndicator {
            z: 3
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: 915.35782
            centerYSvg: cluster.tellTaleCenterYSvg
            centerYOffsetSvg: 1.5
            iconSource: "assets/icons/seatbelt.svg"
            iconSizeSvg: cluster.tellTaleIconSizeSvg
            active: VehicleData.seatbelt
            color: "#e31e24"
        }
        TellTaleIndicator {
            z: 3
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: 942.96475
            centerYSvg: cluster.tellTaleCenterYSvg
            centerYOffsetSvg: 0.5
            iconSource: "assets/icons/esc_off.svg"
            iconSizeSvg: cluster.tellTaleIconSizeSvg
            active: VehicleData.espOff
            color: "#f5b800"
        }
        TellTaleIndicator {
            z: 3
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: 970.57168
            centerYSvg: cluster.tellTaleCenterYSvg
            centerYOffsetSvg: 1.5
            iconSource: "assets/icons/esp.svg"
            iconSizeSvg: cluster.tellTaleIconSizeSvg
            active: VehicleData.espActive
            blinking: true
            color: "#f5b800"
        }
        TellTaleIndicator {
            z: 3
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: 999.4445
            centerYSvg: cluster.tellTaleCenterYSvg
            centerYOffsetSvg: 0
            iconSource: "assets/icons/battery.svg"
            iconSizeSvg: cluster.tellTaleIconSizeSvg
            active: VehicleData.battery
            color: "#e31e24"
        }

        // === Управляемые лампы (координаты и цвета 1:1 из panel.svg) ===
        // #1 ГУР
        TellTaleIndicator {
            z: 5
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: 631.201
            centerYSvg: 383.519
            iconSource: "assets/icons/power_steering.svg"
            iconSizeSvg: 10.931
            iconAspect: 1.2752
            colorize: true
            active: VehicleData.steeringFault
            color: "#e31e24"
        }
        // #2 тормоза
        TellTaleIndicator {
            z: 5
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: 630.956
            centerYSvg: 400.614
            iconSource: "assets/icons/brake_system.svg"
            iconSizeSvg: 10.22
            iconAspect: 1.272
            colorize: true
            active: VehicleData.brakeFault
            color: "#e31e24"
        }
        // #3 ABS
        TellTaleIndicator {
            z: 5
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: 631.016
            centerYSvg: 417.934
            iconSource: "assets/icons/abs.svg"
            iconSizeSvg: 10.195
            iconAspect: 1.2752
            colorize: true
            active: VehicleData.absFault
            color: "#f5b800"
        }
        // #4 стоян.торм
        TellTaleIndicator {
            z: 5
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: 631.000
            centerYSvg: 435.395
            iconSource: "assets/icons/parking_brake.svg"
            iconSizeSvg: 13.5
            iconAspect: 1.0
            colorize: true
            active: VehicleData.parkBrake
            color: "#e31e24"
        }
        // #6 подушки
        TellTaleIndicator {
            z: 5
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: 631.000
            centerYSvg: 452.716
            iconSource: "assets/icons/airbag.svg"
            iconSizeSvg: 10.4
            iconAspect: 1.25
            colorize: true
            active: VehicleData.airbagFault
            color: "#e31e24"
        }
        // #7 check engine
        TellTaleIndicator {
            z: 5
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: 631.000
            centerYSvg: 469.755
            iconSource: "assets/icons/check_engine.svg"
            iconSizeSvg: 8.666
            iconAspect: 1.5001
            colorize: true
            active: VehicleData.checkEngine
            color: "#f5b800"
        }
        // #8 перегрев
        TellTaleIndicator {
            z: 5
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: 631.000
            centerYSvg: 487.919
            iconSource: "assets/icons/coolant_temp.svg"
            iconSizeSvg: 13.0
            iconAspect: 1.0
            colorize: true
            active: VehicleData.overheat
            color: "#e31e24"
        }
        // #10 мало топлива
        TellTaleIndicator {
            z: 5
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: 631.000
            centerYSvg: 504.958
            iconSource: "assets/icons/fuel_low.svg"
            iconSizeSvg: 10.4
            iconAspect: 1.25
            colorize: true
            active: VehicleData.fuelLow
            color: "#f5b800"
        }
        // #40 габариты
        TellTaleIndicator {
            z: 5
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: 418.555
            centerYSvg: 569.844
            iconSource: "assets/icons/side_lamps.svg"
            iconSizeSvg: 19.2
            iconAspect: 1.25
            colorize: true
            active: VehicleData.position
            color: "#00a000"
        }
        // #39 ближний
        TellTaleIndicator {
            z: 5
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: 447.428
            centerYSvg: 569.843
            iconSource: "assets/icons/low_beam.svg"
            iconSizeSvg: 24.0
            iconAspect: 1.0
            colorize: true
            active: VehicleData.lowBeam
            color: "#00a000"
        }
        // #38 дальний
        TellTaleIndicator {
            z: 5
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: 475.035
            centerYSvg: 569.843
            iconSource: "assets/icons/high_beam.svg"
            iconSizeSvg: 24.0
            iconAspect: 1.0
            colorize: true
            active: VehicleData.highBeam
            color: "#0099ff"
        }
        // #37 перед.ПТФ
        TellTaleIndicator {
            z: 5
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: 502.642
            centerYSvg: 569.844
            iconSource: "assets/icons/fog_front.svg"
            iconSizeSvg: 19.2
            iconAspect: 1.25
            colorize: true
            active: VehicleData.frontFog
            color: "#00a000"
        }
        // #36 задн.ПТФ
        TellTaleIndicator {
            z: 5
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: 529.405
            centerYSvg: 569.843
            iconSource: "assets/icons/fog_rear.svg"
            iconSizeSvg: 24.0
            iconAspect: 1.0
            colorize: true
            active: VehicleData.rearFog
            color: "#f5b800"
        }
        // #35 педаль торм
        TellTaleIndicator {
            z: 5
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: 561.232
            centerYSvg: 569.844
            iconSource: "assets/icons/auto_hold.svg"
            iconSizeSvg: 19.2
            iconAspect: 1.25
            colorize: true
            active: VehicleData.pressBrake
            color: "#00a000"
        }
        // #34 давл.масла
        TellTaleIndicator {
            z: 5
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: 591.058
            centerYSvg: 571.844
            iconSource: "assets/icons/oil_pressure.svg"
            iconSizeSvg: 19.2
            iconAspect: 1.25
            colorize: true
            active: VehicleData.oilPressure
            color: "#e31e24"
        }

        readonly property real gaugeLabelYSvg: 538.5
        readonly property real gaugeLabelFontSvg: 11
        readonly property color gaugeDangerColor: "#ff0000"
        readonly property real unitLabelFontSvg: 10
        readonly property real readoutFontSvg: unitLabelFontSvg + 3
        readonly property real readoutUnitGapSvg: 1

        // №33 трип и №31 одометр — число в 1 px слева от «km», один Y и размер шрифта.
        readonly property real tripKmCenterXSvg: 680.587
        readonly property real odometerKmCenterXSvg: 791.356
        readonly property real mileageLabelYSvg: 578.031

        // Индикаторы №13, 15–16, 18, 20 — в panel.svg над path131.
        // №14 время — в QML (как №19 температура).

        // Верхний ряд: 13 поворот | 14 время | 15 авто | 16 нав | 18 медиа | 19 °C | 20 поворот
        // Центры поворотников — из panel.svg; остальное по формуле embed_indicators_13_20.py
        readonly property real turnLeftCenterXSvg: 577.695
        readonly property real turnRightCenterXSvg: 843.454
        readonly property real topRowTurnCenterYSvg: 320.686
        readonly property real topRowTurnIconSizeSvg: 20
        readonly property real topRowIconNavOffsetSvg: 40
        readonly property real topRowNavCenterXSvg: (turnLeftCenterXSvg + turnRightCenterXSvg) / 2
        readonly property real topRowCarCenterXSvg: topRowNavCenterXSvg - topRowIconNavOffsetSvg
        readonly property real topRowMediaCenterXSvg: topRowNavCenterXSvg + topRowIconNavOffsetSvg

        readonly property real outdoorTempCenterYSvg: 322.874
        readonly property real clockTimeCenterXSvg: (turnLeftCenterXSvg + topRowCarCenterXSvg) / 2
        readonly property real outdoorTempCenterXSvg: (topRowMediaCenterXSvg + turnRightCenterXSvg) / 2
        readonly property real clockTimeCenterYSvg: outdoorTempCenterYSvg

        // №1–4, 6–8, 10 — иконки в panel.svg; подписи справа (Oxanium).
        readonly property real warningStripLabelXSvg: 643
        readonly property color warningStripLabelColor: "#808080"
        readonly property real warningStripLabelFontSvg: 10.5
        readonly property color warningRedColor: "#e31e24"
        readonly property color warningAmberColor: "#f5b800"
        readonly property var warningStripLabels: [
            { centerYSvg: 384.5, text: "Неисправность усилителя руля" },
            { centerYSvg: 400.65, text: "Неисправность тормозной системы" },
            { centerYSvg: 417.95, text: "Неисправность системы ABS" },
            { centerYSvg: 435.40, text: "Включён стояночный тормоз" },
            { centerYSvg: 452.72, text: "Неисправность подушек" },
            { centerYSvg: 469.75, text: "Неисправность двигателя" },
            { centerYSvg: 486.23, text: "Перегрев охлаждающей жидкости" },
            { centerYSvg: 504.96, text: "Низкий уровень топлива в баке" }
        ]

        // №20 правый поворотник
        TellTaleIndicator {
            z: 10
                panelWidth: cluster.width
                panelHeight: cluster.height
                centerXSvg: cluster.turnRightCenterXSvg
                centerYSvg: cluster.topRowTurnCenterYSvg
                iconSource: "assets/icons/turn_right.svg"
                iconSizeSvg: cluster.topRowTurnIconSizeSvg
                colorize: false
                active: VehicleData.turnRight
                blinking: true
                blinkIntervalMs: 500
                color: "#00a000"
            }

        // №13 левый поворотник
        TellTaleIndicator {
            z: 10
            panelWidth: cluster.width
            panelHeight: cluster.height
            centerXSvg: cluster.turnLeftCenterXSvg
            centerYSvg: cluster.topRowTurnCenterYSvg
            iconSource: "assets/icons/turn_left.svg"
            iconSizeSvg: cluster.topRowTurnIconSizeSvg
            colorize: false
            active: VehicleData.turnLeft
            blinking: true
            blinkIntervalMs: 500
            color: "#00a000"
        }

        property real totalOdometerKm: 23409
        property string tripCounter: "A"
        property real tripOdometerKm: 234.0
        property real outdoorTempC: 8
        property string clockTimeText: "18:00"

        // Подписи над шкалами ОЖ (50 / 90 / 130) и топлива (0 / 1/2 / 1).
        ScaleGaugeLabel {
            z: 2
            panelWidth: cluster.width
            panelHeight: cluster.height
            fontFamily: oxanium.name
            anchorXSvg: coolantGauge.barLeftSvg
            horizontalAnchor: "left"
            centerYSvg: cluster.gaugeLabelYSvg
            fontSizeSvg: cluster.gaugeLabelFontSvg
            text: "50"
        }
        ScaleGaugeLabel {
            z: 2
            panelWidth: cluster.width
            panelHeight: cluster.height
            fontFamily: oxanium.name
            anchorXSvg: (coolantGauge.barLeftSvg + coolantGauge.barRightSvg) / 2
            horizontalAnchor: "center"
            centerYSvg: cluster.gaugeLabelYSvg
            fontSizeSvg: cluster.gaugeLabelFontSvg
            text: "90"
        }
        ScaleGaugeLabel {
            z: 2
            panelWidth: cluster.width
            panelHeight: cluster.height
            fontFamily: oxanium.name
            anchorXSvg: 532
            horizontalAnchor: "center"
            centerYSvg: cluster.gaugeLabelYSvg
            fontSizeSvg: cluster.gaugeLabelFontSvg
            textColor: cluster.gaugeDangerColor
            text: "130"
        }
        ScaleGaugeLabel {
            z: 2
            panelWidth: cluster.width
            panelHeight: cluster.height
            fontFamily: oxanium.name
            anchorXSvg: fuelGauge.barLeftSvg
            horizontalAnchor: "left"
            centerYSvg: cluster.gaugeLabelYSvg
            fontSizeSvg: cluster.gaugeLabelFontSvg
            textColor: cluster.gaugeDangerColor
            text: "0"
        }
        ScaleGaugeLabel {
            z: 2
            panelWidth: cluster.width
            panelHeight: cluster.height
            fontFamily: oxanium.name
            anchorXSvg: (fuelGauge.barLeftSvg + fuelGauge.barRightSvg) / 2
            horizontalAnchor: "center"
            centerYSvg: cluster.gaugeLabelYSvg
            fontSizeSvg: cluster.gaugeLabelFontSvg
            text: "1/2"
        }
        ScaleGaugeLabel {
            z: 2
            panelWidth: cluster.width
            panelHeight: cluster.height
            fontFamily: oxanium.name
            anchorXSvg: 1002
            horizontalAnchor: "center"
            centerYSvg: cluster.gaugeLabelYSvg
            fontSizeSvg: cluster.gaugeLabelFontSvg
            text: "1"
        }

        // Подписи единиц (km/h, km, °C, x1000 rpm) — Oxanium, координаты из panel.svg.
        PanelUnitLabel {
            z: 2
            panelWidth: cluster.width
            panelHeight: cluster.height
            fontFamily: oxanium.name
            centerXSvg: 850.747
            centerYSvg: 513.177
            fontSizeSvg: cluster.unitLabelFontSvg
            rotationDeg: -26.64
            text: "km/h"
        }
        PanelUnitLabel {
            z: 2
            panelWidth: cluster.width
            panelHeight: cluster.height
            fontFamily: oxanium.name
            centerXSvg: 939.229
            centerYSvg: 466.462
            fontSizeSvg: cluster.unitLabelFontSvg
            text: "km/h"
        }
        MileageReadout {
            z: 2
            panelWidth: cluster.width
            panelHeight: cluster.height
            fontFamily: oxanium.name
            centerXSvg: cluster.odometerKmCenterXSvg
            centerYSvg: cluster.mileageLabelYSvg
            fontSizeSvg: cluster.readoutFontSvg
            gapSvg: cluster.readoutUnitGapSvg
            valueText: VehicleData.odometer.toString()
        }
        MileageReadout {
            z: 2
            panelWidth: cluster.width
            panelHeight: cluster.height
            fontFamily: oxanium.name
            centerXSvg: cluster.tripKmCenterXSvg
            centerYSvg: cluster.mileageLabelYSvg
            fontSizeSvg: cluster.readoutFontSvg
            gapSvg: cluster.readoutUnitGapSvg
            valueText: cluster.tripCounter + " " + cluster.tripOdometerKm.toFixed(1)
        }
        MileageReadout {
            z: 2
            panelWidth: cluster.width
            panelHeight: cluster.height
            fontFamily: oxanium.name
            centerXSvg: cluster.outdoorTempCenterXSvg
            centerYSvg: cluster.outdoorTempCenterYSvg
            fontSizeSvg: cluster.readoutFontSvg
            gapSvg: cluster.readoutUnitGapSvg
            unitText: "°C"
            valueText: VehicleData.externalTemp.toString()
        }
        ScaleGaugeLabel {
            z: 2
            panelWidth: cluster.width
            panelHeight: cluster.height
            fontFamily: oxanium.name
            anchorXSvg: cluster.clockTimeCenterXSvg
            centerYSvg: cluster.clockTimeCenterYSvg
            fontSizeSvg: cluster.readoutFontSvg
            horizontalAnchor: "center"
            text: cluster.clockTimeText
        }

        Repeater {
            model: cluster.warningStripLabels
            delegate: ScaleGaugeLabel {
                required property var modelData
                z: 20
                panelWidth: cluster.width
                panelHeight: cluster.height
                fontFamily: oxanium.name
                anchorXSvg: cluster.warningStripLabelXSvg
                centerYSvg: modelData.centerYSvg
                fontSizeSvg: cluster.warningStripLabelFontSvg
                fontWeight: Font.Normal
                horizontalAnchor: "left"
                textColor: cluster.warningStripLabelColor
                text: modelData.text
            }
        }

        PanelUnitLabel {
            z: 2
            panelWidth: cluster.width
            panelHeight: cluster.height
            fontFamily: oxanium.name
            centerXSvg: 401.848
            centerYSvg: 508.138
            fontSizeSvg: cluster.unitLabelFontSvg
            rotationDeg: -26.92
            text: "x1000 rpm"
        }

        // Заливка-фон и подсветка у стрелок (под стрелками).
        ProgressArc {
            id: speedoArc
            anchors.fill: parent
            panelScale: cluster.width / 1418
            centerXSvg: 939.97607
            centerYSvg: cluster.hubCenterYSvg
            innerRadiusSvg: 66
            outerRadiusSvg: 100
            startAngle: 150
            sweepAngle: 240
            rotationDeg: speedoNeedle.rotationDeg
            dialZeroAngle: speedoNeedle.dialZeroAngle
        }

        ProgressArc {
            id: tachArc
            anchors.fill: parent
            panelScale: cluster.width / 1418
            centerXSvg: 481.32196
            centerYSvg: cluster.hubCenterYSvg
            innerRadiusSvg: 66
            outerRadiusSvg: 100
            startAngle: 150
            sweepAngle: 240
            rotationDeg: tachNeedle.rotationDeg
            dialZeroAngle: tachNeedle.dialZeroAngle
        }

        // Стрелка спидометра. Ось вращения = центр path188-3.
        Needle {
            id: speedoNeedle
            anchors.fill: parent
            source: "assets/needle.svg"
            pivotX: parent.width * (939.97607 / 1418)
            pivotY: parent.height * (cluster.hubCenterYSvg / 1028)
            dialZeroAngle: 149.48
            minValue: 0
            maxValue: 220
            sweepAngle: 240
            value: VehicleData.speed          // ← реальные данные с CAN

            // Плавное движение стрелки (сглаживание рывков)
            Behavior on value {
                NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
            }
        }

        // Стрелка тахометра. Ось вращения = центр ellipse191.
        Needle {
            id: tachNeedle
            anchors.fill: parent
            source: "assets/needle_tach.svg"
            pivotX: parent.width * (481.32196 / 1418)
            pivotY: parent.height * (cluster.hubCenterYSvg / 1028)
            dialZeroAngle: 148.89
            minValue: 0
            maxValue: 7
            sweepAngle: 240
            value: VehicleData.rpm / 1000     // шкала в x1000 rpm

            Behavior on value {
                NumberAnimation { duration: 200; easing.type: Easing.OutCubic }
            }
        }

        // Цифровая скорость — центр = path188-3 (939.976, 447.211).
        Item {
            id: speedoHub
            width: 0
            height: 0
            x: cluster.width * (cluster.speedoHubXSvg / 1418)
            y: cluster.height * (cluster.hubCenterYSvg / 1028)

            Text {
                id: speedReadout
                anchors.centerIn: parent
                text: VehicleData.speed
                color: "#ffffff"
                font.family: oxanium.name
                font.weight: Font.ExtraLight
                font.pixelSize: cluster.width * 0.03
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                transform: Scale {
                    origin.x: speedReadout.width / 2
                    origin.y: speedReadout.height / 2
                    xScale: 1.35
                    yScale: 1.0
                }
            }
        }

        // Индикатор передачи — центр = ellipse191 (481.322, 447.211).
        Item {
            id: tachHub
            width: 0
            height: 0
            x: cluster.width * (cluster.tachHubXSvg / 1418)
            y: cluster.height * (cluster.hubCenterYSvg / 1028)

            Text {
                id: gearReadout
                readonly property var gearLetters: ["P", "R", "N", "D", "M"]
                property string gear: gearLetters[VehicleData.gear] !== undefined
                                      ? gearLetters[VehicleData.gear] : "P"
                anchors.centerIn: parent
                text: gear
                color: "#ffffff"
                font.family: oxanium.name
                font.weight: Font.ExtraLight
                font.pixelSize: cluster.width * 0.03
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
                transform: Scale {
                    origin.x: gearReadout.width / 2
                    origin.y: gearReadout.height / 2
                    xScale: 1.35
                    yScale: 1.0
                }
            }
        }
    }

    // Статус источника данных (ESP32 по HTTP или DEMO)
        Text {
            z: 100
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.margins: 10
            color: VehicleData.connected ? "#60d060" : "#e04040"
            font.pixelSize: 14
            text: VehicleData.sourceName
                  + (VehicleData.connected ? ": связь есть" : ": нет связи")
                  + "  ·  скорость: " + VehicleData.speed + " км/ч"
        }
}
