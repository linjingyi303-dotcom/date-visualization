  function s3ChartDonutDirect(container, rows) {
    var agg = aggregate(rows, F.直接).filter(function (d) { return d.count > 0; });
    if (!agg.length) return;
    var w = chartBoxW(container);
    var h = 320;
    var cx = w / 2;
    var cy = h / 2 + 4;
    var ir = 52;
    var or = Math.min(w, h) * 0.36;
    var tot = d3.sum(agg, function (d) { return d.count; }) || 1;
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    var gridG = svg.append("g").attr("class", "chart-grid-layer").attr("pointer-events", "none");
    s2FineGridXY(gridG, 18, 22, w - 18, h - 36, 24, 20);
    var pie = d3.pie().value(function (d) { return d.count; }).sort(null);
    var arcFull = d3.arc().innerRadius(ir).outerRadius(or).cornerRadius(2);
    var g = svg.append("g").attr("transform", "translate(" + cx + "," + cy + ")");
    var parts = pie(agg);
    var arcs = g.selectAll("path.donut-arc").data(parts).enter().append("path").attr("class", "donut-arc")
      .attr("fill", function (d, i) { return PAL[i % 4]; })
      .attr("stroke", "#0a0a0c").attr("stroke-width", 1.2)
      .style("cursor", "pointer")
      .on("click", function (ev, d) { setFilter(F.直接, d.data.key); })
      .on("mouseenter", function (ev, d) {
        tipShow(ev, esc(String(d.data.key)) + "<br>" + d.data.count + " 条 · " + Math.round(d.data.count / tot * 100) + "%");
      })
      .on("mousemove", moveTip).on("mouseleave", tipHide);
    arcs.attr("d", function (d) {
      var x = Object.assign({}, d);
      x.endAngle = x.startAngle;
      return arcFull(x);
    });
    runWhenChartSvgVisible(container, function () {
      arcs.transition().duration(720).ease(d3.easeCubicOut).attrTween("d", function (d) {
        var inter = d3.interpolate(d.startAngle, d.endAngle);
        return function (t) {
          var x = Object.assign({}, d);
          x.endAngle = inter(t);
          return arcFull(x);
        };
      });
    });
    g.append("text").attr("text-anchor", "middle").attr("dy", "-0.2em").attr("fill", "#e8e8f0").style("font-size", "11px").style("font-weight", "700").text("表达直接性");
    g.append("text").attr("text-anchor", "middle").attr("dy", "1em").attr("fill", "#8c8c9c").style("font-size", "8px").text("n=" + rows.length);
    s2AxisTitleX(svg, w / 2, h - 8, "环形：各直接性档位占比；点击扇区筛选");
    s2MiniDenseCaption(svg, w, rows, ["环形图"], { tx: w - 14, ty: 18, anchor: "end", lineDy: 10 });
    setFigCaptionLegend(container, agg.map(function (d, i) { return { hex: PAL[i % 4], text: d.key }; }),
      "环形图（非饼图平铺）：内环留白强调「间接/半直接/直接」结构占比。点击扇区联动顶栏筛选。\n" + captionSampleLine(rows));
  }

  function s3ChartHBarSubstage(container, rows) {
    var agg = sortPhases(aggregate(rows, F.细分).filter(function (d) { return d.count > 0; }));
    if (!agg.length) return;
    var w = chartBoxW(container);
    var m = { t: 44, l: 168, r: 88, b: 48 };
    var rowH = 34;
    var h = m.t + agg.length * rowH + m.b;
    var maxC = d3.max(agg, function (d) { return d.count; }) || 1;
    var x1 = w - m.r;
    var barW = x1 - m.l;
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    var defs = svg.append("defs");
    var gridG = svg.append("g").attr("class", "chart-grid-layer").attr("pointer-events", "none");
    s2FineGridXY(gridG, m.l, m.t, x1, m.t + agg.length * rowH, 20, agg.length * 4);
    agg.forEach(function (d, i) {
      var y0 = m.t + i * rowH + 6;
      var bw = barW * (d.count / maxC);
      var gid = "s3hb_" + i;
      var fillG = chartBarGradientUrl(defs, gid, PAL[i % 4]);
      svg.append("text").attr("x", m.l - 6).attr("y", y0 + 14).attr("text-anchor", "end").attr("fill", "#bbb").style("font-size", "8px")
        .text(String(d.key).length > 14 ? String(d.key).slice(0, 13) + "…" : d.key);
      var rect = svg.append("rect").attr("x", m.l).attr("y", y0).attr("height", 20).attr("width", 0).attr("rx", 2).attr("ry", 2)
        .attr("fill", fillG).attr("stroke", PAL[i % 4]).attr("stroke-width", 1).style("cursor", "pointer")
        .on("click", function () { setPhase(d.key); })
        .on("mouseenter", function (ev) { tipShow(ev, esc(String(d.key)) + "<br>" + d.count + " 条"); })
        .on("mousemove", moveTip).on("mouseleave", tipHide);
      runWhenChartSvgVisible(container, function () {
        rect.transition().delay(i * 70).duration(560).ease(d3.easeCubicOut).attr("width", bw);
      });
      svg.append("text").attr("x", m.l + bw + 6).attr("y", y0 + 14).attr("fill", "#a4a4b4").style("font-size", "8px").text(d.count);
    });
    s2AxisTitleX(svg, m.l + barW / 2, 18, "横向条形：细分阶段条数（长度∝量）");
    s2AxisTitleY(svg, 12, m.t + (agg.length * rowH) / 2, "纵：细分阶段");
    s2MiniDenseCaption(svg, w, rows, ["横向条"], { tx: x1 - 4, ty: m.t + 4, anchor: "end", lineDy: 10 });
    setFigCaptionLegend(container, agg.map(function (d, i) { return { hex: PAL[i % 4], text: d.key }; }),
      "横向条形图（非柱形纵立）：便于阅读长标签的细分阶段名。点击条筛选阶段。\n" + captionSampleLine(rows));
  }

  function s3ChartHeatmapOrigPack(container, rows) {
    var topO = aggregate(rows, F.原情).sort(function (a, b) { return b.count - a.count; }).slice(0, 7).map(function (d) { return d.key; });
    var topP = aggregate(rows, F.包后).sort(function (a, b) { return b.count - a.count; }).slice(0, 8).map(function (d) { return d.key; });
    if (!topO.length || !topP.length) return;
    var w = chartBoxW(container);
    var m = { t: 52, l: 120, r: 24, b: 56 };
    var cw = (w - m.l - m.r) / topP.length;
    var ch = 26;
    var h = m.t + topO.length * ch + m.b;
    var maxN = 1;
    var mat = {};
    topO.forEach(function (o) {
      topP.forEach(function (p) {
        var n = rows.filter(function (r) { return norm(r[F.原情]) === norm(o) && norm(r[F.包后]) === norm(p); }).length;
        mat[o + "\t" + p] = n;
        if (n > maxN) maxN = n;
      });
    });
    var color = d3.scaleSequential(d3.interpolateRgbBasis(["#1a0d2e", "#6c58ee", "#f54595", "#fce500"])).domain([0, maxN]);
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    var gridG = svg.append("g").attr("class", "chart-grid-layer").attr("pointer-events", "none");
    s2FineGridXY(gridG, m.l, m.t, m.l + topP.length * cw, m.t + topO.length * ch, topP.length * 6, topO.length * 5);
    topP.forEach(function (p, j) {
      svg.append("text").attr("x", m.l + j * cw + cw / 2).attr("y", m.t - 8).attr("text-anchor", "middle").attr("fill", "#999").style("font-size", "7px")
        .text(String(p).length > 5 ? String(p).slice(0, 4) + "…" : p);
    });
    var cells = [];
    topO.forEach(function (o, i) {
      svg.append("text").attr("x", m.l - 6).attr("y", m.t + i * ch + ch / 2 + 3).attr("text-anchor", "end").attr("fill", "#aaa").style("font-size", "7px")
        .text(String(o).length > 8 ? String(o).slice(0, 7) + "…" : o);
      topP.forEach(function (p, j) {
        var n = mat[o + "\t" + p];
        if (!n) return;
        var cx = m.l + j * cw;
        var cy = m.t + i * ch;
        cells.push({ o: o, p: p, n: n, cx: cx, cy: cy, i: i, j: j });
      });
    });
    var gCells = svg.selectAll("rect.hm").data(cells).enter().append("rect").attr("class", "hm")
      .attr("x", function (d) { return d.cx + 1; }).attr("y", function (d) { return d.cy + 1; })
      .attr("width", cw - 2).attr("height", ch - 2).attr("rx", 2).attr("fill", function (d) { return color(d.n); })
      .attr("stroke", "rgba(0,0,0,0.35)").attr("stroke-width", 0.5).style("cursor", "pointer")
      .on("click", function (ev, d) { setFilter(F.原情, d.o); setFilter(F.包后, d.p); })
      .on("mouseenter", function (ev, d) {
        tipShow(ev, "原情 " + esc(String(d.o)) + "<br>包后 " + esc(String(d.p)) + "<br>n=" + d.n);
      })
      .on("mousemove", moveTip).on("mouseleave", tipHide);
    runWhenChartSvgVisible(container, function () {
      gCells.attr("opacity", 0).transition().delay(function (d) { return d.i * 40 + d.j * 28; }).duration(380).attr("opacity", 1);
    });
    s2AxisTitleX(svg, m.l + (topP.length * cw) / 2, h - 10, "横：包装后表达（Top 类目）");
    s2AxisTitleY(svg, 14, m.t + (topO.length * ch) / 2, "纵：原始情绪（Top）");
    s2MiniDenseCaption(svg, w, rows, ["热力格"], { tx: m.l + topP.length * cw - 4, ty: m.t + 4, anchor: "end", lineDy: 10 });
    setFigCaptionLegend(container, [{ hex: "#fc00fc", text: "亮=交叉多" }],
      "热力矩阵：原始情绪×包装后表达的交叉频数（非散点）。点击格同时筛原情与包后。\n" + captionSampleLine(rows));
  }

  function s3ChartStripPackReal(container, rows) {
    var w = chartBoxW(container);
    var h = 300;
    var m = { t: 48, l: 56, r: 28, b: 52 };
    var packs = [1, 2, 3, 4, 5];
    var x0 = m.l;
    var x1 = w - m.r;
    var y0 = m.t;
    var y1 = h - m.b;
    var xStep = (x1 - x0) / packs.length;
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    var gridG = svg.append("g").attr("class", "chart-grid-layer").attr("pointer-events", "none");
    s2FineGridXY(gridG, x0, y0, x1, y1, packs.length * 8, 14);
    packs.forEach(function (pk, j) {
      svg.append("text").attr("x", x0 + j * xStep + xStep / 2).attr("y", y0 - 10).attr("text-anchor", "middle").attr("fill", "#888").style("font-size", "9px").text("包" + pk);
    });
    var ySc = d3.scaleLinear().domain([30, 85]).range([y1, y0]);
    svg.append("line").attr("x1", x0).attr("x2", x0).attr("y1", y0).attr("y2", y1).attr("stroke", CHART_AXIS_DOMAIN_STROKE).attr("stroke-width", 1.2);
    [40, 55, 70, 85].forEach(function (tv) {
      var yy = ySc(tv);
      svg.append("line").attr("x1", x0).attr("x2", x1).attr("y1", yy).attr("y2", yy).attr("stroke", CHART_GRID_STROKE).attr("stroke-width", 0.55).attr("stroke-dasharray", "4 6");
      svg.append("text").attr("x", x0 - 8).attr("y", yy + 3).attr("text-anchor", "end").attr("fill", "#777").style("font-size", "7px").text(tv);
    });
    var emoMap = new Map();
    rows.forEach(function (r, idx) {
      var e = norm(r[F.情绪]) || "—";
      if (!emoMap.has(e)) emoMap.set(e, emoMap.size);
    });
    var pts = rows.map(function (r, idx) {
      var pk = +r[F.包装];
      if (isNaN(pk) || pk < 1 || pk > 5) pk = 3;
      var val = +r[F.真实];
      if (isNaN(val)) val = 55;
      var jitter = (seed01(idx + pk * 17) - 0.5) * xStep * 0.62;
      var x = x0 + (pk - 1) * xStep + xStep / 2 + jitter;
      var yJ = (seed01(idx * 7 + 3) - 0.5) * 8;
      return { x: x, y: ySc(val) + yJ, r: r, pk: pk, val: val, emo: norm(r[F.情绪]) || "—", idx: idx };
    });
    var circles = svg.selectAll("circle.s3pt").data(pts).enter().append("circle").attr("class", "s3pt")
      .attr("cx", function (d) { return d.x; }).attr("cy", function (d) { return d.y; })
      .attr("r", 0).attr("fill", function (d) { return PAL[(emoMap.get(d.emo) || 0) % 4]; }).attr("fill-opacity", 0.72)
      .attr("stroke", "rgba(255,255,255,0.25)").attr("stroke-width", 0.6).style("cursor", "pointer")
      .on("click", function (ev, d) {
        setFilter(F.包装, String(d.pk));
        setFilter(F.情绪, d.emo);
      })
      .on("mouseenter", function (ev, d) {
        var href = thumb(d.r);
        tipShow(ev, (href ? "<img src=\"" + esc(href) + "\" alt=\"\">" : "") + "贴近真实 " + d.val + "<br>包" + d.pk + " · " + esc(d.emo));
      })
      .on("mousemove", moveTip).on("mouseleave", tipHide);
    runWhenChartSvgVisible(container, function () {
      circles.transition().delay(function (d) { return (d.idx % 40) * 12; }).duration(420).ease(d3.easeBackOut.overshoot(1.05)).attr("r", 5);
    });
    s2AxisTitleY(svg, 12, (y0 + y1) / 2, "纵：贴近真实情绪指数");
    s2AxisTitleX(svg, (x0 + x1) / 2, h - 8, "横：包装度分档（带水平抖动）");
    s2MiniDenseCaption(svg, w, rows, ["抖动散点"], { tx: x1 - 4, ty: y0 + 4, anchor: "end", lineDy: 10 });
    setFigCaptionLegend(container, [{ hex: PAL[0], text: "情绪着色" }],
      "分类抖动散点：横轴离散包装度，纵轴为贴近真实情绪指数；点内水平抖动避免重叠。点击点筛包装+情绪。\n" + captionSampleLine(rows));
  }

  function s3ChartTreemapSocial(container, rows) {
    var agg = aggregate(rows, F.社交).filter(function (d) { return d.count > 0; }).sort(function (a, b) { return b.count - a.count; });
    if (!agg.length) return;
    var w = chartBoxW(container);
    var h = 320;
    var m = { t: 40, l: 20, r: 20, b: 44 };
    var W = w - m.l - m.r;
    var H = h - m.t - m.b;
    var root = d3.hierarchy({ name: "root", children: agg.map(function (d) { return { name: d.key, value: d.count }; }) })
      .sum(function (d) { return d.value || 0; })
      .sort(function (a, b) { return (b.value || 0) - (a.value || 0); });
    d3.treemap().size([W, H]).paddingOuter(4).paddingInner(2).round(true)(root);
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    var gridG = svg.append("g").attr("class", "chart-grid-layer").attr("pointer-events", "none");
    s2FineGridXY(gridG, m.l, m.t, m.l + W, m.t + H, 22, 18);
    var leaf = root.leaves();
    var g = svg.append("g").attr("transform", "translate(" + m.l + "," + m.t + ")");
    var nodes = g.selectAll("g.tm").data(leaf).enter().append("g").attr("class", "tm")
      .attr("transform", function (d) { return "translate(" + d.x0 + "," + d.y0 + ")"; })
      .style("cursor", "pointer")
      .on("click", function (ev, d) { setFilter(F.社交, d.data.name); })
      .on("mouseenter", function (ev, d) {
        tipShow(ev, esc(String(d.data.name)) + "<br>" + d.value + " 条");
      })
      .on("mousemove", moveTip).on("mouseleave", tipHide);
    nodes.append("rect").attr("width", function (d) { return Math.max(0, d.x1 - d.x0); }).attr("height", function (d) { return Math.max(0, d.y1 - d.y0); })
      .attr("rx", 2).attr("fill", function (d, i) { return PAL[i % 4]; }).attr("fill-opacity", 0.55).attr("stroke", "rgba(255,255,255,0.2)").attr("stroke-width", 1);
    runWhenChartSvgVisible(container, function () {
      nodes.attr("opacity", 0).transition().delay(function (d, i) { return i * 45; }).duration(400).attr("opacity", 1);
    });
    nodes.append("text").attr("x", 4).attr("y", 14).attr("fill", "#f2f2f8").style("font-size", "8px").style("pointer-events", "none")
      .text(function (d) {
        var s = String(d.data.name);
        var mw = Math.max(0, d.x1 - d.x0) - 8;
        return s.length > 12 && mw < 80 ? s.slice(0, 10) + "…" : (s.length > 16 ? s.slice(0, 14) + "…" : s);
      });
    s2AxisTitleX(svg, m.l + W / 2, h - 10, "矩形树图：社交功能分类面积∝条数；点击块筛选");
    s2MiniDenseCaption(svg, w, rows, ["树图"], { tx: m.l + W - 4, ty: m.t + 4, anchor: "end", lineDy: 10 });
    setFigCaptionLegend(container, agg.slice(0, 6).map(function (d, i) { return { hex: PAL[i % 4], text: d.key }; }),
      "矩形树图（非条形堆叠）：展示社交功能编码的体量结构。点击矩形筛「社交功能分类」。\n" + captionSampleLine(rows));
  }

  function s3ChartStackRelRisk(container, rows) {
    var relAgg = aggregate(rows, F.关系).sort(function (a, b) { return b.count - a.count; }).slice(0, 9);
    if (!relAgg.length) return;
    var riskOrder = ["低", "中", "高"];
    var stackData = relAgg.map(function (d) {
      var slice = rows.filter(function (r) { return norm(r[F.关系]) === norm(d.key); });
      var o = { 关系: d.key };
      riskOrder.forEach(function (rk) {
        o[rk] = slice.filter(function (r) { return norm(r[F.风险]).indexOf(rk) >= 0; }).length;
      });
      return o;
    });
    var series = d3.stack().keys(riskOrder)(stackData);
    var w = chartBoxW(container);
    var m = { t: 44, l: 168, r: 48, b: 52 };
    var rowH = 28;
    var h = m.t + stackData.length * rowH + m.b;
    var maxT = d3.max(stackData, function (d) { return riskOrder.reduce(function (s, k) { return s + d[k]; }, 0); }) || 1;
    var plotW = w - m.l - m.r;
    var svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    var defs = svg.append("defs");
    var gridG = svg.append("g").attr("class", "chart-grid-layer").attr("pointer-events", "none");
    s2FineGridXY(gridG, m.l, m.t, m.l + plotW, m.t + stackData.length * rowH, 24, stackData.length * 4);
    var riskColors = { 低: PAL[1], 中: PAL[3], 高: PAL[0] };
    var stackRects = [];
    series.forEach(function (layer, li) {
      layer.forEach(function (d, i) {
        var y0 = m.t + i * rowH + 5;
        var x0 = m.l + (d[0] / maxT) * plotW;
        var x1 = m.l + (d[1] / maxT) * plotW;
        var bw = Math.max(0, x1 - x0);
        if (bw < 0.5) return;
        var gid = "s3st_" + i + "_" + li;
        var fillG = chartBarGradientUrl(defs, gid, riskColors[layer.key] || PAL[2]);
        var rect = svg.append("rect").attr("x", x0).attr("y", y0).attr("height", 18).attr("width", 0).attr("rx", 1)
          .attr("fill", fillG).attr("stroke", "rgba(0,0,0,0.25)").attr("stroke-width", 0.5).style("cursor", "pointer")
          .on("click", function () {
            setFilter(F.关系, d.data.关系);
            setFilter(F.风险, layer.key);
          })
          .on("mouseenter", function (ev) {
            tipShow(ev, esc(String(d.data.关系)) + "<br>风险「" + esc(layer.key) + "」 " + (d[1] - d[0]) + " 条");
          })
          .on("mousemove", moveTip).on("mouseleave", tipHide);
        stackRects.push({ rect: rect, bw: bw, del: i * 55 + li * 30 });
      });
    });
    runWhenChartSvgVisible(container, function () {
      stackRects.forEach(function (o) {
        o.rect.transition().delay(o.del).duration(480).ease(d3.easeCubicOut).attr("width", o.bw);
      });
    });
    stackData.forEach(function (d, i) {
      svg.append("text").attr("x", m.l - 6).attr("y", m.t + i * rowH + 17).attr("text-anchor", "end").attr("fill", "#bbb").style("font-size", "7.5px")
        .text(String(d.关系).length > 12 ? String(d.关系).slice(0, 11) + "…" : d.关系);
    });
    s2AxisTitleX(svg, m.l + plotW / 2, 20, "堆叠比例横条：每行一关系对象，段=风险等级构成");
    var lx = m.l + plotW - 4;
    var ly = m.t - 2;
    riskOrder.forEach(function (rk, ri) {
      svg.append("rect").attr("x", lx - 62 + ri * 52).attr("y", ly - 14).attr("width", 8).attr("height", 8).attr("fill", riskColors[rk]);
      svg.append("text").attr("x", lx - 52 + ri * 52).attr("y", ly - 7).attr("fill", "#999").style("font-size", "7px").text("风险" + rk);
    });
    s2MiniDenseCaption(svg, w, rows, ["堆叠条"], { tx: m.l + plotW - 4, ty: m.t + 4, anchor: "end", lineDy: 10 });
    setFigCaptionLegend(container, riskOrder.map(function (k) { return { hex: riskColors[k], text: "风险·" + k }; }),
      "横向堆叠条：同一关系对象下低/中/高风险条数构成（100% 宽度归一到该行总量）。点击段双筛。\n" + captionSampleLine(rows));
  }

