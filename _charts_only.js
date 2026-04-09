  function whenChartVisible(host, drawAnim) {
    const io = new IntersectionObserver((ents) => {
      ents.forEach(e => {
        if (e.isIntersecting) {
          drawAnim();
          io.disconnect();
        }
      });
    }, { root: null, rootMargin: "0px 0px -5% 0px", threshold: 0.08 });
    io.observe(host);
    setTimeout(drawAnim, 1800);
  }

  function bindChartRevealForPanel(panelEl, host) {
    if (!panelEl || !host) return;
    host.classList.remove("viz-chart-in");
    delete host.dataset.vizRevealed;
    var reveal = function () {
      if (host.dataset.vizRevealed === "1") return;
      host.dataset.vizRevealed = "1";
      requestAnimationFrame(function () {
        host.classList.add("viz-chart-in");
      });
    };
    try {
      var io = new IntersectionObserver(function (ents) {
        ents.forEach(function (e) {
          if (e.isIntersecting) {
            reveal();
            io.disconnect();
          }
        });
      }, { root: null, threshold: 0.01, rootMargin: "100px 0px 100px 0px" });
      io.observe(panelEl);
    } catch (err) {
      setTimeout(reveal, 200);
    }
    requestAnimationFrame(function () {
      var rect = panelEl.getBoundingClientRect();
      var vh = window.innerHeight || document.documentElement.clientHeight || 800;
      if (rect.bottom > -40 && rect.top < vh + 40) reveal();
    });
    setTimeout(reveal, 500);
  }

  function chartBeeswarmProto(container, rows) {
    const agg = aggregate(rows, F.原型).slice(0, 8);
    if (!agg.length) return;
    const w = chartBoxW(container);
    const labelW = 150;
    const topPad = 26;
    const axisPad = 40;
    const rowH = 36;
    const axisY = topPad + agg.length * rowH + 8;
    const h = axisY + axisPad;
    const xPad = labelW + 36;
    const plotW = Math.max(80, w - xPad - 28);
    const xScale = d3.scaleLinear().domain([1, 5]).range([xPad, xPad + plotW]);
    const svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    svg.append("line").attr("x1", xPad - 12).attr("x2", xPad - 12).attr("y1", topPad - 4).attr("y2", axisY - 2)
      .attr("stroke", "#555").attr("stroke-width", 2).attr("stroke-dasharray", "5 5");
    svg.append("text").attr("x", labelW - 6).attr("y", 14).attr("text-anchor", "end").attr("fill", "#777").style("font-size", "8px").text("人物原型");
    const leg = [["黑白", PAL[0]], ["彩色", PAL[3]], ["其它", PAL[2]]];
    leg.forEach(([lab, col], li) => {
      const lx = w - 10;
      const ly = 8 + li * 14;
      svg.append("rect").attr("x", lx - 58).attr("y", ly).attr("width", 9).attr("height", 9).attr("fill", col).attr("stroke", "#fff").attr("stroke-width", 1);
      svg.append("text").attr("x", lx - 44).attr("y", ly + 8).attr("fill", "#aaa").style("font-size", "8px").text(lab);
    });
    agg.forEach((cat, ri) => {
      const yy = topPad + ri * rowH;
      const sub = rows.filter(r => norm(r[F.原型]) === norm(cat.key));
      svg.append("text").attr("x", labelW - 6).attr("y", yy + rowH / 2 + 4).attr("text-anchor", "end")
        .attr("fill", "#ddd").style("font-size", "10px")
        .text(String(cat.key).length > 8 ? String(cat.key).slice(0, 7) + "…" : cat.key);
      sub.forEach((r, j) => {
        const pack = +r[F.包装];
        const px = isNaN(pack) ? 3 : Math.min(5, Math.max(1, pack));
        const jitter = (seed01(j + ri * 997) - 0.5) * (plotW / 24);
        const jy = (seed01(j * 7919 + ri) - 0.5) * 7;
        const cx = xScale(px) + jitter;
        const cy = yy + rowH / 2 + jy;
        const col = colorByBW(r[F.黑白彩色]);
        const href = thumb(r) || IMG_PLACEHOLDER;
        const half = 5;
        const g = svg.append("g").attr("class", "bee-thumb")
          .attr("data-cx", cx).attr("data-cy", cy)
          .attr("transform", "translate(" + cx + "," + cy + ") scale(0)")
          .style("cursor", "pointer")
          .on("click", () => { setFilter(F.原型, cat.key); })
          .on("mouseenter", function (ev) {
            const t = d3.select(this);
            t.interrupt();
            const x = +t.attr("data-cx"), y = +t.attr("data-cy");
            t.transition().duration(180).attr("transform", "translate(" + x + "," + y + ") scale(2.05)");
            tipShow(ev, (href !== IMG_PLACEHOLDER ? `<img src="${esc(href)}" alt="">` : "") + esc(norm(r[F.备注]) || cat.key));
          })
          .on("mousemove", moveTip)
          .on("mouseleave", function () {
            const t = d3.select(this);
            t.interrupt();
            const x = +t.attr("data-cx"), y = +t.attr("data-cy");
            t.transition().duration(160).attr("transform", "translate(" + x + "," + y + ") scale(1)");
            tipHide();
          });
        g.append("rect").attr("x", -half - 1).attr("y", -half - 1).attr("width", half * 2 + 2).attr("height", half * 2 + 2)
          .attr("fill", "rgba(0,0,0,0.35)").attr("stroke", col).attr("stroke-width", 2);
        g.append("image")
          .attr("href", href)
          .attr("x", -half).attr("y", -half).attr("width", half * 2).attr("height", half * 2)
          .attr("preserveAspectRatio", "xMidYMid slice");
        g.transition().delay(j * 12).duration(320).ease(d3.easeElasticOut)
          .attr("transform", "translate(" + cx + "," + cy + ") scale(1)");
      });
    });
    svg.append("g").attr("transform", "translate(0," + axisY + ")")
      .call(d3.axisBottom(xScale).ticks(5).tickFormat(d3.format("d")))
      .call(g => g.select(".domain").attr("stroke", "#666").attr("stroke-width", 2))
      .selectAll("text").attr("fill", "#aaa").style("font-size", "9px");
    svg.append("text").attr("x", xPad + plotW / 2).attr("y", h - 6).attr("text-anchor", "middle").attr("fill", "#777").style("font-size", "9px")
      .text("情绪包装度（横轴 1–5）");
  }

  function chartSplinePhases(container, rows) {
    const agg = sortPhases(aggregate(rows, F.阶段));
    if (!agg.length) return;
    const w = chartBoxW(container);
    const margin = { t: 28, r: 24, b: 56, l: 24 };
    const iw = w - margin.l - margin.r;
    const ih = 220;
    const h = margin.t + ih + margin.b;
    const max = d3.max(agg, d => d.count) || 1;
    const x = d3.scalePoint().domain(agg.map(d => d.key)).range([margin.l, margin.l + iw]).padding(0.5);
    const y = d3.scaleLinear().domain([0, max]).nice().range([margin.t + ih, margin.t]);
    const svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    const pts = agg.map(d => [x(d.key), y(d.count)]);
    if (pts.length >= 2) {
      const line = d3.line().curve(d3.curveMonotoneX);
      const pathD = line(pts);
      const path = svg.append("path").attr("class", "anim-spline").attr("fill", "none").attr("stroke", PAL[0]).attr("stroke-width", 4)
        .attr("stroke-linecap", "square").attr("stroke-linejoin", "miter").attr("d", pathD);
      whenChartVisible(container, () => {
        try {
          const len = path.node().getTotalLength();
          path.attr("stroke-dasharray", len).attr("stroke-dashoffset", len)
            .transition().duration(1100).ease(d3.easeCubicOut).attr("stroke-dashoffset", 0);
        } catch (er) { path.attr("stroke-dasharray", null).attr("stroke-dashoffset", null); }
      });
    }
    agg.forEach((d, i) => {
      const xi = x(d.key), yi = y(d.count), y0 = margin.t + ih;
      svg.append("line").attr("x1", xi).attr("x2", xi).attr("y1", y0).attr("y2", y0)
        .attr("stroke", "#555").attr("stroke-width", 2).attr("stroke-dasharray", "3 3")
        .transition().delay(400 + i * 80).duration(350).attr("y2", yi);
      svg.append("circle").attr("cx", xi).attr("cy", yi).attr("r", 0)
        .attr("fill", "#fff").attr("stroke", PAL[1]).attr("stroke-width", 3)
        .style("cursor", "pointer")
        .on("click", () => setPhase(d.key))
        .transition().delay(500 + i * 80).duration(400).ease(d3.easeElasticOut).attr("r", 8);
      svg.append("text").attr("x", xi).attr("y", y0 + 22).attr("text-anchor", "middle")
        .attr("fill", "#888").style("font-size", "9px").text(String(d.key).length > 8 ? String(d.key).slice(0, 7) + "…" : d.key);
      svg.append("text").attr("x", xi).attr("y", yi - 14).attr("text-anchor", "middle")
        .attr("fill", PAL[3]).style("font-size", "12px").text(d.count);
    });
  }

  function chartHBarPercentLegend(container, key, rows) {
    const agg = aggregate(rows, key).slice(0, 7);
    if (!agg.length) return;
    const w = chartBoxW(container);
    const labelW = 140;
    const barLeft = labelW + 8;
    const barW = w - barLeft - 200;
    const rowH = 36;
    const h = 48 + agg.length * rowH;
    const max = d3.max(agg, d => d.count) || 1;
    const svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    const x0 = barLeft, x100 = barLeft + barW;
    [0, 0.25, 0.5, 0.75, 1].forEach(t => {
      const gx = x0 + t * barW;
      svg.append("line").attr("x1", gx).attr("x2", gx).attr("y1", 20).attr("y2", h - 16)
        .attr("stroke", "#444").attr("stroke-width", 1).attr("stroke-dasharray", "4 4");
      svg.append("text").attr("x", gx).attr("y", 14).attr("text-anchor", "middle").attr("fill", "#666").style("font-size", "9px")
        .text(Math.round(t * 100) + "%");
    });
    const legX = x100 + 20;
    const sum = d3.sum(agg, x => x.count) || 1;
    agg.forEach((d, i) => {
      const yy = 32 + i * rowH;
      const bw = (d.count / max) * barW;
      let short = String(d.key);
      if (short.length > 10) short = short.slice(0, 9) + "…";
      svg.append("text").attr("x", labelW).attr("y", yy + 18).attr("text-anchor", "end").attr("fill", "#bbb").style("font-size", "10px").text(short);
      svg.append("rect").attr("x", x0).attr("y", yy + 4).attr("width", 0).attr("height", 18)
        .attr("fill", PAL[i % 4]).attr("stroke", "#fff").attr("stroke-width", 2)
        .style("cursor", "pointer")
        .on("click", () => setFilter(key, d.key))
        .transition().duration(500).delay(i * 60).attr("width", Math.max(4, bw));
      svg.append("rect").attr("x", legX).attr("y", yy + 6).attr("width", 14).attr("height", 14)
        .attr("fill", PAL[i % 4]).attr("stroke", "#fff").attr("stroke-width", 2);
      const pct = Math.round(d.count / sum * 100);
      svg.append("text").attr("x", legX + 22).attr("y", yy + 18).attr("fill", "#eee").style("font-size", "11px")
        .text(pct + "% · " + d.count + " 条");
    });
  }

  function chartRadialRingBars(container, key, rows) {
    const agg = aggregate(rows, key).slice(0, 7);
    if (!agg.length) return;
    const w = chartBoxW(container);
    const h = 380;
    const ringW = 16;
    const gap = 5;
    const total = d3.sum(agg, d => d.count) || 1;
    const rOut0 = 38 + agg.length * (ringW + gap);
    const cx = rOut0 + 36;
    const cy = h / 2;
    const leadX = cx + 200;
    const blockRight = leadX + 220;
    const offX = Math.max(12, (w - blockRight) / 2);
    const svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    const root = svg.append("g").attr("transform", "translate(" + offX + ",0)");
    agg.forEach((d, i) => {
      const ro = rOut0 - i * (ringW + gap);
      const ri = ro - ringW;
      const pct = d.count / total;
      const arcBg = d3.arc().innerRadius(ri).outerRadius(ro).startAngle(0).endAngle(2 * Math.PI);
      const arcFg = d3.arc().innerRadius(ri).outerRadius(ro).startAngle(-Math.PI / 2).endAngle(-Math.PI / 2 + pct * 2 * Math.PI);
      root.append("path").attr("d", arcBg({})).attr("transform", "translate(" + cx + "," + cy + ")")
        .attr("fill", PAL[i % 4]).attr("fill-opacity", 0.22).attr("stroke", "#fff").attr("stroke-width", 2);
      const fg = root.append("path").attr("d", arcFg({})).attr("transform", "translate(" + cx + "," + cy + ")")
        .attr("fill", "#0a0a0a").attr("stroke", PAL[i % 4]).attr("stroke-width", 3)
        .style("cursor", "pointer")
        .on("click", () => setFilter(key, d.key))
        .on("mouseenter", function () { d3.select(this).attr("stroke", "#fcfce5").attr("stroke-width", 4); })
        .on("mouseleave", function () { d3.select(this).attr("stroke", PAL[i % 4]).attr("stroke-width", 3); })
        .attr("opacity", 0)
        .transition().duration(600).delay(i * 90).attr("opacity", 1);
      const mid = -Math.PI / 2 + pct * Math.PI;
      const x1 = cx + Math.cos(mid) * ro;
      const y1 = cy + Math.sin(mid) * ro;
      const x2 = leadX;
      const y2 = cy - rOut0 + i * 26 + 20;
      root.append("polyline").attr("points", x1 + "," + y1 + " " + (x1 + (x2 - x1) * 0.45) + "," + y1 + " " + x2 + "," + y2)
        .attr("fill", "none").attr("stroke", PAL[i % 4]).attr("stroke-width", 2).attr("opacity", 0.85);
      root.append("text").attr("x", x2 + 6).attr("y", y2 + 4).attr("fill", "#eee").style("font-size", "10px")
        .text(Math.round(pct * 100) + "% " + (String(d.key).length > 14 ? String(d.key).slice(0, 13) + "…" : d.key));
    });
    root.append("circle").attr("cx", cx).attr("cy", cy).attr("r", rOut0 - agg.length * (ringW + gap) - gap)
      .attr("fill", "#080808").attr("stroke", PAL[3]).attr("stroke-width", 3);
  }

  function chartDonutCallouts(container, key, rows) {
    const agg = aggregate(rows, key);
    if (!agg.length) return;
    const w = chartBoxW(container);
    const h = 320;
    const cx = w / 2;
    const cy = h / 2 + 4;
    const R = Math.min(w * 0.26, h * 0.3, 112);
    const pie = d3.pie().value(d => d.count).sort(null);
    const arc = d3.arc().innerRadius(R * 0.48).outerRadius(R);
    const svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    const g = svg.append("g").attr("transform", "translate(" + cx + "," + cy + ")");
    const pieD = pie(agg);
    const tot = d3.sum(agg, x => x.count) || 1;
    g.selectAll("path.slice").data(pieD).join("path").attr("class", "slice donut-slice-pix")
      .attr("fill", (_, j) => PAL[j % 4]).attr("stroke", "#050508").attr("stroke-width", 2)
      .style("cursor", "pointer")
      .on("click", (_, d) => setFilter(key, d.data.key))
      .on("mouseenter", function () {
        d3.select(this).attr("stroke", "#fcfce5").attr("stroke-width", 5);
      })
      .on("mouseleave", function () {
        d3.select(this).attr("stroke", "#050508").attr("stroke-width", 2);
      })
      .transition().duration(700).attrTween("d", function (d) {
        const i0 = d3.interpolate({ startAngle: d.startAngle, endAngle: d.startAngle }, d);
        return t => arc(i0(t));
      });
    const cg = svg.append("g").attr("class", "donut-callouts");
    pieD.forEach((d, i) => {
      const mid = (d.startAngle + d.endAngle) / 2 - Math.PI / 2;
      const ox = Math.cos(mid), oy = Math.sin(mid);
      const x1 = cx + ox * R * 1.02;
      const y1 = cy + oy * R * 1.02;
      const x2 = cx + ox * (R + 36);
      const y2 = cy + oy * (R + 36);
      const right = ox >= 0;
      const x3 = right ? Math.min(w - 16, cx + R + 108) : Math.max(16, cx - R - 108);
      const col = PAL[i % 4];
      cg.append("polyline").attr("points", x1 + "," + y1 + " " + x2 + "," + y2 + " " + x3 + "," + y2)
        .attr("fill", "none").attr("stroke", col).attr("stroke-width", 3).attr("opacity", 0.95);
      const pct = Math.round(d.data.count / tot * 100);
      cg.append("text").attr("x", right ? x3 + 8 : x3 - 8).attr("y", y2 + 5)
        .attr("text-anchor", right ? "start" : "end").attr("fill", col).style("font-size", "11px").style("font-weight", "700")
        .text(pct + "% · " + d.data.key);
    });
  }

  function chartPolarSpider(container, key, rows) {
    const agg = aggregate(rows, key).slice(0, 7);
    if (!agg.length) return;
    const w = chartBoxW(container);
    const h = 392;
    const cx = w / 2;
    const cy = h / 2 - 8;
    const r0 = 36;
    const r1 = 118;
    const n = agg.length;
    const max = d3.max(agg, d => d.count) || 1;
    const svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    [0, 0.5, 1].forEach((t, li) => {
      const rr = r0 + t * (r1 - r0);
      svg.append("circle").attr("cx", cx).attr("cy", cy).attr("r", rr).attr("fill", "none")
        .attr("stroke", li === 0 ? "#6c58ee" : "#3a3d52").attr("stroke-width", li === 0 ? 2 : 1).attr("stroke-dasharray", li === 0 ? "none" : "5 7");
    });
    svg.append("text").attr("x", cx + r1 + 14).attr("y", cy - r1 + 12).attr("fill", "#6c58ee").style("font-size", "8px").text("100%");
    svg.append("text").attr("x", cx + r1 + 14).attr("y", cy - (r0 + (r1 - r0) * 0.5) + 4).attr("fill", "#777").style("font-size", "8px").text("50%");
    svg.append("text").attr("x", cx + r1 + 14).attr("y", cy - r0 + 10).attr("fill", "#555").style("font-size", "8px").text("0");
    const pts = [];
    agg.forEach((d, i) => {
      const ang = (i / n) * 2 * Math.PI - Math.PI / 2;
      const rr = r0 + (d.count / max) * (r1 - r0);
      const x = cx + Math.cos(ang) * rr;
      const y = cy + Math.sin(ang) * rr;
      pts.push([x, y]);
      svg.append("line").attr("x1", cx).attr("y1", cy).attr("x2", cx + Math.cos(ang) * r1).attr("y2", cy + Math.sin(ang) * r1)
        .attr("stroke", "#4a4d64").attr("stroke-width", 2).attr("stroke-dasharray", "4 6");
      const lx = cx + Math.cos(ang) * (r1 + 26);
      const ly = cy + Math.sin(ang) * (r1 + 26);
      const short = String(d.key).length > 7 ? String(d.key).slice(0, 6) + "…" : d.key;
      svg.append("text").attr("x", lx).attr("y", ly).attr("text-anchor", "middle").attr("fill", PAL[i % 4]).style("font-size", "9px").style("font-weight", "700")
        .text(short + " · " + d.count);
    });
    const line = d3.line().curve(d3.curveLinearClosed);
    const path = svg.append("path").attr("fill", PAL[0]).attr("fill-opacity", 0.18).attr("stroke", "#59e2fd").attr("stroke-width", 4)
      .attr("stroke-linejoin", "miter").attr("d", line(pts)).style("cursor", "pointer");
    agg.forEach((d, i) => {
      const ang = (i / n) * 2 * Math.PI - Math.PI / 2;
      const rr = r0 + (d.count / max) * (r1 - r0);
      svg.append("circle").attr("cx", cx + Math.cos(ang) * rr).attr("cy", cy + Math.sin(ang) * rr).attr("r", 7)
        .attr("fill", PAL[i % 4]).attr("stroke", "#fff").attr("stroke-width", 2)
        .style("cursor", "pointer")
        .on("click", () => setFilter(key, d.key));
    });
    svg.append("text").attr("x", 14).attr("y", h - 22).attr("fill", "#888").style("font-size", "9px")
      .text("图注：半径 = 该来源条数 ÷ 当前最大（" + max + "）；虚线同心圆 ≈ 0% / 50% / 100%。");
    svg.append("text").attr("x", 14).attr("y", h - 8).attr("fill", "#666").style("font-size", "8px")
      .text("顶点旁数字为原始条数；类别数随筛选变化（至多 7 类）。");
    whenChartVisible(container, () => {
      try {
        const len = path.node().getTotalLength();
        path.attr("stroke-dasharray", len).attr("stroke-dashoffset", len)
          .transition().duration(1400).attr("stroke-dashoffset", 0);
      } catch (er) {}
    });
  }

  function chartDualAreaStripes(container, rows) {
    const list = rows.slice();
    const bins = 14;
    const slot = Math.max(1, Math.ceil(list.length / bins));
    const ser = [];
    for (let b = 0; b < bins; b++) {
      let bw = 0, c = 0;
      for (let k = b * slot; k < Math.min(list.length, (b + 1) * slot); k++) {
        const col = String(list[k][F.黑白彩色]);
        bw += col.indexOf("黑白") >= 0 && col.indexOf("彩") < 0 ? 1 : 0;
        c += col.indexOf("彩") >= 0 ? 1 : 0;
      }
      ser.push({ i: b, bw, c });
    }
    const w = chartBoxW(container);
    const margin = { t: 36, r: 20, b: 40, l: 44 };
    const iw = w - margin.l - margin.r;
    const ih = 200;
    const h = margin.t + ih + margin.b;
    const x = d3.scaleLinear().domain([0, bins - 1]).range([margin.l, margin.l + iw]);
    const maxY = d3.max(ser, d => Math.max(d.bw, d.c)) || 1;
    const y = d3.scaleLinear().domain([0, maxY]).nice().range([margin.t + ih, margin.t]);
    const svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    ser.forEach((d, i) => {
      const x0 = x(i) - (x(1) - x(0)) / 2;
      const ww = (x(1) - x(0)) * 0.92;
      svg.append("rect").attr("x", x0).attr("y", margin.t).attr("width", ww).attr("height", ih)
        .attr("fill", PAL[i % 4]).attr("opacity", 0.08).attr("stroke", "none");
    });
    const areaBw = d3.area().x((_, i) => x(i)).y0(y(0)).y1(d => y(d.bw)).curve(d3.curveMonotoneX);
    const areaC = d3.area().x((_, i) => x(i)).y0(y(0)).y1(d => y(d.c)).curve(d3.curveMonotoneX);
    svg.append("path").attr("fill", PAL[0]).attr("fill-opacity", 0.45).attr("stroke", PAL[0]).attr("stroke-width", 3)
      .attr("d", areaBw(ser));
    svg.append("path").attr("fill", PAL[3]).attr("fill-opacity", 0.4).attr("stroke", PAL[3]).attr("stroke-width", 3)
      .attr("d", areaC(ser));
    svg.append("text").attr("x", margin.l).attr("y", 20).attr("fill", PAL[0]).style("font-size", "10px").text("● 黑白（按样本顺序分桶）");
    svg.append("text").attr("x", margin.l + 220).attr("y", 20).attr("fill", PAL[3]).style("font-size", "10px").text("● 彩色");
    let hasL = 0, noL = 0;
    list.forEach(r => { if (norm(r[F.图片])) hasL++; else noL++; });
    svg.append("text").attr("x", margin.l).attr("y", h - 10).attr("fill", "#777").style("font-size", "9px")
      .text("图片列：有链接 " + hasL + " 条 · 无链接 " + noL + " 条（可用顶栏筛选）");
  }

  function chartBarsPicto(container, key, rows) {
    const agg = aggregate(rows, key).slice(0, 5);
    if (!agg.length) return;
    const w = chartBoxW(container);
    const margin = { t: 24, r: 16, b: 72, l: 16 };
    const iw = w - margin.l - margin.r;
    const ih = 160;
    const h = margin.t + ih + margin.b;
    const max = d3.max(agg, d => d.count) || 1;
    const xb = d3.scaleBand().domain(agg.map(d => d.key)).range([margin.l, margin.l + iw]).padding(0.28);
    const y = d3.scaleLinear().domain([0, max]).range([margin.t + ih, margin.t]);
    const svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    agg.forEach((d, i) => {
      const x0 = xb(d.key);
      const bw = xb.bandwidth();
      svg.append("rect").attr("x", x0).attr("y", y(0)).attr("width", bw).attr("height", 0)
        .attr("fill", PAL[i % 4]).attr("stroke", "#fff").attr("stroke-width", 3)
        .style("cursor", "pointer")
        .on("click", () => setFilter(key, d.key))
        .transition().duration(500).delay(i * 70).attr("y", y(d.count)).attr("height", y(0) - y(d.count));
      const ix = x0 + bw / 2 - 16;
      const iy = margin.t + ih + 10;
      const g = svg.append("g").attr("transform", "translate(" + ix + "," + iy + ")");
      for (let r = 0; r < 4; r++) for (let c = 0; c < 4; c++) {
        g.append("rect").attr("x", c * 8).attr("y", r * 8).attr("width", 6).attr("height", 6)
          .attr("fill", ((r + c + i) % 3 === 0) ? PAL[2] : "#222").attr("stroke", "#444").attr("stroke-width", 1);
      }
    });
  }

  function chartRidgeWordcount(container, rows) {
    const aggPh = sortPhases(aggregate(rows, F.阶段));
    const phases = aggPh.map(d => d.key);
    if (!phases.length) return;
    const w = chartBoxW(container);
    const maxW = 12;
    const rowH = 52;
    const margin = { l: 108, r: 24, t: 16, b: 32 };
    const iw = w - margin.l - margin.r;
    const plotBottom = margin.t + phases.length * rowH;
    const h = plotBottom + margin.b;
    const x = d3.scaleLinear().domain([0, maxW]).range([margin.l, margin.l + iw]);
    const svg = d3.select(container).append("svg").attr("class", "chart-svg chart-pixel-svg").attr("width", w).attr("height", h);
    phases.forEach((ph, pi) => {
      const sub = rows.filter(r => norm(r[F.阶段]) === ph);
      const hist = d3.range(0, maxW + 1).map(v => ({ v, n: 0 }));
      sub.forEach(r => {
        const v = Math.min(maxW, Math.max(0, +r[F.字数] | 0));
        if (!isNaN(v)) hist[v].n++;
      });
      const m = d3.max(hist, d => d.n) || 1;
      const yb = margin.t + pi * rowH + rowH - 8;
      const y0 = margin.t + pi * rowH + 8;
      const ys = d3.scaleLinear().domain([0, m]).range([yb, y0]);
      const area = d3.area().x(d => x(d.v)).y0(yb).y1(d => ys(d.n)).curve(d3.curveMonotoneX);
      svg.append("path").attr("fill", PAL[pi % 4]).attr("fill-opacity", 0.35).attr("stroke", PAL[pi % 4]).attr("stroke-width", 2)
        .attr("d", area(hist)).style("cursor", "pointer")
        .on("click", () => setPhase(ph));
      svg.append("text").attr("x", margin.l - 8).attr("y", y0 + (rowH - 16) / 2).attr("text-anchor", "end")
        .attr("fill", "#ccc").style("font-size", "10px").text(ph.length > 8 ? ph.slice(0, 7) + "…" : ph);
    });
    svg.append("g").attr("transform", "translate(0," + plotBottom + ")")
      .call(d3.axisBottom(x).ticks(7).tickFormat(d3.format("d")))
      .call(g => g.select(".domain").attr("stroke", "#666").attr("stroke-width", 2))
      .selectAll("text").attr("fill", "#888").style("font-size", "9px");
    svg.append("text").attr("x", margin.l + iw / 2).attr("y", h - 8).attr("text-anchor", "middle").attr("fill", "#666").style("font-size", "8px")
      .text("横轴：字数 0–12");
  }

