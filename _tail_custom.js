
  let narrativeLayerCleanup = null;
  let narrativeLastIdx = -1;
  let narrativeTick = 0;

  const CHART_NARRATIVE_TEXTS = [
    "【数据总结·人物原型】\n多类「脸」与身体符号并存：张学友系、教皇、金馆长、熊猫本体等共同构成语义池。包装度横轴反映梗是否依赖语境与修辞。\n\n【对应本图】\n每行一原型，横轴为情绪包装度 1–5；点缩略图可筛该原型。",
    "【数据总结·传播阶段】\n早期原型 → 熊猫头形成 → 泛化扩散，样本量与视觉策略随阶段变化。\n\n【对应本图】\n折线连接各阶段条数，点按阶段筛选。",
    "【数据总结·传播平台】\n贴吧约 51%，QQ 等约 30%，论坛约 12%。贴吧为第一入口，说明早期更偏公共讨论与灌水语境，再进入熟人聊天场景。\n\n【对应本图】\n横向百分比条对比各平台占比，可筛选观察子集。",
    "【数据总结·动作特征】\n无动作约 47%，有动作合计约 53%；手势、肢体姿态、持物/道具等占比较高。语义不只靠「脸」，而常靠身体与道具补全。\n\n【对应本图】\n同心环每条一类动作，弧长为占比；点击可筛选。",
    "【数据总结·情绪是否直接】\n直接约 70%，间接约 30%。整体仍以高效率直给为主，但间接表达已不可忽视（反讽、缓冲、阴阳等）。\n\n【对应本图】\n环形图对比直接 / 间接，点击扇区筛选。",
    "【数据总结·图像来源】\n真人表情截图再加工约 79%，网络拼接二创约 19%，熊猫实拍原图极少。说明流行后已弱依赖真实熊猫图像，而依赖人脸 + 框架 + 文字嫁接。\n\n【对应本图】\n雷达半径为相对最大值的条数比例，点击辐条筛选来源类型。",
    "【数据总结·黑白彩色与画质】\n黑白约 93%，彩色约 7%，符合低成本、快改、弱精修的亚文化视觉习惯。低清晰度占多数，传播重辨识度与可改造性，而非画质。\n\n【对应本图】\n按当前筛选结果分桶叠合黑白与彩色曲线；底部汇总含链接条数。",
    "【数据总结·模板类型】\n拼接模板约 63%，空白模板约 37%。主流不是单张原图，而是可反复改字、改语境的模板机制。\n\n【对应本图】\n柱形为模板类型 Top5，下附像素块示意；点击柱筛选。",
    "【数据总结·阶段 × 字数】\n多数图带字，图文共同表意：图像打底，文字定态度与语气。各阶段字数分布可用山脊面积观察集中区间。\n\n【对应本图】\n每行一阶段，横轴字数 0–12，面积为分布；点击带筛选阶段。"
  ];

  function formatNarrativeHtml(raw) {
    var s = esc(String(raw || ""));
    s = s.replace(/【([^】]*)】/g, '<span class="narr-btitle">【$1】</span>');
    s = s.replace(/(\d+(?:\.\d+)?%)/g, '<span class="narr-hl narr-hl--y">$1</span>');
    s = s.replace(/「([^」]+)」/g, '<span class="narr-hl narr-hl--p">「$1」</span>');
    s = s.replace(/\n/g, "<br>");
    return s;
  }

  function applyNarrativeText(innerEl, text, tk) {
    if (tk !== narrativeTick) return;
    innerEl.classList.remove("narr-inner-out", "narr-box-reveal-prep", "narr-box-reveal-run");
    innerEl.innerHTML = formatNarrativeHtml(text || "");
  }

  function setupChartNarrativeLayer() {
    if (narrativeLayerCleanup) {
      narrativeLayerCleanup();
      narrativeLayerCleanup = null;
    }
    narrativeLastIdx = -1;
    const layer = document.getElementById("narrative-scroll-layer");
    const inner = document.getElementById("narrative-scroll-inner");
    const dock = document.getElementById("viz-side-dock");
    const chartsHost = document.getElementById("charts");
    if (!layer || !inner || !dock) return;

    const panels = [].slice.call(document.querySelectorAll(".chart-panel-split"));
    if (!panels.length) return;

    const panelByNarrIdx = {};
    panels.forEach(function (p) {
      const ix = parseInt(p.getAttribute("data-narr-idx"), 10);
      if (!isNaN(ix) && ix >= 0) panelByNarrIdx[ix] = p;
    });

    function syncChartsNarrShift() {
      if (!chartsHost) return;
      if (dock.classList.contains("visible")) chartsHost.classList.add("charts--narr-open");
      else chartsHost.classList.remove("charts--narr-open");
    }

    function syncChartPanelsFocus(activeIdx) {
      panels.forEach(function (p) {
        p.classList.remove("chart-focus", "chart-dim");
        if (activeIdx < 0) return;
        const ix = parseInt(p.getAttribute("data-narr-idx"), 10);
        if (isNaN(ix)) return;
        if (ix === activeIdx) p.classList.add("chart-focus");
        else p.classList.add("chart-dim");
      });
    }

    var stepper = document.getElementById("chart-stepper");
    function syncStepper(activeIdx) {
      if (!stepper) return;
      var chartsEl = document.getElementById("charts");
      if (activeIdx >= 0) {
        stepper.classList.add("visible");
        if (chartsEl) chartsEl.classList.add("charts--stepper-open");
      } else {
        stepper.classList.remove("visible");
        if (chartsEl) chartsEl.classList.remove("charts--stepper-open");
      }
      stepper.querySelectorAll(".stepper-item").forEach(function (row) {
        var dot = row.querySelector(".stepper-dot");
        if (!dot) return;
        var si = parseInt(dot.getAttribute("data-step-idx"), 10);
        if (si === activeIdx) {
          dot.classList.add("active");
          row.classList.add("stepper-item--active");
        } else {
          dot.classList.remove("active");
          row.classList.remove("stepper-item--active");
        }
      });
    }

    function allowNarrativeHandoff(fromIdx, toIdx, vh) {
      if (toIdx < 0) return false;
      const pad = Math.max(48, vh * 0.07);
      if (fromIdx < 0) {
        if (toIdx === 0) return true;
        const prevChart = panelByNarrIdx[toIdx - 1];
        if (!prevChart) return true;
        return prevChart.getBoundingClientRect().bottom <= pad;
      }
      if (toIdx > fromIdx) {
        const prevChart = panelByNarrIdx[toIdx - 1];
        if (!prevChart) return true;
        return prevChart.getBoundingClientRect().bottom <= pad;
      }
      if (toIdx < fromIdx) {
        const nextChart = panelByNarrIdx[toIdx + 1];
        if (!nextChart) return true;
        return nextChart.getBoundingClientRect().top >= vh - pad;
      }
      return true;
    }

    function update() {
      const vh = window.innerHeight || 600;
      const mid = vh * 0.48;
      let best = -1;
      let bestScore = 0;
      panels.forEach(function (p) {
        const idx = parseInt(p.getAttribute("data-narr-idx"), 10);
        if (isNaN(idx) || idx < 0) return;
        const r = p.getBoundingClientRect();
        const overlap = Math.min(r.bottom, vh) - Math.max(r.top, 0);
        const visible = overlap > 0 ? overlap / Math.max(1, Math.min(r.height, vh)) : 0;
        const cy = (r.top + r.bottom) / 2;
        const dist = Math.abs(cy - mid);
        const score = visible * (1 / (1 + dist / Math.max(vh, 1)));
        if (score > bestScore) {
          bestScore = score;
          best = idx;
        }
      });

      if (best >= 0 && bestScore > 0.06) {
        if (narrativeLastIdx !== best && !allowNarrativeHandoff(narrativeLastIdx, best, vh)) {
          syncChartsNarrShift();
          var hold = narrativeLastIdx >= 0 ? narrativeLastIdx : -1;
          syncChartPanelsFocus(hold);
          syncStepper(hold);
          return;
        }
        const tk = ++narrativeTick;
        dock.classList.add("visible");
        layer.classList.add("visible");
        applyNarrativeText(inner, CHART_NARRATIVE_TEXTS[best] || "", tk);
        narrativeLastIdx = best;
        inner.classList.remove("narr-inner-out");
        syncChartsNarrShift();
        syncChartPanelsFocus(best);
        syncStepper(best);
      } else {
        narrativeTick++;
        dock.classList.remove("visible");
        layer.classList.remove("visible");
        inner.innerHTML = "";
        narrativeLastIdx = -1;
        syncChartsNarrShift();
        syncChartPanelsFocus(-1);
        syncStepper(-1);
      }
    }

    var narrRaf = 0;
    function scheduleNarrativeUpdate() {
      if (narrRaf) return;
      narrRaf = requestAnimationFrame(function () {
        narrRaf = 0;
        update();
      });
    }

    var io;
    try {
      io = new IntersectionObserver(scheduleNarrativeUpdate, {
        root: null,
        threshold: [0, 0.05, 0.12, 0.25, 0.45, 0.65, 1],
        rootMargin: "-10% 0px -14% 0px"
      });
      panels.forEach(function (p) {
        io.observe(p);
      });
    } catch (e1) { /* ignore */ }

    window.addEventListener("scroll", scheduleNarrativeUpdate, { passive: true });
    window.addEventListener("resize", scheduleNarrativeUpdate, { passive: true });

    narrativeLayerCleanup = function () {
      try {
        if (io) io.disconnect();
      } catch (e2) { /* ignore */ }
      window.removeEventListener("scroll", scheduleNarrativeUpdate);
      window.removeEventListener("resize", scheduleNarrativeUpdate);
    };

    scheduleNarrativeUpdate();
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
      "人物原型 · 包装度分布",
      "左列原型、横轴情绪包装度 1–5；缩略图可悬停放大，点击筛选该原型。",
      function (box) {
        chartBeeswarmProto(box, rowsMarg(F.原型));
      },
      "Protagonist"
    );
    addPanel(
      "阶段 · 样本数量分布",
      "传播阶段 × 样本数；点击节点筛选阶段。",
      function (box) {
        chartSplinePhases(box, rowsMarg(F.阶段));
      },
      "Phase count"
    );
    addPanel(
      "传播平台分布图",
      "0–100% 虚线格与色块图例；点击条筛选平台。",
      function (box) {
        chartHBarPercentLegend(box, F.平台, rowsMarg(F.平台));
      },
      "Platforms"
    );
    addPanel(
      "动作比例分布图",
      "每环一类动作占比；点击弧筛选。",
      function (box) {
        chartRadialRingBars(box, F.动作, rowsMarg(F.动作));
      },
      "Actions"
    );
    addPanel(
      "表达方式占比图：直接 vs 间接",
      "环形对比直接 / 间接；点击扇区筛选。",
      function (box) {
        chartDonutCallouts(box, F.直接, rowsMarg(F.直接));
      },
      "Directness"
    );
    addPanel(
      "图像来源雷达分布图",
      "真人表情截图再加工、网络拼接二创、熊猫实拍原图",
      function (box) {
        chartPolarSpider(box, F.来源, rowsMarg(F.来源));
      },
      "Sources"
    );
    addPanel(
      "双色面积 · 分带背景",
      "横轴=把当前表从上到下按固定行数切段后的段号；纵轴=每段内黑白/彩色条数。",
      function (box) {
        chartDualAreaStripes(box, rowsExact());
      },
      "B/W bands"
    );
    addPanel(
      "模版类型分布图",
      "模板类型：拼接模版、空白模版；点击柱筛选。",
      function (box) {
        chartBarsPicto(box, F.模板, rowsMarg(F.模板));
      },
      "Templates"
    );
    addPanel(
      "不同阶段阶段 × 字数分布图",
      "每阶段字数分布；点击带筛选阶段。",
      function (box) {
        chartRidgeWordcount(box, rowsMarg(F.阶段));
      },
      "Word ridge"
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

  function render() {
    const statLine = document.getElementById("stat-line");
    const nextN = String(rowsExact().length);
    const totalN = String(ALL.length);
    if (statLine) {
      if (statLine.dataset.ready === "1" && statLine.dataset.lastMatch !== nextN) {
        statLine.classList.remove("stat-pulse");
        void statLine.offsetWidth;
        statLine.classList.add("stat-pulse");
      }
      statLine.dataset.ready = "1";
      statLine.dataset.lastMatch = nextN;
      statLine.innerHTML = "";
      pixelRevealPlainText(statLine, "样本数量 " + nextN + " / " + totalN + " 张", 0);
    }
    renderFiltersBar();
    renderPhases();
    renderCharts();
  }

  function updateChartScrollDepth() {
    var vh = window.innerHeight || 600;
    var mid = vh * 0.5;
    document.querySelectorAll(".chart-snap-page.chart-panel-split").forEach(function (sec) {
      var r = sec.getBoundingClientRect();
      var cy = (r.top + r.bottom) / 2;
      var dist = Math.abs(cy - mid) / Math.max(vh, 1);
      var n = Math.max(0, Math.min(1, 1 - dist * 1.15));
      sec.style.setProperty("--viz-n", n.toFixed(4));
    });
  }

  function onScroll() {
    const p = document.getElementById("progress");
    const max = document.body.scrollHeight - innerHeight || 1;
    const pct = scrollY / max;
    if (p) {
      var vw = window.innerWidth || 1200;
      p.style.width = pct * vw + "px";
    }
    updateChartScrollDepth();
    var tp = document.getElementById("title-parallax");
    if (tp) tp.style.transform = "translateY(" + scrollY * 0.045 + "px)";
  }

  window.addEventListener("scroll", onScroll, { passive: true });

  function initPixelCube() {
    const el = document.getElementById("pixelCube");
    const hero = document.querySelector(".hero-pixel");
    if (!el || !hero) return;
    let ryDeg = 0;
    el.addEventListener(
      "wheel",
      function (e) {
        e.preventDefault();
        ryDeg += e.deltaY * 0.11;
        el.style.setProperty("--cube-ry", ryDeg + "deg");
      },
      { passive: false }
    );
    hero.addEventListener("mousemove", function (e) {
      const r = hero.getBoundingClientRect();
      const nx = (e.clientX - r.left) / Math.max(r.width, 1) - 0.5;
      const ny = (e.clientY - r.top) / Math.max(r.height, 1) - 0.5;
      el.style.setProperty("--cube-rx", ny * -10 + "deg");
      el.style.setProperty("--cube-ry-mouse", nx * 14 + "deg");
    });
    hero.addEventListener("mouseleave", function () {
      el.style.setProperty("--cube-rx", "0deg");
      el.style.setProperty("--cube-ry-mouse", "0deg");
    });
    function frame() {
      ryDeg += 0.018;
      el.style.setProperty("--cube-ry", ryDeg + "deg");
      requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  function initPixelTextReveal() {
    const h1 = document.getElementById("pixTitleHost");
    const sub = document.getElementById("pixSubHost");
    if (h1 && !h1.dataset.pixDone) {
      const t = h1.textContent;
      pixelRevealPlainText(h1, t, 0);
      h1.dataset.pixDone = "1";
    }
    if (sub && !sub.dataset.pixDone) {
      const t = sub.textContent;
      pixelRevealPlainText(sub, t, 0.12);
      sub.dataset.pixDone = "1";
    }
  }

  function initCubeFacesPixelText() {
    document.querySelectorAll(".cube-face.side .face-num").forEach(function (el, i) {
      const t = el.textContent;
      el.textContent = "";
      pixelRevealPlainText(el, t, 0.03 + i * 0.04);
    });
    document.querySelectorAll(".cube-face.side .cube-text").forEach(function (el, i) {
      const t = el.textContent;
      el.textContent = "";
      pixelRevealPlainText(el, t, 0.08 + i * 0.05);
    });
  }

  function initStaticPagePixelText() {
    if (document.body.dataset.pagePixInit === "1") return;
    document.body.dataset.pagePixInit = "1";
    const hint = document.querySelector(".hero-scroll-hint");
    if (hint) pixelRevealElementText(hint);
    const dockTitle = document.querySelector(".filters-dock-title");
    if (dockTitle) pixelRevealElementText(dockTitle);
    const dockArrow = document.querySelector(".filters-dock-arrow");
    if (dockArrow) pixelRevealElementText(dockArrow);
    const badge = document.querySelector(".panel-phase-strip .badge");
    if (badge) pixelRevealElementText(badge);
    const ph2 = document.querySelector(".panel-phase-strip .h2-compact");
    if (ph2) pixelRevealElementText(ph2);
    const phint = document.querySelector(".panel-phase-strip .hint-compact");
    if (phint) pixelRevealElementText(phint);
    const foot = document.querySelector("footer.foot");
    if (foot) pixelRevealElementText(foot);
    document.querySelectorAll(".cube-face.cap-top.side, .cube-face.cap-bottom.side").forEach(function (cap) {
      const t = cap.textContent;
      cap.textContent = "";
      pixelRevealPlainText(cap, t, 0.12);
    });
  }

  function initScrollGuideBtn() {
    const btn = document.getElementById("scroll-guide-btn");
    if (!btn) return;
    btn.classList.remove("hidden");
    btn.addEventListener("click", function () {
      const firstChart = document.querySelector(".chart-panel-split");
      if (firstChart) firstChart.scrollIntoView({ behavior: "smooth", block: "center" });
      else window.scrollBy({ top: Math.min(innerHeight * 0.85, 640), behavior: "smooth" });
    });
  }

  function boot() {
    ALL = window.__ROWS__ || [];
    initPixelCube();
    initCubeFacesPixelText();
    initPixelTextReveal();
    initStaticPagePixelText();
    initScrollGuideBtn();
    render();
    onScroll();
    var t;
    window.addEventListener("resize", function () {
      clearTimeout(t);
      t = setTimeout(function () {
        render();
        onScroll();
      }, 250);
    });
  }

  boot();
})();
