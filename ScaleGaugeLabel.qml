import QtQuick

// Подпись над шкалой в координатах panel.svg (1418×1028).
Item {
    id: root

    required property real panelWidth
    required property real panelHeight
    required property string fontFamily

    // Точка привязки по X в SVG; смысл зависит от horizontalAnchor.
    property real anchorXSvg: 0
    property real centerYSvg: 0
    property real fontSizeSvg: 11
    property string text: ""
    property color textColor: "#ffffff"
    property int fontWeight: Font.ExtraLight
    // left — левый край текста; center — центр; right — правый край.
    property string horizontalAnchor: "center"

    readonly property real scaleX: panelWidth / 1418
    readonly property real scaleY: panelHeight / 1028

    width: 0
    height: 0
    x: anchorXSvg * scaleX
    y: centerYSvg * scaleY

    Text {
        id: label
        anchors.verticalCenter: parent.verticalCenter
        x: {
            if (root.horizontalAnchor === "left")
                return 0
            if (root.horizontalAnchor === "right")
                return -width
            return -width / 2
        }
        text: root.text
        color: root.textColor
        font.family: root.fontFamily
        font.weight: root.fontWeight
        font.pixelSize: root.fontSizeSvg * root.scaleX
        horizontalAlignment: Text.AlignLeft
        verticalAlignment: Text.AlignVCenter
    }
}
