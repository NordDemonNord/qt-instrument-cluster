import QtQuick

Item {
    id: root

    // --- Параметры шкалы ---
    property real minValue: 0          // начало шкалы, км/ч
    property real maxValue: 220        // конец шкалы, км/ч
    property real startAngle: 138      // угол начала дуги (градусы)
    property real sweepAngle: 264      // на сколько градусов раскрыта дуга

    // --- Параметры разметки делений ---
    // Кол-во делений вдоль шкалы. 11 отрезков 0..220 → 12 рисок по границам
    // (0, 20, ... , 220). Поставь 11, если нужны только 11 делений.
    property int divisionCount: 11
    // Угловой шаг между делениями. 264° дуги / 11 отрезков = 24°.
    property real divisionStep: sweepAngle / 11
    // Угол, под которым исходный ассет стоит относительно центра циферблата
    // (оценка). Подстрой, если первое деление не попадает в начало дуги.
    property real divisionAssetAngle: 158

    // РАЗМЕР самих отрезков (масштаб глифа вокруг его собственного центра).
    // Не меняет радиус. Именно он стыкует отрезки: больше — длиннее отрезок —
    // зазор закрывается; меньше — появляется зазор.
    property real divisionSize: 1.95
    // РАДИУС всей шкалы (масштаб кольца вокруг центра циферблата).
    // Меняет размер дила целиком и при этом сохраняет стыковку отрезков.
    // Меньше — шкала ближе к центру/мельче, больше — крупнее.
    property real divisionRadiusScale: 1.0

    // Центр глифа деления в координатах панели (родителя). Вычислен из ассета
    // division.svg (центр фигуры ≈ 829.5, 480.5 в его системе 1418×1028).
    // Используется как точка, вокруг которой масштабируется размер отрезка.
    property real divisionGlyphX: root.parent.width * (829.5 / 1418)
    property real divisionGlyphY: root.parent.height * (480.5 / 1028)

    // Деления шкалы спидометра.
    // Ассет division.svg нарисован в координатах всей панели и уже стоит на
    // первом отрезке (0..20). Остальные деления — его копии, повёрнутые вокруг
    // центра циферблата. Слой занимает весь экран панели (родителя), поэтому
    // смещаем его на положение спидометра.
    Repeater {
        model: root.divisionCount

        delegate: Image {
            source: "assets/division.svg"
            width: root.parent.width
            height: root.parent.height
            x: -root.x
            y: -root.y
            sourceSize: Qt.size(width, height)
            fillMode: Image.PreserveAspectFit
            smooth: true

            transform: [
                // 1) Размер отрезка: масштабируем глиф вокруг его центра.
                //    Радиус при этом не меняется, меняется только стыковка.
                Scale {
                    origin.x: root.divisionGlyphX
                    origin.y: root.divisionGlyphY
                    xScale: root.divisionSize
                    yScale: root.divisionSize
                },
                // 2) Радиус шкалы: масштабируем всё кольцо вокруг центра
                //    циферблата. Стыковка отрезков при этом сохраняется.
                Scale {
                    origin.x: root.x + root.width / 2
                    origin.y: root.y + root.height / 2
                    xScale: root.divisionRadiusScale
                    yScale: root.divisionRadiusScale
                },
                // 3) Совмещаем первое деление с началом дуги и
                //    раскладываем остальные с шагом divisionStep.
                Rotation {
                    origin.x: root.x + root.width / 2
                    origin.y: root.y + root.height / 2
                    angle: (root.startAngle - root.divisionAssetAngle)
                           + index * root.divisionStep
                }
            ]
        }
    }
}
