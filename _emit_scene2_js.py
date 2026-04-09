# -*- coding: utf-8 -*-
"""One-shot: write scene2_charts_code.js (run once, can delete this file after)."""
from pathlib import Path

JS = r'''

  function chartDonutLeadersSub(container, rows) {
    var agg = sortPhases(aggregate(rows, F.细分).filter(function (d) { return d.count > 0; }));
    if (!agg.length) return;
    var w = chartBoxW(container);
    var h = 400;
    var cx = w * 0.38;
    var cy = h * 0.5;
    var ir = 46;
    var or = 96;
    var pie = d3.pie().value(function (d) { return d.count; }).sort(null);
    var arc = d3.arc().innerRadius(ir).outerRadius(or).cornerRadius(1.5);
    var arcs = pie(agg);
    var tot = d3.sum(agg, function (d) { return d.count; }) || 1;
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    var defs = svg.append("defs");
    var g = svg.append("g").attr("transform", "translate(" + cx + "," + cy + ")");
    arcs.forEach(function (d, i) {
      var col = PAL[i % 4];
      var fillG = chartBarGradientUrl(defs, "s2d_" + i, col);
      g.append("path").attr("d", arc(d)).attr("fill", fillG).attr("stroke", "rgba(0,0,0,0.5)").attr("stroke-width", 1.2)
        .style("cursor", "pointer")
        .attr("opacity", 0)
        .on("click", function () { setPhase(d.data.key); })
        .on("mouseenter", function (ev) {
          var p = Math.round(d.data.count / tot * 100);
          tipShow(ev, esc(String(d.data.key)) + "<br>" + d.data.count + " 条 · " + p + "%");
        })
        .on("mousemove", moveTip).on("mouseleave", tipHide)
        .transition().duration(520).delay(i * 70).attr("opacity", 1);
      var mid = (d.startAngle + d.endAngle) / 2 - Math.PI / 2;
      var ox = Math.cos(mid) * (or + 6);
      var oy = Math.sin(mid) * (or + 6);
      var lx = Math.cos(mid) * (or + 32);
      var ly = Math.sin(mid) * (or + 32);
      var tx = cx + lx + (lx >= 0 ? 10 : -10);
      var ty = cy + ly;
      var lab = String(d.data.key).length > 9 ? String(d.data.key).slice(0, 8) + "…" : d.data.key;
      svg.append("polyline")
        .attr("points", (cx + ox) + "," + (cy + oy) + " " + (cx + lx) + "," + (cy + ly) + " " + tx + "," + ty)
        .attr("fill", "none").attr("stroke", "rgba(255,255,255,0.5)").attr("stroke-width", 1)
        .attr("opacity", 0).transition().delay(180 + i * 70).duration(380).attr("opacity", 1);
      svg.append("text").attr("x", tx + (lx >= 0 ? 4 : -4)).attr("y", ty + 4)
        .attr("text-anchor", lx >= 0 ? "start" : "end").attr("fill", "#eee").style("font-size", "10px").attr("opacity", 0)
        .text(lab + " " + Math.round(d.data.count / tot * 100) + "%")
        .transition().delay(240 + i * 70).duration(320).attr("opacity", 1);
    });
    g.append("circle").attr("r", ir - 1).attr("fill", "rgba(10,10,16,0.95)").attr("stroke", "rgba(255,255,255,0.15)");
    setFigCaptionLegend(container, agg.map(function (d, i) { return { hex: PAL[i % 4], text: d.key }; }),
      "环形 + 外引线（参考图1上）。无同心读数格，与场景一甜甜圈区分。点击扇区筛细分阶段。\n" + captionSampleLine(rows));
  }

  function chartPolarSpikeComplexity(container, rows) {
    var keys = ["1", "2", "3", "4", "5"];
    var pts = keys.map(function (k) {
      return { k: k, v: rows.filter(function (r) { return String(r[F.复杂度]) === k; }).length };
    });
    if (!d3.sum(pts, function (d) { return d.v; })) return;
    var w = chartBoxW(container);
    var R = Math.min(142, w / 2 - 24);
    var cx = w / 2;
    var cy = R + 44;
    var h = cy + R + 56;
    var maxV = d3.max(pts, function (d) { return d.v; }) || 1;
    var rS = d3.scaleLinear().domain([0, maxV]).range([22, R]);
    var n = pts.length;
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    var gridG = svg.append("g").attr("class", "chart-grid-layer").attr("pointer-events", "none");
    var gr = 0;
    d3.range(0, 5).forEach(function (i) {
      var rr = (i / 4) * R;
      var c = gridG.append("circle").attr("cx", cx).attr("cy", cy).attr("r", rr).attr("fill", "none")
        .attr("stroke", CHART_GRID_STROKE).attr("stroke-width", CHART_GRID_W);
      revealCircleStroke(d3.select(c.node()), rr, 520, gr);
      gr += 10;
    });
    var seg = pts.map(function (d, i) {
      var ang = (i / n) * 2 * Math.PI - Math.PI / 2;
      var rr = rS(d.v);
      return [cx + Math.cos(ang) * rr, cy + Math.sin(ang) * rr];
    });
    var line = d3.line().curve(d3.curveLinearClosed);
    svg.append("path").datum(seg).attr("d", line).attr("fill", "rgba(245,69,149,0.18)").attr("stroke", PAL[0]).attr("stroke-width", 2.8)
      .attr("opacity", 0).transition().duration(880).attr("opacity", 1);
    pts.forEach(function (d, i) {
      var ang = (i / n) * 2 * Math.PI - Math.PI / 2;
      var rr = rS(d.v);
      var px = cx + Math.cos(ang) * rr;
      var py = cy + Math.sin(ang) * rr;
      svg.append("circle").attr("cx", px).attr("cy", py).attr("r", 0).attr("fill", "#fff").attr("stroke", PAL[1]).attr("stroke-width", 2)
        .style("cursor", "pointer")
        .on("click", function () { setFilter(F.复杂度, d.k); })
        .on("mouseenter", function (ev) { tipShow(ev, "复杂度 " + d.k + "<br>" + d.v + " 条"); })
        .on("mousemove", moveTip).on("mouseleave", tipHide)
        .transition().delay(350 + i * 60).duration(340).attr("r", 5.5);
      var tx = cx + Math.cos(ang) * (R + 18);
      var ty = cy + Math.sin(ang) * (R + 18);
      svg.append("text").attr("x", tx).attr("y", ty + 3).attr("text-anchor", "middle").attr("fill", "#aaa").style("font-size", "9px").text("L" + d.k);
    });
    setFigCaptionLegend(container, [{ hex: PAL[0], text: "放射折线面包络（参考图1下）" }],
      "角位=复杂度等级，半径=条数；闭合折线+填色，非场景一极坐标柱。\n" + captionSampleLine(rows));
  }

  function chartBeeswarmSubPackWc(container, rows) {
    var subs = ["动作模板化", "回复工具化", "聊天迁移"];
    var w = chartBoxW(container);
    var m = { t: 32, l: 118, r: 20, b: 44 };
    var iw = w - m.l - m.r;
    var rowH = 84;
    var h = m.t + subs.length * rowH + m.b;
    var xS = d3.scaleLinear().domain([0.5, 5.5]).range([m.l, m.l + iw]);
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    svg.append("line").attr("x1", m.l - 12).attr("x2", m.l - 12).attr("y1", m.t).attr("y2", h - m.b)
      .attr("stroke", "rgba(255,255,255,0.32)").attr("stroke-width", 1).attr("stroke-dasharray", "4 5");
    subs.forEach(function (sub, ri) {
      var yy = m.t + ri * rowH;
      var subRows = rows.filter(function (r) { return norm(r[F.细分]) === sub; });
      var emoRank = aggregate(subRows, F.情绪);
      svg.append("line").attr("x1", m.l).attr("x2", m.l + iw).attr("y1", yy + rowH / 2).attr("y2", yy + rowH / 2)
        .attr("stroke", CHART_GRID_STROKE).attr("stroke-width", 0.6).attr("stroke-dasharray", "3 6");
      svg.append("text").attr("x", m.l - 18).attr("y", yy + rowH / 2 + 4).attr("text-anchor", "end").attr("fill", "#ccc").style("font-size", "9px")
        .text(sub.length > 6 ? sub.slice(0, 5) + "…" : sub);
      subRows.forEach(function (r, j) {
        var pk = +r[F.包装];
        var wc = +r[F.字数];
        if (isNaN(pk)) return;
        var jitter = (seed01(j + ri * 997) - 0.5) * (iw / 26);
        var jy = (seed01(j * 7919 + ri) - 0.5) * (rowH * 0.58);
        var cxi = xS(pk) + jitter;
        var cyi = yy + rowH / 2 + jy;
        var rad = 3.5 + Math.sqrt(Math.min(wc + 1, 28)) * 1.25;
        var emoIdx = 0;
        emoRank.forEach(function (e, ei) { if (norm(e.key) === norm(r[F.情绪])) emoIdx = ei; });
        var col = PAL[emoIdx % 4];
        var href = thumb(r) || IMG_PLACEHOLDER;
        svg.append("circle").attr("cx", cxi).attr("cy", cyi).attr("r", 0)
          .attr("fill", col).attr("fill-opacity", 0.78).attr("stroke", "#fff").attr("stroke-width", 1.1)
          .style("cursor", "pointer")
          .on("click", function () { setPhase(sub); setFilter(F.包装, String(pk)); })
          .on("mouseenter", function (ev) {
            tipShow(ev, (href !== IMG_PLACEHOLDER ? "<img src=\"" + esc(href) + "\" alt=\"\">" : "") + esc(norm(r[F.图字]) || "（无图内字）"));
          })
          .on("mousemove", moveTip).on("mouseleave", tipHide)
          .transition().delay(j * 3).duration(300).ease(d3.easeElasticOut).attr("r", rad);
      });
    });
    var gAx = svg.append("g").attr("transform", "translate(0," + (h - m.b + 4) + ")")
      .call(d3.axisBottom(xS).ticks(5).tickFormat(d3.format("d")))
      .call(function (gg) { gg.select(".domain").attr("stroke", CHART_AXIS_DOMAIN_STROKE).attr("stroke-width", 1.3); });
    gAx.selectAll("text").attr("fill", "#999").style("font-size", "9px");
    svg.append("text").attr("x", m.l + iw / 2).attr("y", h - 6).attr("text-anchor", "middle").attr("fill", "#777").style("font-size", "9px")
      .text("横轴：包装度 · 面积≈字数 · 色：情绪（参考气泡带）");
    setFigCaptionLegend(container, [{ hex: PAL[0], text: "细分×包装×字数×情绪" }],
      "左侧虚线分隔类目。悬停见缩略图与图内字。\n" + captionSampleLine(rows));
  }

  function chartSplineDropEmotion(container, rows) {
    var top = aggregate(rows, F.情绪).slice(0, 7);
    if (!top.length) return;
    var w = chartBoxW(container);
    var margin = { t: 28, r: 28, b: 56, l: 36 };
    var iw = w - margin.l - margin.r;
    var ih = 280;
    var h = margin.t + ih + margin.b;
    var xS = d3.scalePoint().domain(top.map(function (d) { return d.key; })).range([margin.l, margin.l + iw]).padding(0.5);
    var maxC = d3.max(top, function (d) { return d.count; }) || 1;
    var yS = d3.scaleLinear().domain([0, maxC]).nice().range([margin.t + ih, margin.t]);
    var line = d3.line().x(function (d) { return xS(d.key); }).y(function (d) { return yS(d.count); }).curve(d3.curveMonotoneX);
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    var gridG = svg.append("g").attr("class", "chart-grid-layer").attr("pointer-events", "none");
    var gd = 0;
    yS.ticks(5).forEach(function (t) {
      var yy = yS(t);
      var ln = gridG.append("line").attr("x1", margin.l).attr("x2", margin.l + iw).attr("y1", yy).attr("y2", yy)
        .attr("stroke", CHART_GRID_STROKE).attr("stroke-width", CHART_GRID_W);
      revealStrokeLine(ln, 480, gd);
      gd += 8;
    });
    var gAx = svg.append("g").attr("transform", "translate(0," + (margin.t + ih) + ")")
      .call(d3.axisBottom(xS))
      .call(function (gg) { gg.select(".domain").attr("stroke", CHART_AXIS_DOMAIN_STROKE); });
    gAx.selectAll("text").attr("fill", "#aaa").style("font-size", "8px")
      .attr("transform", "rotate(-18)").style("text-anchor", "end");
    top.forEach(function (d, i) {
      var x = xS(d.key);
      var y = yS(d.count);
      var y0 = yS(0);
      svg.append("line").attr("x1", x).attr("x2", x).attr("y1", y0).attr("y2", y0).attr("stroke", "rgba(255,255,255,0.45)").attr("stroke-width", 1)
        .transition().delay(200 + i * 40).duration(400).attr("y2", y);
    });
    svg.append("path").datum(top).attr("fill", "none").attr("stroke", PAL[0]).attr("stroke-width", 3)
      .attr("d", line).attr("opacity", 0)
      .transition().duration(900).attr("opacity", 1);
    top.forEach(function (d, i) {
      var x = xS(d.key);
      var y = yS(d.count);
      svg.append("circle").attr("cx", x).attr("cy", y).attr("r", 0).attr("fill", "#fff").attr("stroke", PAL[0]).attr("stroke-width", 2)
        .style("cursor", "pointer")
        .on("click", function () { setFilter(F.情绪, d.key); })
        .on("mouseenter", function (ev) { tipShow(ev, esc(String(d.key)) + "<br>" + d.count + " 条"); })
        .on("mousemove", moveTip).on("mouseleave", tipHide)
        .transition().delay(420 + i * 50).duration(320).attr("r", 7);
    });
    setFigCaptionLegend(container, top.map(function (d, i) { return { hex: PAL[i % 4], text: String(d.key).slice(0, 10) }; }),
      "样条曲线 + 垂线锚点 + 大白点（参考图2中）。点击筛情绪。\n" + captionSampleLine(rows));
  }

  function chartHBarPercentScene(container, rows) {
    var agg = aggregate(rows, F.场景).slice(0, 6);
    if (!agg.length) return;
    var maxC = d3.max(agg, function (d) { return d.count; }) || 1;
    var w = chartBoxW(container);
    var rowH = 36;
    var margin = { t: 24, l: 12, r: 160, b: 24 };
    var iw = w - margin.l - margin.r;
    var h = margin.t + agg.length * rowH + margin.b;
    var xS = d3.scaleLinear().domain([0, maxC]).range([0, iw]);
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    var defs = svg.append("defs");
    agg.forEach(function (d, i) {
      var yy = margin.t + i * rowH;
      var pct = Math.round(d.count / maxC * 100);
      var col = PAL[i % 4];
      var fillG = chartBarGradientUrl(defs, "s2hb_" + i, col);
      svg.append("rect").attr("x", margin.l).attr("y", yy + 6).attr("width", 0).attr("height", rowH - 14)
        .attr("fill", fillG).attr("rx", 2).style("cursor", "pointer")
        .on("click", function () { setFilter(F.场景, d.key); })
        .on("mouseenter", function (ev) { tipShow(ev, esc(String(d.key)) + "<br>" + d.count + " 条 · 相对最长条 " + pct + "%"); })
        .on("mousemove", moveTip).on("mouseleave", tipHide)
        .transition().duration(700).delay(i * 55).attr("width", Math.max(4, xS(d.count)));
      var lab = String(d.key).length > 14 ? String(d.key).slice(0, 13) + "…" : d.key;
      svg.append("text").attr("x", margin.l + iw + 8).attr("y", yy + rowH / 2 + 4).attr("fill", "#eee").style("font-size", "9px").text(lab);
      svg.append("circle").attr("cx", margin.l + iw + 118).attr("cy", yy + rowH / 2).attr("r", 5).attr("fill", col);
    });
    svg.append("text").attr("x", margin.l).attr("y", 14).attr("fill", "#888").style("font-size", "9px").text("0% — 相对最长场景为 100%（参考横向百分比条 + 右侧色点）");
    setFigCaptionLegend(container, agg.map(function (d, i) { return { hex: PAL[i % 4], text: String(d.key).slice(0, 12) }; }),
      "条形长度相对最大类归一；右侧点状图例。点击筛场景。\n" + captionSampleLine(rows));
  }

  function chartDualAreaBWSub(container, rows) {
    var order = ["动作模板化", "回复工具化", "聊天迁移"];
    var series = order.map(function (sub) {
      var slice = rows.filter(function (r) { return norm(r[F.细分]) === sub; });
      var bw = slice.filter(function (r) { return String(r[F.黑白]).indexOf("黑白") >= 0; }).length;
      var cl = slice.filter(function (r) { return String(r[F.黑白]).indexOf("彩") >= 0; }).length;
      var t = bw + cl || 1;
      return { sub: sub, bw: bw / t * 100, cl: cl / t * 100 };
    });
    var w = chartBoxW(container);
    var margin = { t: 36, r: 28, b: 52, l: 44 };
    var iw = w - margin.l - margin.r;
    var ih = 240;
    var h = margin.t + ih + margin.b;
    var xS = d3.scalePoint().domain(order).range([margin.l, margin.l + iw]).padding(0.35);
    var yS = d3.scaleLinear().domain([0, 100]).range([margin.t + ih, margin.t]);
    var band = xS.step();
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    order.forEach(function (sub, i) {
      var x = xS(sub) - band * 0.2;
      var ww = band * 0.4;
      svg.append("rect").attr("x", x).attr("y", margin.t).attr("width", ww).attr("height", ih)
        .attr("fill", i % 2 ? "rgba(108,88,238,0.12)" : "rgba(245,69,149,0.1)");
    });
    var areaBw = d3.area().x(function (d) { return xS(d.sub); }).y0(function (d) { return yS(d.bw); }).y1(function (d) { return yS(0); }).curve(d3.curveMonotoneX);
    var areaCl = d3.area().x(function (d) { return xS(d.sub); }).y0(function (d) { return yS(d.bw + d.cl); }).y1(function (d) { return yS(d.bw); }).curve(d3.curveMonotoneX);
    svg.append("path").datum(series).attr("fill", "rgba(89,226,253,0.35)").attr("stroke", PAL[1]).attr("stroke-width", 1.5)
      .attr("d", areaBw).attr("opacity", 0).transition().duration(800).attr("opacity", 1);
    svg.append("path").datum(series).attr("fill", "rgba(252,229,0,0.32)").attr("stroke", PAL[3]).attr("stroke-width", 1.5)
      .attr("d", areaCl).attr("opacity", 0).transition().duration(800).delay(200).attr("opacity", 1);
    var lineBw = d3.line().x(function (d) { return xS(d.sub); }).y(function (d) { return yS(d.bw); }).curve(d3.curveMonotoneX);
    var lineCl = d3.line().x(function (d) { return xS(d.sub); }).y(function (d) { return yS(d.bw + d.cl); }).curve(d3.curveMonotoneX);
    svg.append("path").datum(series).attr("fill", "none").attr("stroke", PAL[1]).attr("stroke-width", 2.2).attr("d", lineBw).attr("opacity", 0).transition().delay(400).duration(600).attr("opacity", 1);
    svg.append("path").datum(series).attr("fill", "none").attr("stroke", PAL[3]).attr("stroke-width", 2.2).attr("d", lineCl).attr("opacity", 0).transition().delay(500).duration(600).attr("opacity", 1);
    var gAx = svg.append("g").attr("transform", "translate(0," + (margin.t + ih) + ")")
      .call(d3.axisBottom(xS))
      .call(function (gg) { gg.select(".domain").attr("stroke", CHART_AXIS_DOMAIN_STROKE); });
    gAx.selectAll("text").attr("fill", "#bbb").style("font-size", "9px");
    svg.append("g").attr("transform", "translate(" + margin.l + ",0)").call(d3.axisLeft(yS).ticks(5).tickFormat(function (d) { return d + "%"; }))
      .call(function (gg) { gg.select(".domain").attr("stroke", CHART_AXIS_DOMAIN_STROKE); })
      .selectAll("text").attr("fill", "#999").style("font-size", "9px");
    setFigCaptionLegend(container, [{ hex: PAL[1], text: "青区：黑白占比" }, { hex: PAL[3], text: "黄区：彩色占比" }],
      "按细分阶段叠双色面积（参考图3上：阶段色带 + 双线趋势）。\n" + captionSampleLine(rows));
  }

  function chartPictoBarsAction(container, rows) {
    var agg = aggregate(rows, F.动作).slice(0, 6);
    if (!agg.length) return;
    var w = chartBoxW(container);
    var maxC = d3.max(agg, function (d) { return d.count; }) || 1;
    var margin = { t: 28, r: 20, b: 72, l: 36 };
    var iw = w - margin.l - margin.r;
    var ih = 260;
    var h = margin.t + ih + margin.b;
    var xS = d3.scaleBand().domain(agg.map(function (d) { return d.key; })).range([margin.l, margin.l + iw]).padding(0.28);
    var yS = d3.scaleLinear().domain([0, maxC]).range([margin.t + ih, margin.t]);
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    var defs = svg.append("defs");
    var glyphs = ["●", "■", "◆", "▲", "▼", "◇"];
    agg.forEach(function (d, i) {
      var x = xS(d.key);
      var bw = xS.bandwidth();
      var y1 = yS(d.count);
      var col = PAL[i % 4];
      var fillG = chartBarGradientUrl(defs, "s2pb_" + i, col);
      var cx = x + bw / 2;
      svg.append("line").attr("x1", cx).attr("x2", cx).attr("y1", margin.t - 6).attr("y2", margin.t)
        .attr("stroke", "rgba(255,255,255,0.35)").attr("stroke-dasharray", "2 3");
      svg.append("circle").attr("cx", cx).attr("cy", margin.t - 10).attr("r", 3).attr("fill", col);
      svg.append("rect").attr("x", x).attr("y", y1).attr("width", bw).attr("height", margin.t + ih - y1)
        .attr("fill", fillG).attr("stroke", "rgba(255,255,255,0.35)").attr("stroke-width", 1).style("cursor", "pointer")
        .on("click", function () { setFilter(F.动作, d.key); })
        .on("mouseenter", function (ev) { tipShow(ev, esc(String(d.key)) + "<br>" + d.count + " 条"); })
        .on("mousemove", moveTip).on("mouseleave", tipHide)
        .attr("opacity", 0).transition().delay(i * 80).duration(550).attr("opacity", 1);
      svg.append("text").attr("x", cx).attr("y", margin.t + ih + 42).attr("text-anchor", "middle")
        .attr("fill", "#ddd").style("font-size", "20px").style("font-family", "serif").text(glyphs[i % glyphs.length]);
      var lab = String(d.key).length > 8 ? String(d.key).slice(0, 7) + "…" : d.key;
      svg.append("text").attr("x", cx).attr("y", margin.t + ih + 58).attr("text-anchor", "middle")
        .attr("fill", "#999").style("font-size", "8px").text(lab);
    });
    setFigCaptionLegend(container, agg.map(function (d, i) { return { hex: PAL[i % 4], text: String(d.key).slice(0, 10) }; }),
      "象形柱 + 柱顶节点线 + 柱下符号（参考图3中）。\n" + captionSampleLine(rows));
  }

  function chartRidgePackBySub(container, rows) {
    var subs = ["动作模板化", "回复工具化", "聊天迁移"];
    var w = chartBoxW(container);
    var m = { t: 20, l: 100, r: 24, b: 40 };
    var iw = w - m.l - m.r;
    var laneH = 62;
    var h = m.t + subs.length * laneH + m.b;
    var packs = ["1", "2", "3", "4", "5"];
    var xS = d3.scaleBand().domain(packs).range([m.l, m.l + iw]).padding(0.15);
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    svg.append("text").attr("x", m.l + iw / 2).attr("y", 14).attr("text-anchor", "middle").attr("fill", "#888").style("font-size", "9px").text("包装度 1—5 · 各细分阶段分布脊线");
    subs.forEach(function (sub, ri) {
      var yy = m.t + ri * laneH;
      var slice = rows.filter(function (r) { return norm(r[F.细分]) === sub; });
      var counts = packs.map(function (p) {
        return slice.filter(function (r) { return String(r[F.包装]) === p; }).length;
      });
      var maxC = d3.max(counts) || 1;
      var y0 = yy + laneH - 8;
      var pts = counts.map(function (c, j) {
        var cx = xS(packs[j]) + xS.bandwidth() / 2;
        var amp = (c / maxC) * (laneH - 18);
        return [cx, y0 - amp];
      });
      var area = d3.area().x(function (d) { return d[0]; }).y0(y0).y1(function (d) { return d[1]; }).curve(d3.curveCatmullRom.alpha(0.5));
      svg.append("path").datum(pts).attr("fill", ri % 2 ? "rgba(245,69,149,0.25)" : "rgba(252,229,0,0.22)")
        .attr("stroke", PAL[ri % 4]).attr("stroke-width", 1.2).attr("d", area).attr("opacity", 0)
        .style("cursor", "pointer")
        .on("click", function () { setPhase(sub); })
        .transition().delay(ri * 120).duration(700).attr("opacity", 1);
      svg.append("text").attr("x", m.l - 8).attr("y", yy + laneH / 2).attr("text-anchor", "end").attr("fill", "#ccc").style("font-size", "9px")
        .text(sub.length > 6 ? sub.slice(0, 5) + "…" : sub);
      svg.append("line").attr("x1", m.l).attr("x2", m.l + iw).attr("y1", y0).attr("y2", y0)
        .attr("stroke", CHART_GRID_STROKE).attr("stroke-width", 0.65).attr("stroke-dasharray", "4 4");
    });
    var gAx = svg.append("g").attr("transform", "translate(0," + (h - m.b + 6) + ")")
      .call(d3.axisBottom(xS))
      .call(function (gg) { gg.select(".domain").attr("stroke", CHART_AXIS_DOMAIN_STROKE); });
    gAx.selectAll("text").attr("fill", "#999").style("font-size", "9px");
    setFigCaptionLegend(container, [{ hex: PAL[0], text: "脊线 / Joy：细分×包装" }],
      "三行=三阶段；峰=该包装度条数相对行内最大。点击填色区筛阶段。\n" + captionSampleLine(rows));
  }

  function chartConcentricSweepPack(container, rows) {
    var packs = ["5", "4", "3", "2", "1"];
    var tot = rows.length || 1;
    var counts = packs.map(function (p) { return rows.filter(function (r) { return String(r[F.包装]) === p; }).length; });
    if (!d3.sum(counts)) return;
    var w = chartBoxW(container);
    var cx = w / 2;
    var cy = 168;
    var r0 = 28;
    var ring = 22;
    var h = cy + r0 + packs.length * ring + 50;
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    var warm = ["#fce5a8", "#f4b76e", "#e8944a", "#d86a3a", "#c44536"];
    packs.forEach(function (p, i) {
      var ro = r0 + (packs.length - 1 - i) * ring;
      var ri2 = ro - ring + 4;
      var c = counts[i];
      var frac = c / tot;
      var col = warm[i % warm.length];
      var arcBg = d3.arc().innerRadius(ri2).outerRadius(ro).startAngle(0).endAngle(2 * Math.PI);
      var arcFg = d3.arc().innerRadius(ri2 + 2).outerRadius(ro - 2).startAngle(-Math.PI / 2).endAngle(-Math.PI / 2 + frac * 2 * Math.PI);
      var g = svg.append("g").attr("transform", "translate(" + cx + "," + cy + ")");
      g.append("path").attr("d", arcBg).attr("fill", col).attr("fill-opacity", 0.35).attr("stroke", "rgba(0,0,0,0.4)");
      g.append("path").attr("d", arcFg).attr("fill", "#0a0a10").attr("stroke", "none").attr("opacity", 0)
        .style("cursor", "pointer")
        .on("click", function () { setFilter(F.包装, p); })
        .on("mouseenter", function (ev) {
          tipShow(ev, "包装 " + p + " 级<br>" + c + " 条 · " + Math.round(frac * 100) + "%");
        })
        .on("mousemove", moveTip).on("mouseleave", tipHide)
        .transition().duration(900).delay(i * 100).attr("opacity", 0.92);
      var mid = -Math.PI / 2 + frac * Math.PI;
      var tx = cx + Math.cos(mid) * (ro + 14) + (Math.cos(mid) >= 0 ? 12 : -12);
      var ly = cy + Math.sin(mid) * (ro + 14);
      svg.append("line").attr("x1", cx + Math.cos(mid) * ro).attr("y1", cy + Math.sin(mid) * ro).attr("x2", tx).attr("y2", ly)
        .attr("stroke", "rgba(255,255,255,0.4)").attr("stroke-width", 0.8).attr("opacity", 0)
        .transition().delay(400 + i * 100).duration(400).attr("opacity", 1);
      svg.append("text").attr("x", tx + (Math.cos(mid) >= 0 ? 4 : -4)).attr("y", ly + 3)
        .attr("text-anchor", Math.cos(mid) >= 0 ? "start" : "end").attr("fill", "#eee").style("font-size", "9px").attr("opacity", 0)
        .text("包" + p + " · " + Math.round(frac * 100) + "%")
        .transition().delay(480 + i * 100).duration(350).attr("opacity", 1);
    });
    svg.append("circle").attr("cx", cx).attr("cy", cy).attr("r", r0 - 4).attr("fill", "rgba(8,8,12,0.95)").attr("stroke", warm[0]);
    setFigCaptionLegend(container, packs.map(function (p, i) { return { hex: warm[i], text: "包装 " + p }; }),
      "同心温色环 + 深色扫角 + 外引线（参考图4）。由内到外包装度 1→5。\n" + captionSampleLine(rows));
  }

  function chartChordLiteOrigPack(container, rows) {
    var L = aggregate(rows, F.原情).slice(0, 5);
    var Rgt = aggregate(rows, F.包后).slice(0, 5);
    if (!L.length || !Rgt.length) return;
    var flowMap = new Map();
    rows.forEach(function (r) {
      var a = norm(r[F.原情]);
      var b = norm(r[F.包后]);
      var k = a + "\t" + b;
      flowMap.set(k, (flowMap.get(k) || 0) + 1);
    });
    var w = chartBoxW(container);
    var h = 380;
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    var leftX = 56;
    var rightX = w - 56;
    var yL = d3.scalePoint().domain(L.map(function (d) { return d.key; })).range([48, h - 48]).padding(0.55);
    var yR = d3.scalePoint().domain(Rgt.map(function (d) { return d.key; })).range([48, h - 48]).padding(0.55);
    L.forEach(function (d, i) {
      svg.append("circle").attr("cx", leftX).attr("cy", yL(d.key)).attr("r", 5).attr("fill", PAL[i % 4]);
      svg.append("text").attr("x", leftX - 10).attr("y", yL(d.key) + 3).attr("text-anchor", "end").attr("fill", "#ccc").style("font-size", "8px")
        .text(String(d.key).length > 10 ? String(d.key).slice(0, 9) + "…" : d.key);
    });
    Rgt.forEach(function (d, i) {
      svg.append("circle").attr("cx", rightX).attr("cy", yR(d.key)).attr("r", 5).attr("fill", PAL[(i + 2) % 4]);
      svg.append("text").attr("x", rightX + 10).attr("y", yR(d.key) + 3).attr("text-anchor", "start").attr("fill", "#ccc").style("font-size", "8px")
        .text(String(d.key).length > 10 ? String(d.key).slice(0, 9) + "…" : d.key);
    });
    var maxF = 0;
    flowMap.forEach(function (v) { if (v > maxF) maxF = v; });
    var fi = 0;
    flowMap.forEach(function (cnt, k) {
      var parts = k.split("\t");
      var a = parts[0];
      var b = parts[1];
      if (yL(a) == null || yR(b) == null) return;
      var sw = 1.5 + (cnt / (maxF || 1)) * 10;
      var path = "M" + leftX + "," + yL(a) + " C" + (leftX + (rightX - leftX) * 0.45) + "," + yL(a) + " " +
        (rightX - (rightX - leftX) * 0.45) + "," + yR(b) + " " + rightX + "," + yR(b);
      svg.append("path").attr("d", path).attr("fill", "none").attr("stroke", PAL[fi % 4]).attr("stroke-opacity", 0.55)
        .attr("stroke-width", sw).attr("opacity", 0).style("cursor", "pointer")
        .on("mouseenter", function (ev) { tipShow(ev, esc(a) + " → " + esc(b) + "<br>" + cnt + " 条"); })
        .on("mousemove", moveTip).on("mouseleave", tipHide)
        .on("click", function () { setFilter(F.原情, a); setFilter(F.包后, b); })
        .transition().delay(fi * 25).duration(500).attr("opacity", 1);
      fi++;
    });
    setFigCaptionLegend(container, [{ hex: PAL[0], text: "左：原始情绪 Top5" }, { hex: PAL[2], text: "右：包装后 Top5" }],
      "弦式贝塞尔带：线粗=路径条数；悬停看配对。点击同时筛原情与包后。\n" + captionSampleLine(rows));
  }

  function chartMatrixBubbleDirectPack(container, rows) {
    var dirs = aggregate(rows, F.直接).map(function (d) { return d.key; }).slice(0, 4);
    var packs = ["1", "2", "3", "4", "5"];
    if (!dirs.length) return;
    var w = chartBoxW(container);
    var m = { t: 36, l: 88, r: 24, b: 48 };
    var cellW = (w - m.l - m.r) / packs.length;
    var cellH = 44;
    var h = m.t + dirs.length * cellH + m.b;
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    packs.forEach(function (p, j) {
      svg.append("text").attr("x", m.l + j * cellW + cellW / 2).attr("y", m.t - 8).attr("text-anchor", "middle").attr("fill", "#999").style("font-size", "9px").text("包" + p);
    });
    dirs.forEach(function (dir, i) {
      svg.append("text").attr("x", m.l - 6).attr("y", m.t + i * cellH + cellH / 2 + 3).attr("text-anchor", "end").attr("fill", "#bbb").style("font-size", "8px")
        .text(String(dir).length > 8 ? String(dir).slice(0, 7) + "…" : dir);
      packs.forEach(function (p, j) {
        var slice = rows.filter(function (r) { return norm(r[F.直接]) === norm(dir) && String(r[F.包装]) === p; });
        var n = slice.length;
        if (!n) return;
        var dom = aggregate(slice, F.情绪)[0];
        var ei = dirs.length * j + i;
        var col = PAL[ei % 4];
        var cx = m.l + j * cellW + cellW / 2;
        var cy = m.t + i * cellH + cellH / 2;
        var rad = 6 + Math.sqrt(n) * 3.2;
        var href = slice[0] ? (thumb(slice[0]) || IMG_PLACEHOLDER) : IMG_PLACEHOLDER;
        svg.append("circle").attr("cx", cx).attr("cy", cy).attr("r", 0).attr("fill", col).attr("fill-opacity", 0.75).attr("stroke", "#fff").attr("stroke-width", 1.2)
          .style("cursor", "pointer")
          .on("click", function () { setFilter(F.直接, dir); setFilter(F.包装, p); })
          .on("mouseenter", function (ev) {
            var t = esc(String(dom ? dom.key : "")) + "<br>" + n + " 条";
            tipShow(ev, (href !== IMG_PLACEHOLDER ? "<img src=\"" + esc(href) + "\" alt=\"\">" : "") + t);
          })
          .on("mousemove", moveTip).on("mouseleave", tipHide)
          .transition().duration(400).delay((i * packs.length + j) * 18).attr("r", Math.min(rad, cellW * 0.38));
      });
    });
    setFigCaptionLegend(container, [{ hex: PAL[0], text: "矩阵：直接性×包装" }],
      "气泡大小=交叉条数；悬停主情绪+缩略图。\n" + captionSampleLine(rows));
  }

  function renderCharts() {
    const host = document.getElementById("charts");
    if (!host) return;

    var stepperPre = document.getElementById("chart-stepper");
    if (stepperPre) {
      stepperPre.innerHTML = "";
      stepperPre.classList.remove("visible");
      delete stepperPre.dataset.built;
    }
    host.classList.remove("charts--stepper-open", "charts--narr-open");
    host.innerHTML = "";

    let narrIdx = 0;

    function addPanel(title, hint, renderFn, stepLabelEn) {
      const sec = document.createElement("section");
      sec.setAttribute("data-narr-idx", String(narrIdx));
      sec.setAttribute("data-step-label-en", stepLabelEn || "");
      sec.className = "panel chart-panel chart-panel-split chart-snap-page " + (narrIdx % 2 === 0 ? "z-left" : "z-right");
      const idx = narrIdx;
      narrIdx++;

      const stickyH = document.createElement("div");
      stickyH.className = "chart-sticky-header";
      stickyH.innerHTML =
        '<span class="chart-sticky-num">0' +
        (idx + 1) +
        ' /</span><span class="chart-sticky-title">' +
        esc(title) +
        "</span>";
      sec.appendChild(stickyH);

      const vis = document.createElement("div");
      vis.className = "chart-visual-centered";
      const h3 = document.createElement("h3");
      h3.textContent = title;
      vis.appendChild(h3);
      const subt = document.createElement("p");
      subt.className = "subt";
      subt.textContent = hint;
      vis.appendChild(subt);

      const row = document.createElement("div");
      row.className = "chart-row";
      const main = document.createElement("div");
      main.className = "chart-row-main";
      const ch = document.createElement("div");
      ch.className = "chart-host";
      const cap = document.createElement("aside");
      cap.className = "chart-figure-caption";
      main.appendChild(ch);
      row.appendChild(main);
      row.appendChild(cap);
      vis.appendChild(row);
      sec.appendChild(vis);
      host.appendChild(sec);

      attachChartOnView(sec, ch, renderFn);

      requestAnimationFrame(function () {
        const h3e = vis.querySelector("h3");
        const ste = vis.querySelector(".subt");
        if (h3e) {
          const t = h3e.textContent;
          h3e.textContent = "";
          pixelRevealPlainText(h3e, t, 0);
        }
        if (ste) {
          const t2 = ste.textContent;
          ste.textContent = "";
          pixelRevealPlainText(ste, t2, 0.04);
        }
      });
    }

    addPanel(
      "细分阶段 · 环形引线图",
      "外引文字+折线标注占比；点击扇区筛选细分阶段。",
      function (box) { chartDonutLeadersSub(box, rowsMarg(F.细分)); },
      "Donut leaders"
    );
    addPanel(
      "视觉复杂度 · 放射闭合线",
      "五轴极坐标折线围成面；半径为各级条数。",
      function (box) { chartPolarSpikeComplexity(box, rowsMarg(F.复杂度)); },
      "Polar burst"
    );
    addPanel(
      "细分 × 包装 × 字数（气泡带）",
      "三行阶段、横轴包装、圆面积≈字数、颜色=情绪。",
      function (box) { chartBeeswarmSubPackWc(box, rowsExact()); },
      "Beeswarm strip"
    );
    addPanel(
      "情绪 · 样条与垂线锚点",
      "平滑曲线连接 Top 情绪；白点+下垂线。",
      function (box) { chartSplineDropEmotion(box, rowsExact()); },
      "Spline drops"
    );
    addPanel(
      "社交场景 · 横向百分比条",
      "相对最长类为 100%；右侧色点图例。",
      function (box) { chartHBarPercentScene(box, rowsMarg(F.场景)); },
      "H-bar %"
    );
    addPanel(
      "黑白/彩色 · 双面积（按阶段）",
      "三列细分阶段；青黄叠层面积看彩图渗透。",
      function (box) { chartDualAreaBWSub(box, rowsExact()); },
      "Dual area BW"
    );
    addPanel(
      "动作特征 · 象形柱",
      "竖柱 + 柱顶节点线 + 柱下符号块。",
      function (box) { chartPictoBarsAction(box, rowsMarg(F.动作)); },
      "Picto bars"
    );
    addPanel(
      "包装度 · 脊线（按细分）",
      "三行 Joy/ridge；横轴包装 1—5。",
      function (box) { chartRidgePackBySub(box, rowsExact()); },
      "Ridge pack"
    );
    addPanel(
      "包装度 · 同心扫角环",
      "温色环轨 + 深色弧长 = 占比；引线读数。",
      function (box) { chartConcentricSweepPack(box, rowsExact()); },
      "Ring sweep"
    );
    addPanel(
      "原始情绪 → 包装后（弦带）",
      "贝塞尔粗线表示路径流量；悬停看配对。",
      function (box) { chartChordLiteOrigPack(box, rowsExact()); },
      "Chord-lite"
    );
    addPanel(
      "表达直接性 × 包装（矩阵气泡）",
      "离散格点交叉；气泡大小=条数，悬停主情绪与图。",
      function (box) { chartMatrixBubbleDirectPack(box, rowsExact()); },
      "Matrix bubble"
    );

    var stepper = document.getElementById("chart-stepper");
    if (stepper && !stepper.dataset.built) {
      stepper.dataset.built = "1";
      stepper.innerHTML = "";
      var panelList = [].slice.call(document.querySelectorAll(".chart-panel-split"));
      panelList.forEach(function (p, i) {
        var row = document.createElement("div");
        row.className = "stepper-item";
        var lab = document.createElement("span");
        lab.className = "stepper-label";
        lab.setAttribute("lang", "en");
        lab.textContent = p.getAttribute("data-step-label-en") || "Chart " + (i + 1);
        var dot = document.createElement("button");
        dot.type = "button";
        dot.className = "stepper-dot";
        var en = p.getAttribute("data-step-label-en") || "";
        dot.setAttribute("aria-label", "Chart " + (i + 1) + (en ? ": " + en : ""));
        dot.setAttribute("data-step-idx", String(i));
        dot.addEventListener("click", function () {
          p.scrollIntoView({ behavior: "smooth", block: "center" });
        });
        row.appendChild(dot);
        row.appendChild(lab);
        stepper.appendChild(row);
      });
    }

    setupChartNarrativeLayer();
  }
'''

if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    (root / "scene2_charts_code.js").write_text(JS.strip() + "\n", encoding="utf-8")
    print("wrote", root / "scene2_charts_code.js", "chars", len(JS))
