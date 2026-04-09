# -*- coding: utf-8 -*-
"""从 场景一.html 组装 场景二.html：替换数据、字段映射、阶段条、scene2_charts_code.js 中 11 套图表与叙事文案。"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_JSON = ROOT / "scene2_data.json"
SCENE1 = ROOT / "场景一.html"
OUT = ROOT / "场景二.html"

HEADER_REPL = r'''  const F = {
    大阶段: "大阶段", 细分: "细分阶段", 当前图片: "当前图片", 原文件名: "原文件名", 图字: "图片文字",
    复杂度: "视觉复杂度", 字数: "文字字数", 黑白: "黑白/彩色", 情绪: "情绪判断", 动作: "动作特征",
    场景: "社交场景判断", 直接: "表达直接性", 包装: "包装程度", 原情: "原始情绪类型", 包后: "包装后的表达类型",
    关系: "关系对象类型", 风险: "关系风险等级"
  };
const FILTER_KEYS = [
    F.大阶段, F.细分, F.复杂度, F.字数, F.黑白, F.情绪, F.动作, F.场景, F.直接, F.包装, F.原情, F.包后, F.关系, F.风险
  ];
  const PAL = ["#F54595", "#59E2FD", "#6C58EE", "#FCE500"];
  const PAL_LEGEND = ["粉洋红", "青色", "紫色", "黄色"];
  /** 逐字显现：相邻字符延迟（秒），越小越快 */
  const PIX_CHAR_STAGGER = 0.0065;
  /** 右侧图注专用：更短间隔 */
  const PIX_CAP_STAGGER = 0.0018;
  const SVG_NS = "http://www.w3.org/2000/svg";
  /** 优先与 场景二.html 同目录的 对应图片2/；失败时回退 data-img-alt（见立方体与阶段条脚本） */
  const IMG_BASE = "对应图片2/";
  const IMG_BASE_ALT = "../数据/场景二/对应图片2/";
  /** 坐标区：主网格 + 细网格（场景二加密，对齐参考稿） */
  const CHART_GRID_STROKE = "rgba(255,255,255,0.5)";
  const CHART_GRID_W = 0.55;
  const CHART_GRID_FINE = "rgba(255,255,255,0.11)";
  const CHART_GRID_FINE_W = 0.32;
  const CHART_AXIS_DOMAIN_STROKE = "rgba(255,255,255,0.72)";
  const CHART_AXIS_TICK_STROKE = "rgba(255,255,255,0.48)";
  const CHART_AXIS_TICK_W = 0.72;
'''

# NEW_CHARTS 由 main() 从 scene2_charts_code.js 读取

NARRATIVE_NEW = r'''  const CHART_NARRATIVE_TEXTS = [
    "【数据总结·细分阶段】\n三阶段样本量与结构不同：动作模板化偏「梗图原型」，回复工具化强化可发送性，聊天迁移则把冲突与关系试探写进长句。\n\n【对应本图】\n环形 + 外引线标注占比；无场景一同款的同心射线格，点击扇区即筛细分阶段。",
    "【数据总结·视觉复杂度】\n1—3 级占绝大多数，脸+字+少量动作即可传意。\n\n【对应本图】\n五轴极坐标上闭合折线围成面（周末式放射爆刺形态），与场景一极坐标柱/雷达读法不同；点半径筛复杂度。",
    "【数据总结·多维交叉】\n同一阶段内包装度与字数共同刻画「做图成本」；情绪用色区分。\n\n【对应本图】\n三行=三细分阶段，横轴包装 1—5，圆面积≈字数；左侧虚线分隔类目，悬停看图内字。",
    "【数据总结·情绪】\n无语/调侃、无语/吐槽、敷衍/缓冲等最常见，承担轻负面与缓冲。\n\n【对应本图】\n样条曲线 + 下垂锚线 + 大白点（参考图2中线图范式），点击筛情绪。",
    "【数据总结·社交场景】\n通用聊天占主导，其次群聊互损、私聊、工作校园等。\n\n【对应本图】\n横向条长相对最长场景归一为 100%，右侧色点对应图例；非树图、非华夫饼。",
    "【数据总结·黑白/彩色】\n黑白为主，彩色约占两成，模板感强。\n\n【对应本图】\n按三细分阶段叠双色面积 + 边界线，竖向色带区分阶段；读青黄叠层与趋势线，而非单列饼图。",
    "【数据总结·动作】\n无动作过半，其余多为打电脑、摆手、打电话等语气动作。\n\n【对应本图】\n象形柱 + 柱顶节点线 + 柱下符号块；与棒棒糖、堆叠条均不同。",
    "【数据总结·包装度】\n低包装仍多，中高包装承担阴阳、自嘲、拖延缓冲等。\n\n【对应本图】\n脊线/Joy：每行一阶段，横轴包装 1—5，峰高为相对占比；点击填色筛阶段。",
    "【数据总结·包装占比】\n各级包装在全体样本中的份额可一眼对比。\n\n【对应本图】\n同心温色环 + 深色扫角弧 + 引线（参考图4）；由内到外为包装 1→5。",
    "【数据总结·包装链】\n原情绪多无语/无奈、不爽/攻击等，包装后常落轻吐槽、阴阳、自嘲。\n\n【对应本图】\n左右列 Top5，贝塞尔弦带粗细=路径条数；悬停看「原情→包后」配对，点击双筛。",
    "【数据总结·直接性×包装】\n直接、半直接与包装度交叉，可见「怎么说」与「包几层」的关系。\n\n【对应本图】\n离散矩阵格 + 气泡面积=交叉条数；悬停主情绪与缩略图，非连续散点云、非热力格。"
  ];'''


def patch_prefix(prefix: str) -> str:
    """替换 F、FILTER_KEYS、PAL…SVG_NS 整块并加入 IMG_BASE。"""
    prefix = re.sub(
        r"  const F = \{[\s\S]*?  const CHART_AXIS_TICK_W = [^;]+;",
        HEADER_REPL.rstrip(),
        prefix,
        count=1,
    )
    prefix = re.sub(
        r"  function thumb\(r\) \{[\s\S]*?\n  \}",
        r"""  function thumbEncodedPath(fn) {
    const f = norm(fn);
    return f ? f.split("/").map(encodeURIComponent).join("/") : "";
  }
  function thumb(r) {
    const u = norm(r[F.当前图片]);
    if (u && (u.startsWith("http") || u.startsWith("data:"))) return u;
    if (u) return u.indexOf("/") >= 0 || u.startsWith(".") ? u : IMG_BASE + encodeURIComponent(u);
    const p = thumbEncodedPath(r[F.原文件名]);
    return p ? IMG_BASE + p : "";
  }
  function thumbAltUrl(r) {
    const p = thumbEncodedPath(r[F.原文件名]);
    return p && typeof IMG_BASE_ALT !== "undefined" && IMG_BASE_ALT ? IMG_BASE_ALT + p : "";
  }""",
        prefix,
        count=1,
    )
    prefix = re.sub(
        r"  function setPhase\(v\) \{[\s\S]*?\n  \}",
        r"""  function setPhase(v) {
    filters[F.细分] = v ? norm(v) : null;
    bumpViz();
    render();
  }""",
        prefix,
        count=1,
    )
    prefix = re.sub(
        r"  function renderPhases\(\) \{[\s\S]*?\n  \}",
        r"""  function renderPhases() {
    const host = document.getElementById("phases");
    host.innerHTML = "";
    const rows = rowsMarg(F.细分);
    const cur = filters[F.细分];
    const PHASE_STRIP = [
      { label: "QQ/微信早期（全部）", key: null, isAll: true },
      { label: "动作模板化", key: "动作模板化", isAll: false },
      { label: "回复工具化", key: "回复工具化", isAll: false },
      { label: "聊天迁移", key: "聊天迁移", isAll: false }
    ];

    function block(entry, samples, count) {
      const isAll = entry.isAll;
      const label = entry.key;
      const on = isAll ? !cur : norm(cur) === norm(label);
      const div = document.createElement("div");
      div.className = "phase-block phase-block--strip" + (on ? " on" : "");
      div.innerHTML = "<h3>" + esc(entry.label) + "</h3><div class='meta'>" + count + " 条</div>";
      const thumbs = document.createElement("div");
      thumbs.className = "phase-thumbs phase-thumbs--strip";
      samples.filter(s => thumb(s)).slice(0, 24).forEach(s => {
        const img = document.createElement("img");
        img.src = thumb(s);
        const altu = thumbAltUrl(s);
        if (altu) img.setAttribute("data-img-alt", altu);
        img.alt = "";
        img.addEventListener("error", function () {
          const a = this.getAttribute("data-img-alt");
          if (a && !this.dataset._fb) { this.dataset._fb = "1"; this.src = a; }
        });
        img.addEventListener("mouseenter", ev => {
          const memo = norm(s[F.图字]) || "（无图内字）";
          tipShow(ev, `<img src="${esc(thumb(s))}" alt="">` + esc(memo));
        });
        img.addEventListener("mousemove", moveTip);
        img.addEventListener("mouseleave", tipHide);
        thumbs.appendChild(img);
      });
      div.appendChild(thumbs);
      div.addEventListener("click", () => setPhase(isAll ? null : label));
      host.appendChild(div);
    }

    PHASE_STRIP.forEach(entry => {
      if (entry.isAll) {
        block(entry, rows, rows.length);
        return;
      }
      const samples = rows.filter(r => norm(r[F.细分]) === norm(entry.key));
      block(entry, samples, samples.length);
    });
    requestAnimationFrame(function () {
      document.querySelectorAll("#phases .phase-block h3").forEach(function (h, i) {
        const t = h.textContent;
        h.textContent = "";
        pixelRevealPlainText(h, t, i * 0.014);
      });
      document.querySelectorAll("#phases .phase-block .meta").forEach(function (m, i) {
        const t = m.textContent;
        m.textContent = "";
        pixelRevealPlainText(m, t, 0.04 + i * 0.014);
      });
    });
  }""",
        prefix,
        count=1,
    )
    prefix = re.sub(
        r'const PHASE_ORDER = \[[^\]]*\];',
        'const PHASE_ORDER = ["动作模板化", "回复工具化", "聊天迁移"];',
        prefix,
        count=1,
    )
    prefix = re.sub(
        r"  function aggregate\(rows, key\) \{[\s\S]*?\n  \}",
        r"""  function aggregate(rows, key) {
    const m = new Map();
    for (const r of rows) {
      let v = r[key];
      if (key === F.字数 || key === F.复杂度 || key === F.包装) v = String(v == null ? "" : v);
      else v = norm(v) || "（空）";
      m.set(v, (m.get(v) || 0) + 1);
    }
    return [...m].map(([key, count]) => ({ key, count })).sort((a, b) => b.count - a.count);
  }""",
        prefix,
        count=1,
    )
    return prefix


def main():
    html = SCENE1.read_text(encoding="utf-8")
    data = json.loads(DATA_JSON.read_text(encoding="utf-8"))
    rows_js = json.dumps(data["rows"], ensure_ascii=False)
    html = re.sub(
        r"<script>window\.__ROWS__ = .*?</script>",
        "<script>window.__ROWS__ = " + rows_js + ";</script>",
        html,
        count=1,
        flags=re.DOTALL,
    )

    i0 = html.index("  const F = {")
    i1 = html.index("\n  function render() {")
    middle_old = html[i0:i1]

    i_bee = middle_old.index("  function chartBeeswarmProto")
    prefix = patch_prefix(middle_old[:i_bee])
    new_charts = "\n" + (ROOT / "scene2_charts_code.js").read_text(encoding="utf-8")
    ix_new_rc = new_charts.index("  function renderCharts()")
    new_chart_funcs = new_charts[:ix_new_rc]
    new_render_charts = new_charts[ix_new_rc:]
    i_narr = middle_old.index("  let narrativeLayerCleanup")
    i_rc_old = middle_old.index("  function renderCharts()")
    narrative_slice = middle_old[i_narr:i_rc_old]
    # 必须用 lambda：若把 repl 当作普通字符串，re.sub 会把其中的 \n 当成真实换行，弄断 JS 引号。
    # 勿用 .strip()：会去掉行首「  const」前的空格，破坏缩进。
    narrative_slice = re.sub(
        r"  const CHART_NARRATIVE_TEXTS = \[[\s\S]*?\n  \];",
        lambda _m: NARRATIVE_NEW.strip("\n\r\t"),
        narrative_slice,
        count=1,
    )
    middle_new = prefix + new_chart_funcs + narrative_slice + new_render_charts

    html = html[:i0] + middle_new + html[i1:]

    html = html.replace(
        "贴吧早期熊猫头表情包数据可视化",
        "QQ/微信早期熊猫头表情包数据可视化（场景二）",
    )
    html = html.replace(
        "本研究通过对 43 组熊猫头表情包的多维度编码统计，完整呈现其早期从原型诞生、形态演变到全网传播的文化特征与发展规律。",
        "本页基于 130 张样本，聚焦 QQ/微信早期：细分阶段、情绪与包装链、社交场景与关系风险等多维编码，呈现熊猫头作为「回复工具」的语义与传播特征。",
        1,
    )
    html = html.replace("早期形成阶段分期", "细分阶段（场景二）", 1)
    html = html.replace("点击项筛选阶段，再点同一项可取消。", "点击项筛选细分阶段；缩略图悬停显示图内文字。", 1)
    html = html.replace(
        "本次分析系统梳理了熊猫头表情包的演化脉络与传播特征，以详实样本展现了这一经典网络符号的文化价值与传播逻辑。",
        "场景二样本来自 QQ/微信早期熊猫头，侧重「回复工具化」与情绪包装链；路径与图片位于 ../数据/场景二/ 。",
        1,
    )

    _cube_onerr = ' onerror="var a=this.getAttribute(\'data-img-alt\');if(a&&!this.dataset._fb){this.dataset._fb=\'1\';this.src=a;}"'
    html = html.replace(
        'src="meme-img/22.png"',
        'src="对应图片2/37.png" data-img-alt="../数据/场景二/对应图片2/37.png"' + _cube_onerr,
        1,
    )
    html = html.replace(
        'src="meme-img/264.png"',
        'src="对应图片2/199.png" data-img-alt="../数据/场景二/对应图片2/199.png"' + _cube_onerr,
        1,
    )
    html = html.replace(
        'src="meme-img/284.png"',
        'src="对应图片2/109.png" data-img-alt="../数据/场景二/对应图片2/109.png"' + _cube_onerr,
        1,
    )
    html = html.replace(
        'src="meme-img/268.png"',
        'src="对应图片2/38.png" data-img-alt="../数据/场景二/对应图片2/38.png"' + _cube_onerr,
        1,
    )

    cube_txts = [
        (
            "① 场景二·情绪功能",
            "无语、吐槽、敷衍与轻度攻击最常见；熊猫头把难直接说的话改成「表情包式」输出，降低尴尬与冲突感。",
        ),
        (
            "② 场景二·模板与视觉",
            "黑白为主、复杂度集中在 1—3 级：脸+字+少量动作即可传意，强模板、弱精致修图。",
        ),
        (
            "③ 场景二·社交场景",
            "通用聊天占主导，是先成为泛用回复语言，再向群聊、工作、私聊等语境渗透。",
        ),
        (
            "④ 场景二·包装与风险",
            "原始情绪多无语/无奈与不爽，包装后常为轻吐槽、阴阳、自嘲；关系对象以泛聊天为主，风险多落在低—中区。",
        ),
    ]
    cube_blocks = [
        (
            '<div class="face-num">① 阶段总结——风格</div>\n            <div class="cube-text">熊猫头整体以黑白、低清晰度、真人表情截图再加工为主，说明它最初和早期传播形态，确实更接近“低门槛、可快速复制”的网络拼贴图。</div>',
            f'<div class="face-num">{cube_txts[0][0]}</div>\n            <div class="cube-text">{cube_txts[0][1]}</div>',
        ),
        (
            '<div class="face-num">② 阶段总结——动作</div>\n            <div class="cube-text">动作并不是绝对主导，但“有动作”已经占到 23/43，说明熊猫头并不只是“静态脸部表情”，而是在中后期逐渐依赖手势、姿态、道具来增强语义。</div>',
            f'<div class="face-num">{cube_txts[1][0]}</div>\n            <div class="cube-text">{cube_txts[1][1]}</div>',
        ),
        (
            '<div class="face-num">③ 阶段总结——传播平台</div>\n            <div class="cube-text">贴吧是最主要的早期传播平台，其次才是 QQ 等，这说明它最初更像公共讨论空间里的亚文化产物，后来再进入熟人聊天场景。</div>',
            f'<div class="face-num">{cube_txts[2][0]}</div>\n            <div class="cube-text">{cube_txts[2][1]}</div>',
        ),
        (
            '<div class="face-num">④ 阶段总结——创作</div>\n            <div class="cube-text">拼接模板多于空白模板，且图像来源高度依赖真人截图再加工，说明熊猫头不是“凭空设计出来”的，而是从真人表情素材中不断二创、模板化、语境化生成的。</div>',
            f'<div class="face-num">{cube_txts[3][0]}</div>\n            <div class="cube-text">{cube_txts[3][1]}</div>',
        ),
    ]
    for old_b, new_b in cube_blocks:
        if old_b not in html:
            raise SystemExit("Cube block not found, check 场景一.html whitespace")
        html = html.replace(old_b, new_b, 1)

    OUT.write_text(html, encoding="utf-8")
    print("Wrote", OUT, "chars", len(html))


if __name__ == "__main__":
    main()
