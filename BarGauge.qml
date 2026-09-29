import QtQuick

// Горизонтальная интерактивная шкала (№41 ОЖ / №23 топливо).
// Иконки остаются в panel.svg — здесь только сегменты шкалы.
// Координаты в системе panel.svg (1418×1028).
Item {
    id: root

    required property real panelWidth
    required property real panelHeight

    property real barLeftSvg: 0
    property real barRightSvg: 0
    property real barCenterYSvg: 0
    property real barHeightSvg: 8

    property int segmentCount: 8
    property real segmentGapSvg: 2

    property real value: 0
    property color fillColor: "#ffffff"
    property color emptyFillColor: "#000000"
    property color segmentBorderColor: "#808080"
    // 1 — красная окантовка у первой/последней ячейки;
    // 1.5 — плюс половина контура у соседней (ячейка целиком, без разреза).
    property color warningBorderColor: "#ff0000"
    property real warningBorderAtStart: 0
    property real warningBorderAtEnd: 0

    readonly property real scaleX: panelWidth / 1418
    readonly property real scaleY: panelHeight / 1028

    function svgX(xSvg: real): real { return xSvg * scaleX }
    function svgY(ySvg: real): real { return ySvg * scaleY }

    readonly property real filledSegments: Math.min(segmentCount,
                                                   Math.max(0, value * segmentCount))

    // Доля заполнения внутри ячейки segIndex (0 … 1).
    function fillFractionInSegment(segIndex: int): real {
        const fs = filledSegments
        if (fs <= segIndex)
            return 0
        if (fs >= segIndex + 1)
            return 1
        return fs - segIndex
    }

    anchors.fill: parent

    Item {
        id: barLayer
        readonly property real barLeft: root.svgX(root.barLeftSvg)
        readonly property real barTop: root.svgY(root.barCenterYSvg) - root.svgY(root.barHeightSvg) / 2
        readonly property real barWidth: root.svgX(root.barRightSvg) - barLeft
        readonly property real barHeight: root.svgY(root.barHeightSvg)
        readonly property real gap: root.svgX(root.segmentGapSvg)
        readonly property real segmentWidth: root.segmentCount > 0
            ? Math.max(0, (barWidth - gap * (root.segmentCount - 1)) / root.segmentCount)
            : 0
        readonly property real borderW: Math.max(1, barHeight * 0.14)

        function segX(index: int): real {
            return index * (segmentWidth + gap)
        }

        x: barLeft
        y: barTop
        width: barWidth
        height: barHeight

        Repeater {
            model: root.segmentCount

            Rectangle {
                readonly property bool filled: index < Math.floor(root.filledSegments)

                x: barLayer.segX(index)
                width: barLayer.segmentWidth
                height: parent.height
                radius: height * 0.15
                color: filled ? root.fillColor : root.emptyFillColor
                border.color: root.segmentBorderColor
                border.width: barLayer.borderW
            }
        }

        // --- Красная окантовка (под заливкой; убирается по мере заполнения) ---

        // Первая ячейка — весь контур красный, съедается слева направо.
        Item {
            readonly property real fi: root.fillFractionInSegment(0)
            visible: root.warningBorderAtStart >= 1 && fi < 1
            x: barLayer.segX(0)
            width: barLayer.segmentWidth
            height: parent.height

            readonly property real inset: fi * width

            Rectangle {
                visible: parent.inset < 0.001
                width: barLayer.borderW
                height: parent.height
                color: root.warningBorderColor
            }
            Rectangle {
                x: parent.inset
                width: Math.max(0, parent.width - parent.inset)
                height: barLayer.borderW
                color: root.warningBorderColor
            }
            Rectangle {
                x: parent.inset
                y: parent.height - barLayer.borderW
                width: Math.max(0, parent.width - parent.inset)
                height: barLayer.borderW
                color: root.warningBorderColor
            }
            Rectangle {
                x: parent.width - barLayer.borderW
                width: barLayer.borderW
                height: parent.height
                color: root.warningBorderColor
            }
        }

        // Вторая ячейка — красная левая половина контура.
        Item {
            readonly property real fi: root.fillFractionInSegment(1)
            visible: root.warningBorderAtStart > 1 && root.filledSegments < 2
            x: barLayer.segX(1)
            width: barLayer.segmentWidth
            height: parent.height

            readonly property real halfW: width / 2
            readonly property real topStart: fi * width
            readonly property real topLen: Math.max(0, halfW - topStart)

            Rectangle {
                visible: parent.fi < 0.001
                width: barLayer.borderW
                height: parent.height
                color: root.warningBorderColor
            }
            Rectangle {
                x: parent.topStart
                width: parent.topLen
                height: barLayer.borderW
                color: root.warningBorderColor
            }
            Rectangle {
                x: parent.topStart
                y: parent.height - barLayer.borderW
                width: parent.topLen
                height: barLayer.borderW
                color: root.warningBorderColor
            }
        }

        // Последняя ячейка — весь контур красный, съедается слева направо.
        Item {
            readonly property int segIndex: root.segmentCount - 1
            readonly property real fi: root.fillFractionInSegment(segIndex)
            visible: root.warningBorderAtEnd >= 1 && fi < 1
            x: barLayer.segX(segIndex)
            width: barLayer.segmentWidth
            height: parent.height

            readonly property real inset: fi * width

            Rectangle {
                visible: parent.inset < 0.001
                width: barLayer.borderW
                height: parent.height
                color: root.warningBorderColor
            }
            Rectangle {
                x: parent.inset
                width: Math.max(0, parent.width - parent.inset)
                height: barLayer.borderW
                color: root.warningBorderColor
            }
            Rectangle {
                x: parent.inset
                y: parent.height - barLayer.borderW
                width: Math.max(0, parent.width - parent.inset)
                height: barLayer.borderW
                color: root.warningBorderColor
            }
            Rectangle {
                x: parent.width - barLayer.borderW
                width: barLayer.borderW
                height: parent.height
                color: root.warningBorderColor
            }
        }

        // Предпоследняя — красная правая половина контура.
        Item {
            readonly property int segIndex: root.segmentCount - 2
            readonly property real fi: root.fillFractionInSegment(segIndex)
            visible: root.warningBorderAtEnd > 1 && root.filledSegments < root.segmentCount - 1
            x: barLayer.segX(segIndex)
            width: barLayer.segmentWidth
            height: parent.height

            readonly property real halfW: width / 2
            readonly property real topStart: Math.max(halfW, fi * width)
            readonly property real topLen: Math.max(0, width - topStart)

            Rectangle {
                x: parent.width - barLayer.borderW
                width: barLayer.borderW
                height: parent.height
                color: root.warningBorderColor
            }
            Rectangle {
                x: parent.topStart
                width: parent.topLen
                height: barLayer.borderW
                color: root.warningBorderColor
            }
            Rectangle {
                x: parent.topStart
                y: parent.height - barLayer.borderW
                width: parent.topLen
                height: barLayer.borderW
                color: root.warningBorderColor
            }
        }

        Rectangle {
            visible: root.filledSegments > 0
                     && root.filledSegments < root.segmentCount
                     && (root.filledSegments - Math.floor(root.filledSegments)) > 0.001
            x: Math.floor(root.filledSegments) * (barLayer.segmentWidth + barLayer.gap)
            width: barLayer.segmentWidth * (root.filledSegments - Math.floor(root.filledSegments))
            height: parent.height
            radius: height * 0.15
            color: root.fillColor
        }
    }
}
