import QtQuick
import Qt5Compat.GraphicalEffects

// Кольцо-заливка между хабом и делениями.
// База кэшируется; подсветка рисуется в маленьком холсте у циферблата.
Item {
    id: root

    property real panelScale: 1.0
    property real centerXSvg: 0
    property real centerYSvg: 0
    property real innerRadiusSvg: 66
    property real outerRadiusSvg: 100
    property real edgeBandSvg: 7
    // Ширина внутренней светлой кромки (у хаба).
    property real innerEdgeBandSvg: 2.5
    property real innerBlendExtend: 1.2
    // Плавный переход рубин → серая середина (только наружу от границы кольца).
    property real innerBoundaryFeatherFrac: 0.14

    property real startAngle: 150
    property real sweepAngle: 240

    property real rotationDeg: 0
    property real dialZeroAngle: 149.48
    property real highlightLeadDeg: 0

    property color baseColor: "#18181E"
    property color innerZoneDeepColor: "#450A14"
    property color innerZoneColor: "#651018"
    property color innerZoneMidColor: "#7A1A28"
    property color innerEdgeHighlightColor: "#A52E3C"
    property color innerBoundaryTintColor: "#2A2226"
    property color innerBoundaryTint2Color: "#1E1C20"
    property color edgeWhiteColor: "#54545E"
    property color glowColor: "#ffffff"

    property bool innerGlowEnabled: true
    property color innerGlowColor: "#3A0810"
    property real innerGlowAlpha: 0.65
    property real innerGlowRadius: 9
    property real innerGlowSpread: 0.12
    property real innerGlowSpreadFrac: 0.07

    property int radialSteps: 64
    property int highlightRadialSteps: 8
    property real blendExtend: 2.0
    property real highlightSpanDeg: 46
    property int highlightSlices: 20
    property real highlightStrength: 0.72

    anchors.fill: parent

    readonly property real highlightSide:
        outerRadiusSvg * 2 * panelScale + 8

    readonly property real glowMargin:
        innerGlowRadius * panelScale * 2.2

    readonly property real innerGlowSide:
        highlightSide + glowMargin * 2

    function repaintBase() { baseCanvas.requestPaint() }
    function repaintGlow() { innerGlowCanvas.requestPaint() }
    function repaintHighlight() { highlightCanvas.requestPaint() }
    function repaintAll() { repaintBase(); repaintGlow(); repaintHighlight() }

    onPanelScaleChanged: repaintAll()
    onWidthChanged: repaintBase()
    onHeightChanged: repaintBase()
    onInnerRadiusSvgChanged: repaintAll()
    onOuterRadiusSvgChanged: repaintAll()
    onEdgeBandSvgChanged: repaintAll()
    onInnerEdgeBandSvgChanged: repaintAll()
    onBlendExtendChanged: repaintAll()
    onRadialStepsChanged: repaintAll()
    onHighlightRadialStepsChanged: repaintHighlight()
    onStartAngleChanged: repaintAll()
    onSweepAngleChanged: repaintAll()
    onBaseColorChanged: repaintBase()
    onInnerZoneColorChanged: repaintAll()
    onInnerEdgeHighlightColorChanged: repaintAll()
    onInnerBlendExtendChanged: repaintAll()
    onInnerBoundaryFeatherFracChanged: repaintAll()
    onInnerZoneDeepColorChanged: repaintAll()
    onInnerZoneMidColorChanged: repaintAll()
    onInnerBoundaryTintColorChanged: repaintAll()
    onInnerBoundaryTint2ColorChanged: repaintAll()
    onInnerGlowEnabledChanged: repaintGlow()
    onInnerGlowColorChanged: repaintGlow()
    onInnerGlowAlphaChanged: repaintGlow()
    onInnerGlowRadiusChanged: repaintGlow()
    onInnerGlowSpreadChanged: repaintGlow()
    onInnerGlowSpreadFracChanged: repaintGlow()
    onEdgeWhiteColorChanged: repaintBase()
    onGlowColorChanged: repaintHighlight()
    onDialZeroAngleChanged: repaintHighlight()
    onHighlightLeadDegChanged: repaintHighlight()
    onHighlightSpanDegChanged: repaintHighlight()
    onHighlightSlicesChanged: repaintHighlight()
    onHighlightStrengthChanged: repaintHighlight()
    onRotationDegChanged: repaintHighlight()
    onCenterXSvgChanged: repaintHighlight()
    onCenterYSvgChanged: repaintHighlight()

    function lerpColor(c0, c1, t) {
        if (t < 0) t = 0;
        if (t > 1) t = 1;
        return Qt.rgba(c0.r + (c1.r - c0.r) * t,
                       c0.g + (c1.g - c0.g) * t,
                       c0.b + (c1.b - c0.b) * t, 1.0);
    }

    function smoother(t) {
        if (t < 0) t = 0;
        if (t > 1) t = 1;
        return t * t * t * (t * (t * 6 - 15) + 10);
    }

    function innerBlendFrac() {
        var thickness = outerRadiusSvg - innerRadiusSvg;
        var edgeFrac = Math.min(0.35, innerEdgeBandSvg / thickness);
        return edgeFrac * innerBlendExtend;
    }

    function outerBlendFrac() {
        var thickness = outerRadiusSvg - innerRadiusSvg;
        var edgeFrac = Math.min(0.35, edgeBandSvg / thickness);
        return edgeFrac * blendExtend;
    }

    function sampleGradient(stops, t) {
        if (t <= stops[0].pos)
            return stops[0].color;
        for (var i = 1; i < stops.length; i++) {
            if (t <= stops[i].pos) {
                var span = stops[i].pos - stops[i - 1].pos;
                var localT = span > 0 ? (t - stops[i - 1].pos) / span : 0;
                return lerpColor(stops[i - 1].color, stops[i].color, smoother(localT));
            }
        }
        return stops[stops.length - 1].color;
    }

    function innerZoneFillColor(normR) {
        var innerBlend = innerBlendFrac();
        if (innerBlend <= 0)
            return innerZoneColor;
        // 0 — внешний край кольца (тёмный), 1 — у хаба (светлее).
        var u = 1.0 - normR / innerBlend;
        return sampleGradient([
            { pos: 0.0, color: innerZoneDeepColor },
            { pos: 0.38, color: innerZoneColor },
            { pos: 0.72, color: innerZoneMidColor },
            { pos: 1.0, color: innerEdgeHighlightColor }
        ], u);
    }

    // Серая середина + внешняя кромка; у внутренней границы — многоступенчатый переход.
    function middleZoneColor(normR) {
        var innerBlend = innerBlendFrac();
        var feather = innerBoundaryFeatherFrac;
        var outerBlend = outerBlendFrac();

        if (normR < innerBlend + feather) {
            var t = (normR - innerBlend) / feather;
            if (t < 0)
                t = 0;
            var rubyEdge = innerZoneFillColor(innerBlend);
            return sampleGradient([
                { pos: 0.0, color: rubyEdge },
                { pos: 0.35, color: innerBoundaryTintColor },
                { pos: 0.68, color: innerBoundaryTint2Color },
                { pos: 1.0, color: baseColor }
            ], t);
        }

        var wOuter = 0;
        if (normR > 1.0 - outerBlend)
            wOuter = smoother((normR - (1.0 - outerBlend)) / outerBlend) * 0.75;

        return lerpColor(baseColor, edgeWhiteColor, wOuter);
    }

    function radialZoneColor(normR) {
        if (normR < innerBlendFrac())
            return innerZoneFillColor(normR);
        return middleZoneColor(normR);
    }

    function paintClosedInnerBand(ctx, cx, cy, r0, r1, a0, a1, fullCircle, color) {
        sector(ctx, cx, cy, r0, r1, a0, a1, color);
        sector(ctx, cx, cy, r0, r1, a1, a0 + fullCircle, color);
    }

    function sector(ctx, cx, cy, ri, ro, a0, a1, color) {
        if (ro <= ri || a1 <= a0)
            return;
        ctx.beginPath();
        ctx.arc(cx, cy, ro, a0, a1, false);
        ctx.arc(cx, cy, ri, a1, a0, true);
        ctx.closePath();
        ctx.fillStyle = color;
        ctx.fill();
    }

    function paintBase(ctx) {
        ctx.reset();

        var s = panelScale;
        var cx = centerXSvg * s;
        var cy = centerYSvg * s;
        var ri = innerRadiusSvg * s;
        var ro = outerRadiusSvg * s;

        var d2r = Math.PI / 180;
        var a0 = startAngle * d2r;
        var a1 = (startAngle + sweepAngle) * d2r;
        var innerBlend = innerBlendFrac();
        var fullCircle = 2 * Math.PI;

        var steps = radialSteps;
        for (var j = 0; j < steps; j++) {
            var t0 = j / steps;
            var t1 = (j + 1) / steps;
            var normMid = (t0 + t1) * 0.5;
            if (normMid >= innerBlend)
                continue;

            var r0 = ri + (ro - ri) * t0;
            var r1 = ri + (ro - ri) * t1;
            var innerColor = innerZoneFillColor(normMid);

            // Внутреннее кольцо: дуга шкалы + зазор = замкнутое кольцо.
            paintClosedInnerBand(ctx, cx, cy, r0, r1, a0, a1, fullCircle, innerColor);
        }

        for (j = 0; j < steps; j++) {
            t0 = j / steps;
            t1 = (j + 1) / steps;
            normMid = (t0 + t1) * 0.5;
            if (normMid < innerBlend)
                continue;

            r0 = ri + (ro - ri) * t0;
            r1 = ri + (ro - ri) * t1;
            sector(ctx, cx, cy, r0, r1, a0, a1, middleZoneColor(normMid));
        }

        // Вырез по внутреннему краю кольца — совпадает с геометрией фона.
        ctx.save();
        ctx.globalCompositeOperation = 'destination-out';
        ctx.beginPath();
        ctx.arc(cx, cy, ri, 0, fullCircle);
        ctx.fill();
        ctx.restore();
    }

    // Маска для Glow: рубиновое кольцо + мягкий выброс наружу по дуге.
    function paintInnerGlow(ctx, canvasSize) {
        ctx.reset();

        var s = panelScale;
        var cx = canvasSize * 0.5;
        var cy = canvasSize * 0.5;
        var ri = innerRadiusSvg * s;
        var ro = outerRadiusSvg * s;

        var d2r = Math.PI / 180;
        var a0 = startAngle * d2r;
        var a1 = (startAngle + sweepAngle) * d2r;
        var innerBlend = innerBlendFrac();
        var glowSpread = innerGlowSpreadFrac;
        var maxNorm = innerBlend + glowSpread;
        var fullCircle = 2 * Math.PI;
        var steps = radialSteps;

        for (var j = 0; j < steps; j++) {
            var t0 = j / steps;
            var t1 = (j + 1) / steps;
            var normMid = (t0 + t1) * 0.5;
            if (normMid > maxNorm)
                continue;

            var alpha = 0;
            if (normMid <= innerBlend) {
                alpha = innerGlowAlpha * 0.8;
            } else {
                var spillT = (normMid - innerBlend) / glowSpread;
                alpha = innerGlowAlpha * (1.0 - smoother(spillT)) * 0.35;
            }
            if (alpha <= 0.01)
                continue;

            var r0 = ri + (ro - ri) * t0;
            var r1 = ri + (ro - ri) * t1;
            var maskColor = Qt.rgba(innerGlowColor.r, innerGlowColor.g, innerGlowColor.b, alpha);

            if (normMid <= innerBlend)
                paintClosedInnerBand(ctx, cx, cy, r0, r1, a0, a1, fullCircle, maskColor);
            else
                sector(ctx, cx, cy, r0, r1, a0, a1, maskColor);
        }
    }

    // Осветляет фон у стрелки; угловой диапазон обрезается по дуге шкалы.
    function paintHighlight(ctx, canvasSize) {
        ctx.reset();

        var s = panelScale;
        var cx = canvasSize * 0.5;
        var cy = canvasSize * 0.5;
        var ri = innerRadiusSvg * s;
        var ro = outerRadiusSvg * s;

        var d2r = Math.PI / 180;
        var arcStart = startAngle * d2r;
        var arcEnd = (startAngle + sweepAngle) * d2r;
        var centerRad = (dialZeroAngle + rotationDeg + highlightLeadDeg) * d2r;
        var halfSpan = (highlightSpanDeg * 0.5) * d2r;
        var spanStart = Math.max(centerRad - halfSpan, arcStart);
        var spanEnd = Math.min(centerRad + halfSpan, arcEnd);
        if (spanEnd <= spanStart)
            return;

        var angSlices = highlightSlices;
        var radSteps = highlightRadialSteps;
        var angStep = (spanEnd - spanStart) / angSlices;
        var fullHalfSpan = halfSpan;

        for (var i = 0; i < angSlices; i++) {
            var sa = spanStart + angStep * i;
            var sb = spanStart + angStep * (i + 1) + 0.001;
            var distFromCenter = Math.abs((sa + sb) * 0.5 - centerRad);
            var angT = distFromCenter / fullHalfSpan;
            if (angT > 1)
                angT = 1;
            // Косинусный спад — длиннее и мягче, без полос от сегментов.
            var angIntensity = 0.5 * (1 + Math.cos(angT * Math.PI)) * highlightStrength;

            for (var j = 0; j < radSteps; j++) {
                var t0 = j / radSteps;
                var t1 = (j + 1) / radSteps;
                var r0 = ri + (ro - ri) * t0;
                var r1 = ri + (ro - ri) * t1;
                var normMid = (t0 + t1) * 0.5;
                var zoneColor = radialZoneColor(normMid);
                sector(ctx, cx, cy, r0, r1, sa, sb,
                       lerpColor(zoneColor, glowColor, angIntensity));
            }
        }
    }

    Canvas {
        id: baseCanvas
        anchors.fill: parent
        antialiasing: true

        Component.onCompleted: requestPaint()
        onPaint: root.paintBase(getContext("2d"))
    }

    // Статическое рубиновое свечение внутреннего кольца.
    Item {
        id: innerGlowHost
        width: root.innerGlowSide
        height: root.innerGlowSide
        x: root.centerXSvg * root.panelScale - width * 0.5
        y: root.centerYSvg * root.panelScale - height * 0.5
        visible: root.innerGlowEnabled
        z: 1

        Canvas {
            id: innerGlowCanvas
            anchors.fill: parent
            antialiasing: true
            visible: false

            Component.onCompleted: requestPaint()
            onPaint: root.paintInnerGlow(getContext("2d"), width)
        }

        Glow {
            anchors.fill: parent
            source: innerGlowCanvas
            radius: root.innerGlowRadius * root.panelScale
            samples: Math.round(1 + root.innerGlowRadius * root.panelScale * 2)
            spread: root.innerGlowSpread
            color: root.innerGlowColor
            transparentBorder: true
            cached: true
        }
    }

    // Подсветка у стрелки (без свечения).
    Item {
        id: highlightHost
        width: root.highlightSide
        height: root.highlightSide
        x: root.centerXSvg * root.panelScale - width * 0.5
        y: root.centerYSvg * root.panelScale - height * 0.5
        z: 2

        Canvas {
            id: highlightCanvas
            anchors.fill: parent
            antialiasing: true
            renderStrategy: Canvas.Immediate

            Component.onCompleted: requestPaint()
            onPaint: root.paintHighlight(getContext("2d"), width)
        }
    }
}
