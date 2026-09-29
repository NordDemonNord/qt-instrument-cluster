import QtQuick
import Qt5Compat.GraphicalEffects

// Индикатор-пиктограмма (tell-tale) с поддержкой CAN-состояний:
// active, color, blinking, opacity.
// Позиция задаётся центром в координатах panel.svg (1418×1028).
Item {
    id: root

    required property real panelWidth
    required property real panelHeight

    property string iconSource: ""
    property real centerXSvg: 0
    property real centerYSvg: 0
    property real centerYOffsetSvg: 0
    property real iconSizeSvg: 16
    // Соотношение сторон иконки (ширина/высота). 1 = квадрат.
    // Для широких иконок (например 166.4×130.49) указывать реальное w/h,
    // иначе PreserveAspectFit впишет её в квадрат и сдвинет/сожмёт.
    property real iconAspect: 1.0

    property bool active: false
    property bool colorize: true
    property color color: "#ffffff"
    property real inactiveOpacity: 0
    property real activeOpacity: 1

    property bool blinking: false
    property int blinkIntervalMs: 500

    readonly property real scaleX: panelWidth / 1418
    readonly property real scaleY: panelHeight / 1028

    readonly property real iconPixelSize: iconSizeSvg * scaleX
    readonly property real iconPixelWidth: iconPixelSize * iconAspect

    property bool _blinkPhase: true

    width: iconPixelWidth
    height: iconPixelSize
    x: centerXSvg * scaleX - width / 2
    y: (centerYSvg + centerYOffsetSvg) * scaleY - height / 2

    opacity: {
        if (!active)
            return inactiveOpacity
        if (!blinking)
            return activeOpacity
        return _blinkPhase ? activeOpacity : inactiveOpacity
    }

    Timer {
        interval: root.blinkIntervalMs
        running: root.active && root.blinking
        repeat: true
        onTriggered: root._blinkPhase = !root._blinkPhase
    }

    onActiveChanged: if (!active) _blinkPhase = true
    onBlinkingChanged: if (!blinking) _blinkPhase = true

    Image {
        id: iconImage
        anchors.fill: parent
        source: root.iconSource
        sourceSize: Qt.size(root.iconPixelWidth, root.iconPixelSize)
        fillMode: Image.PreserveAspectFit
        smooth: true
        visible: !root.colorize
    }

    ColorOverlay {
        anchors.fill: iconImage
        source: iconImage
        visible: root.colorize
        color: root.active ? root.color : Qt.rgba(0, 0, 0, 0)
    }
}
