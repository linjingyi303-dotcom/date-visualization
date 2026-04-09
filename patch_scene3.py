# -*- coding: utf-8 -*-
import re
from pathlib import Path

ROOT = Path(r"c:\Users\林靖怡\Desktop\数据可视化")
html_path = ROOT / "场景三.html"

NEW_CHARTS = r'''
  function s3DonutDirectness(container, rows) {
    var agg = aggregate(rows, F.直接).filter(function (d) { return d.count > 0; });
    if (!agg.length) return;
    var w = chartBoxW(container);
    var h = 360;
    var cx = w / 2;
    var cy = h / 2;
    var ir = 62;
    var or = 118;
    var pie = d3.pie().value(function (d) { return d.count; }).sort(null);
    var arc = d3.arc().innerRadius(ir).outerRadius(or).cornerRadius(3);
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    var g = svg.append("g").attr("transform", "translate(" + cx + "," + cy + ")");
    var tot = d3.sum(agg, function (d) { return d.count; }) || 1;
    var arcs = g.selectAll("path").data(pie(agg)).enter().append("path")
      .attr("fill", function (d, i) { return PAL[i % 4]; })
      .attr("stroke", "#0a0a10")
      .attr("stroke-width", 2)
      .style("cursor", "pointer")
      .each(function (d) { this._current = { startAngle: d.startAngle, endAngle: d.startAngle }; })
      .on("click", function (_, d) { setFilter(F.直接, d.data.key); })
      .on("mouseenter", function (ev, d) {
        tipShow(ev, esc(String(d.data.key)) + "<br>" + d.data.count + " 条 · " + ((d.data.count / tot) * 100).toFixed(1) + "%");
      })
      .on("mousemove", moveTip).on("mouseleave", tipHide);
    runWhenChartSvgVisible(container, function () {
      arcs.transition().duration(900).ease(d3.easeCubicOut).attrTween("d", function (d) {
        var i = d3.interpolate(this._current, d);
        this._current = i(0);
        return function (t) { return arc(i(t)); };
      });
    });
    g.append("text").attr("text-anchor", "middle").attr("dy", "-0.15em").attr("fill", "#ddd").style("font-size", "11px").text("表达直接性");
    g.append("text").attr("text-anchor", "middle").attr("dy", "1em").attr("fill", "#888").style("font-size", "8px").text("n=" + rows.length);
    setFigCaptionLegend(container, agg.map(function (d, i) { return { hex: PAL[i % 4], text: String(d.key).slice(0, 14) }; }),
      "环形图：角向比例=条数占比；与场景二矩阵/弦图不同，单维直接性结构。\n" + captionSampleLine(rows));
  }

  function s3HBarSubCounts(container, rows) {
    var agg = aggregate(rows, F.细分).filter(function (d) { return d.count > 0; })
      .sort(function (a, b) { return b.count - a.count; });
    if (!agg.length) return;
    var w = chartBoxW(container);
    var m = { t: 28, r: 120, b: 48, l: 168 };
    var iw = w - m.l - m.r;
    var rowH = 34;
    var h = m.t + agg.length * rowH + m.b;
    var maxC = d3.max(agg, function (d) { return d.count; }) || 1;
    var xS = d3.scaleLinear().domain([0, maxC]).nice().range([0, iw]);
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    agg.forEach(function (d, i) {
      var yy = m.t + i * rowH;
      svg.append("text").attr("x", m.l - 8).attr("y", yy + rowH / 2 + 4).attr("text-anchor", "end")
        .attr("fill", "#bbb").style("font-size", "8px")
        .text(String(d.key).length > 10 ? String(d.key).slice(0, 9) + "…" : d.key);
      var bw = 0;
      var rect = svg.append("rect").attr("x", m.l).attr("y", yy + 6).attr("height", rowH - 12).attr("width", bw)
        .attr("fill", chartBarGradientUrl(svg.append("defs"), "s3h_" + i, PAL[i % 4]))
        .attr("stroke", PAL[i % 4]).attr("stroke-width", 1.2).style("cursor", "pointer")
        .on("click", function () { setPhase(d.key); })
        .on("mouseenter", function (ev) { tipShow(ev, esc(String(d.key)) + "<br>" + d.count + " 条"); })
        .on("mousemove", moveTip).on("mouseleave", tipHide);
      svg.append("text").attr("x", m.l + iw + 6).attr("y", yy + rowH / 2 + 4).attr("fill", "#aaa").style("font-size", "9px").text(d.count);
      runWhenChartSvgVisible(container, function () {
        rect.transition().delay(i * 70).duration(720).ease(d3.easeCubicOut).attr("width", xS(d.count));
      });
    });
    var gAx = svg.append("g").attr("transform", "translate(" + m.l + "," + (h - m.b + 8) + ")").call(d3.axisBottom(xS).ticks(6).tickFormat(d3.format("d")))
      .call(function (gg) { gg.select(".domain").attr("stroke", CHART_AXIS_DOMAIN_STROKE); });
    gAx.selectAll("text").attr("fill", "#888").style("font-size", "8px");
    s2AxisTitleX(svg, m.l + iw / 2, h - 6, "横轴：该细分阶段条数（绝对值）");
    setFigCaptionLegend(container, [{ hex: PAL[0], text: "横向条形图" }],
      "水平条形：每行一类细分阶段，长度=条数；非缩略图矩阵、非脊线。\n" + captionSampleLine(rows));
  }

  function s3HeatmapOrigToPack(container, rows) {
    var origs = aggregate(rows, F.原情).slice(0, 7).map(function (d) { return d.key; });
    var packs = aggregate(rows, F.包后).slice(0, 7).map(function (d) { return d.key; });
    if (!origs.length || !packs.length) return;
    var map = {};
    rows.forEach(function (r) {
      var o = norm(r[F.原情]);
      var p = norm(r[F.包后]);
      if (origs.indexOf(o) < 0 || packs.indexOf(p) < 0) return;
      var k = o + "\t" + p;
      map[k] = (map[k] || 0) + 1;
    });
    var maxV = d3.max(Object.values(map)) || 1;
    var col = d3.scaleSequential(d3.interpolateRgb("#0a1628", "#59E2FD")).domain([0, maxV]);
    var w = chartBoxW(container);
    var m = { t: 52, l: 138, r: 24, b: 56 };
    var cw = (w - m.l - m.r) / packs.length;
    var ch = 36;
    var h = m.t + origs.length * ch + m.b;
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    packs.forEach(function (p, j) {
      svg.append("text").attr("x", m.l + j * cw + cw / 2).attr("y", m.t - 8).attr("text-anchor", "middle")
        .attr("fill", "#999").style("font-size", "7px").text(String(p).length > 5 ? String(p).slice(0, 4) + "…" : p);
    });
    origs.forEach(function (o, i) {
      svg.append("text").attr("x", m.l - 6).attr("y", m.t + i * ch + ch / 2 + 3).attr("text-anchor", "end")
        .attr("fill", "#ccc").style("font-size", "7px")
        .text(String(o).length > 8 ? String(o).slice(0, 7) + "…" : o);
      packs.forEach(function (p, j) {
        var v = map[o + "\t" + p] || 0;
        var cell = svg.append("rect")
          .attr("x", m.l + j * cw + 2).attr("y", m.t + i * ch + 2).attr("width", cw - 4).attr("height", ch - 4)
          .attr("fill", v ? col(v) : "rgba(20,20,28,0.5)").attr("stroke", "rgba(255,255,255,0.12)").attr("stroke-width", 0.6)
          .style("cursor", "pointer")
          .attr("opacity", 0)
          .on("click", function () { setFilter(F.原情, o); setFilter(F.包后, p); })
          .on("mouseenter", function (ev) { tipShow(ev, esc(o) + " → " + esc(p) + "<br>n=" + v); })
          .on("mousemove", moveTip).on("mouseleave", tipHide);
        runWhenChartSvgVisible(container, function () {
          cell.transition().delay((i * packs.length + j) * 28).duration(380).attr("opacity", 1);
        });
      });
    });
    s2AxisTitleX(svg, m.l + (packs.length * cw) / 2, h - 8, "列：包装后表达（Top）");
    s2AxisTitleY(svg, 14, m.t + (origs.length * ch) / 2, "行：原始情绪（Top）");
    setFigCaptionLegend(container, [{ hex: "#59E2FD", text: "色深∝交叉条数" }],
      "热力格：原情绪×包装后交叉计数；非弦带、非气泡矩阵。\n" + captionSampleLine(rows));
  }

  function s3JitterPackVsReal(container, rows) {
    var w = chartBoxW(container);
    var m = { t: 36, r: 52, b: 52, l: 52 };
    var iw = w - m.l - m.r;
    var ih = 280;
    var h = m.t + ih + m.b;
    var packs = ["1", "2", "3", "4", "5"];
    var xS = d3.scaleBand().domain(packs).range([m.l, m.l + iw]).padding(0.22);
    var ys = rows.map(function (r) { return +r[F.真实]; }).filter(function (v) { return !isNaN(v); });
    var yMin = ys.length ? d3.min(ys) : 0;
    var yMax = ys.length ? d3.max(ys) : 100;
    var yS = d3.scaleLinear().domain([yMin, yMax]).nice().range([m.t + ih, m.t]);
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    var seed = function (i) { return (Math.sin(i * 12.9898) * 43758.5453) % 1; };
    var pts = [];
    rows.forEach(function (r, idx) {
      var pk = String(r[F.包装]);
      if (packs.indexOf(pk) < 0) return;
      var yv = +r[F.真实];
      if (isNaN(yv)) return;
      var cx0 = xS(pk) + xS.bandwidth() / 2;
      var jitter = (seed(idx) - 0.5) * xS.bandwidth() * 0.72;
      var col = String(r[F.黑白]).indexOf("彩") >= 0 ? PAL[1] : "#aaa";
      pts.push({ x: cx0 + jitter, y: yS(yv), col: col, r: r, idx: idx });
    });
    var meanByPack = {};
    packs.forEach(function (p) {
      var slice = rows.filter(function (r) { return String(r[F.包装]) === p; });
      var vals = slice.map(function (r) { return +r[F.真实]; }).filter(function (v) { return !isNaN(v); });
      meanByPack[p] = vals.length ? d3.mean(vals) : null;
    });
    pts.forEach(function (d, i) {
      svg.append("circle").attr("cx", d.x).attr("cy", d.y).attr("r", 0).attr("fill", d.col).attr("stroke", "#111").attr("stroke-width", 0.6)
        .style("cursor", "pointer")
        .on("click", function () { setFilter(F.包装, String(d.r[F.包装])); })
        .on("mouseenter", function (ev) {
          tipShow(ev, "包装" + d.r[F.包装] + " · 真实度 " + d.r[F.真实] + "<br>" + esc(norm(d.r[F.图字]).slice(0, 40)));
        })
        .on("mousemove", moveTip).on("mouseleave", tipHide);
      runWhenChartSvgVisible(container, function () {
        d3.select(svg.node().querySelectorAll("circle")[i]).transition().delay(i % 40 * 12).duration(420).ease(d3.easeBackOut.overshoot(1.05)).attr("r", 4.2);
      });
    });
    packs.forEach(function (p) {
      var my = meanByPack[p];
      if (my == null) return;
      var xc = xS(p) + xS.bandwidth() / 2;
      svg.append("line").attr("x1", xS(p) + 4).attr("x2", xS(p) + xS.bandwidth() - 4).attr("y1", yS(my)).attr("y2", yS(my))
        .attr("stroke", PAL[2]).attr("stroke-width", 2).attr("stroke-dasharray", "4 3").attr("opacity", 0.85);
    });
    var gAx = svg.append("g").attr("transform", "translate(0," + (m.t + ih) + ")").call(d3.axisBottom(xS))
      .call(function (gg) { gg.select(".domain").attr("stroke", CHART_AXIS_DOMAIN_STROKE); });
    gAx.selectAll("text").attr("fill", "#aaa").style("font-size", "9px");
    var gAy = svg.append("g").attr("transform", "translate(" + m.l + ",0)").call(d3.axisLeft(yS).ticks(6))
      .call(function (gg) { gg.select(".domain").attr("stroke", CHART_AXIS_DOMAIN_STROKE); });
    gAy.selectAll("text").attr("fill", "#888").style("font-size", "8px");
    s2AxisTitleX(svg, m.l + iw / 2, h - 8, "横轴：包装程度（1—5）");
    s2AxisTitleY(svg, 18, m.t + ih / 2, "纵轴：贴近真实情绪指数");
    setFigCaptionLegend(container, [{ hex: PAL[1], text: "彩=彩色图" }, { hex: "#aaa", text: "灰=黑白" }, { hex: PAL[2], text: "紫虚线=该档均值" }],
      "带抖动的散点：每点一条样本；紫虚线为各包装档均值。\n" + captionSampleLine(rows));
  }

  function s3TreemapSocialFn(container, rows) {
    var agg = aggregate(rows, F.社功).filter(function (d) { return d.count > 0; });
    if (!agg.length) return;
    var w = chartBoxW(container);
    var h = 340;
    var root = d3.hierarchy({ name: "root", children: agg.map(function (d) { return { name: d.key, value: d.count }; }) })
      .sum(function (d) { return d.value || 0; });
    d3.treemap().size([w - 24, h - 36]).paddingOuter(4).paddingInner(2).round(true)(root);
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    var leaves = root.leaves();
    var g = svg.append("g").attr("transform", "translate(12,18)");
    var cells = g.selectAll("g").data(leaves).enter().append("g").attr("transform", function (d) { return "translate(" + d.x0 + "," + d.y0 + ")"; });
    cells.append("rect").attr("width", function (d) { return Math.max(0, d.x1 - d.x0); }).attr("height", function (d) { return Math.max(0, d.y1 - d.y0); })
      .attr("fill", function (d, i) { return PAL[i % 4]; }).attr("fill-opacity", 0.45).attr("stroke", "rgba(255,255,255,0.25)").attr("stroke-width", 1)
      .style("cursor", "pointer")
      .attr("opacity", 0)
      .on("click", function (_, d) { setFilter(F.社功, d.data.name); })
      .on("mouseenter", function (ev, d) { tipShow(ev, esc(String(d.data.name)) + "<br>" + d.value + " 条"); })
      .on("mousemove", moveTip).on("mouseleave", tipHide);
    cells.filter(function (d) { return d.x1 - d.x0 > 56 && d.y1 - d.y0 > 22; }).append("text")
      .attr("x", 4).attr("y", 14).attr("fill", "#eee").style("font-size", "7px")
      .text(function (d) {
        var s = String(d.data.name);
        return s.length > 10 ? s.slice(0, 9) + "…" : s;
      });
    runWhenChartSvgVisible(container, function () {
      cells.select("rect").transition().delay(function (_, i) { return i * 40; }).duration(500).attr("opacity", 1);
    });
    svg.append("text").attr("x", w / 2).attr("y", 14).attr("text-anchor", "middle").attr("fill", "#999").style("font-size", "8px").text("矩形面积 ∝ 条数 · 社交功能分类");
    setFigCaptionLegend(container, agg.slice(0, 6).map(function (d, i) { return { hex: PAL[i % 4], text: String(d.key).slice(0, 12) }; }),
      "树状分割（treemap）：与玫瑰图、条形图几何不同。\n" + captionSampleLine(rows));
  }

  function s3StackedRiskByRelation(container, rows) {
    var rels = aggregate(rows, F.关系).filter(function (d) { return d.count > 0; }).sort(function (a, b) { return b.count - a.count; }).slice(0, 6);
    if (!rels.length) return;
    var risks = ["低", "中", "高"];
    var riskCol = { 低: PAL[1], 中: PAL[2], 高: PAL[0] };
    var w = chartBoxW(container);
    var m = { t: 32, r: 28, b: 56, l: 168 };
    var rowH = 40;
    var h = m.t + rels.length * rowH + m.b;
    var iw = w - m.l - m.r;
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    rels.forEach(function (rd, ri) {
      var yy = m.t + ri * rowH;
      var slice = rows.filter(function (r) { return norm(r[F.关系]) === norm(rd.key); });
      var cLow = slice.filter(function (r) { return norm(r[F.风险]).indexOf("低") >= 0; }).length;
      var cMid = slice.filter(function (r) { return norm(r[F.风险]).indexOf("中") >= 0; }).length;
      var cHi = slice.filter(function (r) { return norm(r[F.风险]).indexOf("高") >= 0; }).length;
      var tot = cLow + cMid + cHi || 1;
      svg.append("text").attr("x", m.l - 8).attr("y", yy + rowH / 2 + 4).attr("text-anchor", "end").attr("fill", "#bbb").style("font-size", "7.5px")
        .text(String(rd.key).length > 12 ? String(rd.key).slice(0, 11) + "…" : rd.key);
      var x0 = m.l;
      var stack = [
        { k: "低", n: cLow, c: riskCol.低 },
        { k: "中", n: cMid, c: riskCol.中 },
        { k: "高", n: cHi, c: riskCol.高 }
      ];
      stack.forEach(function (seg, si) {
        var ww = (seg.n / tot) * iw;
        var r = svg.append("rect").attr("x", x0).attr("y", yy + 6).attr("height", rowH - 14).attr("width", 0)
          .attr("fill", seg.c).attr("fill-opacity", 0.55).attr("stroke", seg.c).attr("stroke-width", 1)
          .style("cursor", "pointer")
          .on("click", function () { setFilter(F.关系, rd.key); setFilter(F.风险, seg.k); })
          .on("mouseenter", function (ev) { tipShow(ev, esc(rd.key) + " · 风险" + seg.k + "<br>" + seg.n + " 条"); })
          .on("mousemove", moveTip).on("mouseleave", tipHide);
        runWhenChartSvgVisible(container, function () {
          r.transition().delay(ri * 100 + si * 80).duration(650).ease(d3.easeCubicOut).attr("width", ww);
        });
        x0 += ww;
      });
    });
    var lx = m.l;
    risks.forEach(function (rk) {
      svg.append("rect").attr("x", lx).attr("y", 8).attr("width", 10).attr("height", 10).attr("fill", riskCol[rk]).attr("opacity", 0.7);
      svg.append("text").attr("x", lx + 14).attr("y", 17).attr("fill", "#888").style("font-size", "7px").text("风险" + rk);
      lx += 52;
    });
    s2AxisTitleX(svg, m.l + iw / 2, h - 10, "每行：该关系对象下 低/中/高 风险占比（100% 堆叠）");
    setFigCaptionLegend(container, [{ hex: PAL[1], text: "低" }, { hex: PAL[2], text: "中" }, { hex: PAL[0], text: "高" }],
      "堆叠比例条：关系对象×风险；非单列柱、非弦图。\n" + captionSampleLine(rows));
  }

  function s3WafflePackTier(container, rows) {
    var low = rows.filter(function (r) { var p = +r[F.包装]; return !isNaN(p) && p <= 2; }).length;
    var mid = rows.filter(function (r) { var p = +r[F.包装]; return p === 3; }).length;
    var hi = rows.filter(function (r) { var p = +r[F.包装]; return !isNaN(p) && p >= 4; }).length;
    var tot = low + mid + hi || 1;
    var w = chartBoxW(container);
    var cols = 20;
    var cell = 14;
    var gap = 2;
    var rowsW = 10;
    var h = 48 + rowsW * (cell + gap) + 40;
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    var nLow = Math.round((low / tot) * (cols * rowsW));
    var nMid = Math.round((mid / tot) * (cols * rowsW));
    var nHi = cols * rowsW - nLow - nMid;
    var seq = [];
    var i;
    for (i = 0; i < nLow; i++) seq.push(PAL[1]);
    for (i = 0; i < nMid; i++) seq.push(PAL[2]);
    for (i = 0; i < nHi; i++) seq.push(PAL[0]);
    var g = svg.append("g").attr("transform", "translate(" + ((w - cols * (cell + gap)) / 2) + ",40)");
    seq.forEach(function (col, j) {
      var cx = (j % cols) * (cell + gap);
      var cy = Math.floor(j / cols) * (cell + gap);
      g.append("rect").attr("x", cx).attr("y", cy).attr("width", cell).attr("height", cell).attr("fill", col).attr("stroke", "#111").attr("stroke-width", 0.5)
        .attr("opacity", 0);
    });
    svg.append("text").attr("x", w / 2).attr("y", 22).attr("text-anchor", "middle").attr("fill", "#999").style("font-size", "8px")
      .text("华夫饼：低包装(1—2) · 中(3) · 高(4—5) 占比（近似格数）");
    runWhenChartSvgVisible(container, function () {
      g.selectAll("rect").transition().delay(function (_, i) { return i * 6; }).duration(220).attr("opacity", 0.92);
    });
    setFigCaptionLegend(container,
      [{ hex: PAL[1], text: "低包装 1—2：" + low + " 条" }, { hex: PAL[2], text: "中(3)：" + mid + " 条" }, { hex: PAL[0], text: "高 4—5：" + hi + " 条" }],
      "10×20 华夫格近似三类包装占比；与柱/环/热力均不重复。\n" + captionSampleLine(rows));
  }
'''

NARR = '''  const CHART_NARRATIVE_TEXTS = [
    "【数据总结·表达直接性】\\n间接表达占绝大多数，熊猫头常用「表情代说」降低当面冲突感。\\n\\n【对应本图】\\n环形图仅看「表达直接性」单一维度占比，点击扇区可筛。",
    "【数据总结·细分阶段】\\n各细分阶段样本量不同，可观察哪一阶段表情包更集中。\\n\\n【对应本图】\\n水平条形图按条数排序，点击条形筛该细分阶段。",
    "【数据总结·包装链】\\n原始情绪与包装后表达存在稳定迁移模式（如向轻吐槽、阴阳等收敛）。\\n\\n【对应本图】\\n热力格为原情绪×包装后交叉计数，点击格双筛。",
    "【数据总结·真实度指数】\\n贴近真实情绪程度指数分布可反映「包一层之后离真心有多远」。\\n\\n【对应本图】\\n散点+抖动：横轴包装度，纵轴指数；紫虚线为各档均值。",
    "【数据总结·社交功能】\\n不同社交功能（轻吐槽、边界维持等）承载不同互动任务。\\n\\n【对应本图】\\n树状分割块面积∝条数，点击块筛社交功能分类。",
    "【数据总结·关系与风险】\\n关系对象与风险等级共同刻画「跟谁说话、敢不敢撕破脸」。\\n\\n【对应本图】\\n每行一关系对象，横条为低/中/高风险的 100% 堆叠；另附华夫饼看包装档位占比。"
  ];'''

ADD_PANELS = '''    addPanel(
      "表达直接性 · 环形占比",
      "单维度环形：间接/直接/半直接等占比；点击扇区筛选。",
      function (box) { s3DonutDirectness(box, rowsExact()); },
      "环形直接性"
    );
    addPanel(
      "细分阶段 · 水平条形排名",
      "每行一类细分阶段，条长=条数；点击筛选。",
      function (box) { s3HBarSubCounts(box, rowsExact()); },
      "条形细分"
    );
    addPanel(
      "原始情绪 × 包装后 · 热力格",
      "格内颜色深浅=交叉样本数；点击格同时筛原情与包后。",
      function (box) { s3HeatmapOrigToPack(box, rowsExact()); },
      "热力包装链"
    );
    addPanel(
      "包装度 × 真实情绪指数 · 抖动散点",
      "每点一条；紫虚线为各包装档均值；青/灰示彩色/黑白。",
      function (box) { s3JitterPackVsReal(box, rowsExact()); },
      "散点真实度"
    );
    addPanel(
      "社交功能 · 树状分割（Treemap）",
      "矩形面积∝条数；点击块筛社交功能分类。",
      function (box) { s3TreemapSocialFn(box, rowsExact()); },
      "树图社交"
    );
    addPanel(
      "关系对象 × 风险 · 堆叠条 + 包装华夫饼",
      "上行：每关系对象内低/中/高风险的占比条；下图：低/中/高包装档的华夫近似占比。",
      function (box) {
        s3StackedRiskByRelation(box, rowsExact());
        s3WafflePackTier(box, rowsExact());
      },
      "堆叠风险"
    );'''

def main():
    s = html_path.read_text(encoding="utf-8")

    s = re.sub(
        r"<script>window\.__ROWS__ = \[.*?\];</script>\s*",
        '<script src="scene3_data.js"></script>\n',
        s,
        count=1,
        flags=re.DOTALL,
    )

    s = s.replace("QQ/微信早期熊猫头数据可视化（场景二）", "熊猫头表情包数据可视化（场景三）")
    s = s.replace("场景二", "场景三")
    s = s.replace("对应图片2/", "对应图片3/")
    s = s.replace("../数据/场景二/对应图片2/", "../数据/场景三/对应图片3/")
    s = s.replace("w.s2CubeFaceError", "w.s3CubeFaceError")
    s = s.replace("onerror=\"s2CubeFaceError(this)\"", "onerror=\"s3CubeFaceError(this)\"")
    s = s.replace("s2CubeFaceError", "s3CubeFaceError")

    s = s.replace(
        '<img class="cube-face-img" data-cube-file="37.png" src="对应图片3/37.png"',
        '<img class="cube-face-img" data-cube-file="144.png" src="对应图片3/144.png"',
    )
    s = s.replace(
        '<img class="cube-face-img" data-cube-file="199.png" src="对应图片3/199.png"',
        '<img class="cube-face-img" data-cube-file="32.png" src="对应图片3/32.png"',
    )
    s = s.replace(
        '<img class="cube-face-img" data-cube-file="109.png" src="对应图片3/109.png"',
        '<img class="cube-face-img" data-cube-file="200.png" src="对应图片3/200.png"',
    )
    s = s.replace(
        '<img class="cube-face-img" data-cube-file="38.png" src="对应图片3/38.png"',
        '<img class="cube-face-img" data-cube-file="5.png" src="对应图片3/5.png"',
    )

    # cube face copy (场景三叙事)
    s = re.sub(
        r'(<div class="face-num">① 场景三[^<]*</div>\s*<div class="cube-text">)[^<]*(</div>)',
        r'\1「当下」阶段：熊猫头多作间接回应，把硬话软说成表情包。\2',
        s,
        count=1,
    )
    s = re.sub(
        r'(<div class="face-num">② 场景三[^<]*</div>\s*<div class="cube-text">)[^<]*(</div>)',
        r'\1高包装 4—5 档集中，表情包已是社交修辞工具。\2',
        s,
        count=1,
    )
    s = re.sub(
        r'(<div class="face-num">③ 场景三[^<]*</div>\s*<div class="cube-text">)[^<]*(</div>)',
        r'\1班级群/校园语境突出，群聊里互损与缓冲并存。\2',
        s,
        count=1,
    )
    s = re.sub(
        r'(<div class="face-num">④ 场景三[^<]*</div>\s*<div class="cube-text">)[^<]*(</div>)',
        r'\1关系对象以同学/师生为主；风险多中位，配合包装链阅读。\2',
        s,
        count=1,
    )

    old_f = """  const F = {
    大阶段: \"大阶段\", 细分: \"细分阶段\", 当前图片: \"当前图片\", 原文件名: \"原文件名\", 图字: \"图片文字\",
    复杂度: \"视觉复杂度\", 字数: \"文字字数\", 黑白: \"黑白/彩色\", 情绪: \"情绪判断\", 动作: \"动作特征\",
    场景: \"社交场景判断\", 直接: \"表达直接性\", 包装: \"包装程度\", 原情: \"原始情绪类型\", 包后: \"包装后的表达类型\",
    关系: \"关系对象类型\", 风险: \"关系风险等级\"
  };
const FILTER_KEYS = [
    F.大阶段, F.细分, F.复杂度, F.字数, F.黑白, F.情绪, F.动作, F.场景, F.直接, F.包装, F.原情, F.包后, F.关系, F.风险
  ];"""
    new_f = """  const F = {
    大阶段: \"大阶段\", 细分: \"细分阶段\", 缩略: \"缩略图\", 当前图片: \"当前图片\", 原文件名: \"原文件名\", 图字: \"图片文字\",
    图片: \"原文件名\",
    复杂度: \"视觉复杂度\", 字数: \"文字字数\", 黑白: \"黑白/彩色\", 情绪: \"情绪判断\", 动作: \"动作特征\",
    场景: \"社交场景判断\", 直接: \"表达直接性\", 包装: \"包装程度\", 原情: \"原始情绪类型\", 包后: \"包装后的表达类型\",
    关系: \"关系对象类型\", 风险: \"关系风险等级\", 社功: \"社交功能分类\", 真实: \"贴近真实情绪程度指数\"
  };
const FILTER_KEYS = [
    F.大阶段, F.细分, F.复杂度, F.字数, F.黑白, F.情绪, F.动作, F.场景, F.直接, F.包装, F.原情, F.包后, F.关系, F.风险, F.社功
  ];"""
    s = s.replace(old_f, new_f)

    s = s.replace(
        "/** 优先与 场景二.html 同目录的 对应图片2/；失败时回退 data-img-alt（见立方体与阶段条脚本） */\n  const IMG_BASE = \"对应图片3/\";\n  const IMG_BASE_ALT = \"../数据/场景三/对应图片3/\";",
        "/** 场景三：对应图片3 */\n  const IMG_BASE = \"对应图片3/\";\n  const IMG_BASE_ALT = \"../数据/场景三/对应图片3/\";",
    )

    old_thumb = """  function thumb(r) {
    const u = norm(r[F.当前图片]);
    if (u && (u.startsWith(\"http\") || u.startsWith(\"data:\"))) return u;
    if (u) return u.indexOf(\"/\") >= 0 || u.startsWith(\".\") ? u : IMG_BASE + encodeURIComponent(u);
    const p = thumbEncodedPath(r[F.原文件名]);
    return p ? IMG_BASE + p : \"\";
  }"""
    new_thumb = """  function thumb(r) {
    var u1 = norm(r[F.缩略]);
    if (u1 && (u1.startsWith(\"http\") || u1.startsWith(\"data:\"))) return u1;
    if (u1) return u1.indexOf(\"/\") >= 0 || u1.startsWith(\".\") ? u1 : IMG_BASE + encodeURIComponent(u1);
    const u = norm(r[F.当前图片]);
    if (u && (u.startsWith(\"http\") || u.startsWith(\"data:\"))) return u;
    if (u) return u.indexOf(\"/\") >= 0 || u.startsWith(\".\") ? u : IMG_BASE + encodeURIComponent(u);
    const p = thumbEncodedPath(r[F.原文件名]);
    return p ? IMG_BASE + p : \"\";
  }"""
    s = s.replace(old_thumb, new_thumb)

    # Replace chart block
    pat = r"  function chartDonutLeadersSub\(container, rows\) \{.*?^  let narrativeLayerCleanup"
    s2, n = re.subn(pat, NEW_CHARTS.rstrip() + "\n\n  let narrativeLayerCleanup", s, count=1, flags=re.MULTILINE | re.DOTALL)
    if n != 1:
        raise SystemExit("chart block replace failed, n=" + str(n))
    s = s2

    s = re.sub(
        r"  const CHART_NARRATIVE_TEXTS = \[[\s\S]*?\];",
        NARR.strip(),
        s,
        count=1,
    )

    s = re.sub(
        r"    addPanel\(\s*\"细分阶段 × 包装度[\s\S]*?\"矩阵气泡\"\s*\);\s*",
        ADD_PANELS,
        s,
        count=1,
    )

    html_path.write_text(s, encoding="utf-8")
    print("patched", html_path)


if __name__ == "__main__":
    main()
