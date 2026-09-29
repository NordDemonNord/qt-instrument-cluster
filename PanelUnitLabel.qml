import QtQuick

// Статичная подпись единиц в координатах panel.svg (1418×1028).
Item {
    id: root

    required property real panelWidth
    required property real panelHeight
    required property string fontFamily

    property real centerXSvg: 0
    property real centerYSvg: 0
    property real fontSizeSvg: 8
    property string text: ""
    property real rotationDeg: 0

    readonly property real scaleX: panelWidth / 1418
    readonly property real scaleY: panelHeight / 1028

    width: 0
    height: 0
    x: centerXSvg * scaleX
    y: centerYSvg * scaleY

    Item {
        anchors.centerIn: parent
        width: label.implicitWidth
        height: label.implicitHeight
        rotation: root.rotationDeg
        transformOrigin: Item.Center

        Text {
            id: label
            anchors.centerIn: parent
            text: root.text
            color: "#ffffff"
            font.family: root.fontFamily
            font.weight: Font.ExtraLight
            font.pixelSize: root.fontSizeSvg * root.scaleX
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
    }
}
