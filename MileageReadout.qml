import QtQuick

// №31 / №33 / №19: число слева от единицы (зазор gapSvg), общий центр по Y.
Item {
    id: root

    required property real panelWidth
    required property real panelHeight
    required property string fontFamily

    property real centerXSvg: 0
    property real centerYSvg: 0
    property real fontSizeSvg: 10
    property real gapSvg: 1
    property string unitText: "km"
    property string valueText: ""

    readonly property real scaleX: panelWidth / 1418
    readonly property real scaleY: panelHeight / 1028

    width: 0
    height: 0
    x: centerXSvg * scaleX
    y: centerYSvg * scaleY

    Text {
        id: unitLabel
        anchors.centerIn: parent
        text: root.unitText
        color: "#ffffff"
        font.family: root.fontFamily
        font.weight: Font.ExtraLight
        font.pixelSize: root.fontSizeSvg * root.scaleX
        horizontalAlignment: Text.AlignHCenter
        verticalAlignment: Text.AlignVCenter
    }

    Text {
        anchors.right: unitLabel.left
        anchors.rightMargin: root.gapSvg * root.scaleX
        anchors.verticalCenter: unitLabel.verticalCenter
        text: root.valueText
        color: "#ffffff"
        font.family: root.fontFamily
        font.weight: Font.ExtraLight
        font.pixelSize: root.fontSizeSvg * root.scaleX
        horizontalAlignment: Text.AlignRight
        verticalAlignment: Text.AlignVCenter
    }
}
