import QtQuick

// Стрелка прибора. Картинка стрелки нарисована в координатах всей панели и уже
// стоит в положении minValue. Анимация — поворот вокруг оси циферблата.
Image {
    id: root

    // --- Шкала ---
    property real value: 0          // текущее значение
    property real minValue: 0       // значение в нарисованном положении стрелки
    property real maxValue: 220     // значение в конце шкалы

    // На сколько градусов повернуть стрелку от нарисованного положения (minValue)
    // до конца шкалы (maxValue). Плюс — по часовой стрелке. Подгоняется по рисунку.
    property real sweepAngle: 240

    // Ось вращения в координатах этого изображения (= координаты панели).
    property real pivotX: 0
    property real pivotY: 0

    // Угол на шкале (Canvas: 0° = вправо, по часовой) в положении minValue.
    property real dialZeroAngle: 149.48

    readonly property real rotationDeg:
        (value - minValue) / (maxValue - minValue) * sweepAngle

    readonly property real dialAngle: dialZeroAngle + rotationDeg

    fillMode: Image.PreserveAspectFit
    sourceSize: Qt.size(width, height)
    smooth: true
    mipmap: true

    transform: Rotation {
        origin.x: root.pivotX
        origin.y: root.pivotY
        angle: root.rotationDeg
    }
}
