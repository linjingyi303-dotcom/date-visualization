# -*- coding: utf-8 -*-
import re
from pathlib import Path

base = Path(r"c:\Users\林靖怡\Desktop\数据可视化")
html_path = base / "场景三.html"
charts_path = base / "_scene3_charts_block.js"

html = html_path.read_text(encoding="utf-8")
new_charts = charts_path.read_text(encoding="utf-8")

html, n = re.subn(
    r"<script>window\.__ROWS__\s*=\s*\[.*?\];</script>",
    '<script src="scene3_data.js"></script>',
    html,
    count=1,
    flags=re.DOTALL,
)
if n != 1:
    raise SystemExit(f"__ROWS__ replace count={n}, expected 1")

start = html.find("  function chartDonutLeadersSub(container, rows) {")
end = html.find("  let narrativeLayerCleanup = null;", start)
if start < 0 or end < 0:
    raise SystemExit(f"chart markers missing start={start} end={end}")
html = html[:start] + new_charts + html[end:]

replacements = [
    (
        "<title>QQ/微信早期熊猫头表情包数据可视化（场景二）</title>",
        "<title>当下熊猫头表情包数据可视化（场景三）</title>",
    ),
    (
        """        w.s2CubeFaceError = function (img) {
          if (!img || !img.getAttribute) return;
          var fn = img.getAttribute("data-cube-file");
          if (!fn) return;
          var step = parseInt(img.getAttribute("data-cube-step") || "0", 10);
          /* 首地址已是 对应图片2/，避免 step0 再次指向同一路径导致死循环 */
          var urls = [
            "../数据/场景二/对应图片2/" + fn,
            "对应图片2/" + encodeURIComponent(fn),
            "../数据/场景二/对应图片2/" + encodeURIComponent(fn)
          ];""",
        """        w.s3CubeFaceError = function (img) {
          if (!img || !img.getAttribute) return;
          var fn = img.getAttribute("data-cube-file");
          if (!fn) return;
          var step = parseInt(img.getAttribute("data-cube-step") || "0", 10);
          /* 首地址已是 对应图片3/，避免 step0 再次指向同一路径导致死循环 */
          var urls = [
            "../数据/场景三/对应图片3/" + fn,
            "对应图片3/" + encodeURIComponent(fn),
            "../数据/场景三/对应图片3/" + encodeURIComponent(fn)
          ];""",
    ),
    (
        """          <div class="cube-face front side">
            <div class="face-num">① 场景二·情绪功能</div>
            <div class="cube-text">无语、吐槽、敷衍与轻度攻击最常见；熊猫头把难直接说的话改成「表情包式」输出，降低尴尬与冲突感。</div>
            <div class="cube-thumb">
              <img class="cube-face-img" data-cube-file="37.png" src="对应图片2/37.png" onerror="s2CubeFaceError(this)" alt="" decoding="async" />
                </div>
                </div>
          <div class="cube-face right side">
            <div class="face-num">② 场景二·模板与视觉</div>
            <div class="cube-text">黑白为主、复杂度集中在 1—3 级：脸+字+少量动作即可传意，强模板、弱精致修图。</div>
            <div class="cube-thumb">
              <img class="cube-face-img" data-cube-file="199.png" src="对应图片2/199.png" onerror="s2CubeFaceError(this)" alt="" decoding="async" />
            </div>
                </div>
          <div class="cube-face back side">
            <div class="face-num">③ 场景二·社交场景</div>
            <div class="cube-text">通用聊天占主导，是先成为泛用回复语言，再向群聊、工作、私聊等语境渗透。</div>
            <div class="cube-thumb">
              <img class="cube-face-img" data-cube-file="109.png" src="对应图片2/109.png" onerror="s2CubeFaceError(this)" alt="" decoding="async" />
            </div>
                    </div>
          <div class="cube-face left side">
            <div class="face-num">④ 场景二·包装与风险</div>
            <div class="cube-text">原始情绪多无语/无奈与不爽，包装后常为轻吐槽、阴阳、自嘲；关系对象以泛聊天为主，风险多落在低—中区。</div>
            <div class="cube-thumb">
              <img class="cube-face-img" data-cube-file="38.png" src="对应图片2/38.png" onerror="s2CubeFaceError(this)" alt="" decoding="async" />
                </div>
                    </div>""",
        """          <div class="cube-face front side">
            <div class="face-num">① 场景三·直接性与包装</div>
            <div class="cube-text">间接表达占多数；包装度多在 2—5 档，把真实情绪折成梗、礼貌壳或自嘲句式，适配当下群聊与评论区语境。</div>
            <div class="cube-thumb">
              <img class="cube-face-img" data-cube-file="144.png" src="对应图片3/144.png" onerror="s3CubeFaceError(this)" alt="" decoding="async" />
                </div>
                </div>
          <div class="cube-face right side">
            <div class="face-num">② 场景三·细分阶段</div>
            <div class="cube-text">从场景萌芽、关系分层到礼貌化与情绪包装，再到婉拒与万能模板：阶段越靠后，字数与修辞负担往往越高。</div>
            <div class="cube-thumb">
              <img class="cube-face-img" data-cube-file="32.png" src="对应图片3/32.png" onerror="s3CubeFaceError(this)" alt="" decoding="async" />
            </div>
                </div>
          <div class="cube-face back side">
            <div class="face-num">③ 场景三·社交功能</div>
            <div class="cube-text">轻吐槽、围观附和、自嘲摆烂、阴阳怪气等功能标签并存；同一张脸可在不同功能间切换，承担接话、缓冲或软攻击。</div>
            <div class="cube-thumb">
              <img class="cube-face-img" data-cube-file="92.png" src="对应图片3/92.png" onerror="s3CubeFaceError(this)" alt="" decoding="async" />
            </div>
                    </div>
          <div class="cube-face left side">
            <div class="face-num">④ 场景三·关系与风险</div>
            <div class="cube-text">同学/同事与陌生网友占比高；高风险多与边界、婉拒或攻击性话术同现，可结合堆叠条观察各关系下的风险构成。</div>
            <div class="cube-thumb">
              <img class="cube-face-img" data-cube-file="133.png" src="对应图片3/133.png" onerror="s3CubeFaceError(this)" alt="" decoding="async" />
                </div>
                    </div>""",
    ),
    (
        '<h2 class="h2-compact">细分阶段（场景二）</h2>',
        '<h2 class="h2-compact">细分阶段（场景三）</h2>',
    ),
    (
        '<footer class="foot">场景二样本来自 QQ/微信早期熊猫头，侧重「回复工具化」与情绪包装链；路径与图片位于 ../数据/场景二/ 。</footer>',
        '<footer class="foot">场景三样本聚焦「当下」熊猫头用法：间接表达、礼貌壳、社交功能与关系风险；表格与图源 ../数据/场景三/，页面同目录 对应图片3/ 。</footer>',
    ),
    (
        """  const F = {
    大阶段: "大阶段", 细分: "细分阶段", 当前图片: "当前图片", 原文件名: "原文件名", 图字: "图片文字",
    复杂度: "视觉复杂度", 字数: "文字字数", 黑白: "黑白/彩色", 情绪: "情绪判断", 动作: "动作特征",
    场景: "社交场景判断", 直接: "表达直接性", 包装: "包装程度", 原情: "原始情绪类型", 包后: "包装后的表达类型",
    关系: "关系对象类型", 风险: "关系风险等级"
  };
const FILTER_KEYS = [
    F.大阶段, F.细分, F.复杂度, F.字数, F.黑白, F.情绪, F.动作, F.场景, F.直接, F.包装, F.原情, F.包后, F.关系, F.风险
  ];""",
        """  const F = {
    大阶段: "大阶段", 细分: "细分阶段", 当前图片: "当前图片", 原文件名: "原文件名", 图字: "图片文字",
    复杂度: "视觉复杂度", 字数: "文字字数", 黑白: "黑白/彩色", 情绪: "情绪判断", 动作: "动作特征",
    场景: "社交场景判断", 直接: "表达直接性", 包装: "包装程度", 原情: "原始情绪类型", 包后: "包装后的表达类型",
    关系: "关系对象类型", 风险: "关系风险等级", 社交: "社交功能分类", 真实: "贴近真实情绪程度指数", 图片: "缩略图"
  };
const FILTER_KEYS = [
    F.大阶段, F.细分, F.复杂度, F.字数, F.黑白, F.情绪, F.动作, F.场景, F.直接, F.包装, F.原情, F.包后, F.关系, F.风险, F.社交
  ];""",
    ),
    (
        "  /** 优先与 场景二.html 同目录的 对应图片2/；失败时回退 data-img-alt（见立方体与阶段条脚本） */\n  const IMG_BASE = \"对应图片2/\";\n  const IMG_BASE_ALT = \"../数据/场景二/对应图片2/\";",
        "  /** 优先与 场景三.html 同目录的 对应图片3/；失败时回退 data-img-alt（见立方体与阶段条脚本） */\n  const IMG_BASE = \"对应图片3/\";\n  const IMG_BASE_ALT = \"../数据/场景三/对应图片3/\";",
    ),
    (
        """  function thumb(r) {
    const u = norm(r[F.当前图片]);
    if (u && (u.startsWith("http") || u.startsWith("data:"))) return u;
    if (u) return u.indexOf("/") >= 0 || u.startsWith(".") ? u : IMG_BASE + encodeURIComponent(u);
    const p = thumbEncodedPath(r[F.原文件名]);
    return p ? IMG_BASE + p : "";
  }""",
        """  function thumb(r) {
    const t = norm(r[F.图片]);
    if (t && (t.startsWith("http") || t.startsWith("data:"))) return t;
    if (t) return t.indexOf("/") >= 0 || t.startsWith(".") ? t : IMG_BASE + encodeURIComponent(t);
    const u = norm(r[F.当前图片]);
    if (u && (u.startsWith("http") || u.startsWith("data:"))) return u;
    if (u) return u.indexOf("/") >= 0 || u.startsWith(".") ? u : IMG_BASE + encodeURIComponent(u);
    const p = thumbEncodedPath(r[F.原文件名]);
    return p ? IMG_BASE + p : "";
  }""",
    ),
    (
        '  const PHASE_ORDER = ["动作模板化", "回复工具化", "聊天迁移"];',
        '  const PHASE_ORDER = ["场景细分萌芽", "关系分层", "礼貌化表达", "情绪包装", "软攻击/婉拒系统", "万能模板化"];',
    ),
    (
        """    const PHASE_STRIP = [
      { label: "QQ/微信早期（全部）", key: null, isAll: true },
      { label: "动作模板化", key: "动作模板化", isAll: false },
      { label: "回复工具化", key: "回复工具化", isAll: false },
      { label: "聊天迁移", key: "聊天迁移", isAll: false }
    ];""",
        """    const aggPh = aggregate(ALL, F.细分).filter(function (d) { return d.count > 0; });
    const orderedPh = sortPhases(aggPh);
    const PHASE_STRIP = [{ label: "场景三（全部）", key: null, isAll: true }].concat(
      orderedPh.map(function (d) { return { label: d.key, key: d.key, isAll: false }; })
    );""",
    ),
]

for old, new in replacements:
    if old not in html:
        raise SystemExit("block not found:\n" + old[:200])
    html = html.replace(old, new, 1)

narr_old = """  const CHART_NARRATIVE_TEXTS = [
    "【数据总结·细分×包装（缩略图格）】\\n包装度 1—5 是“情绪说法被包了几层”的离散刻度；三细分阶段在不同包装档位呈现不同的图像密度与字数体量。\\n\\n【对应本图】\\n横轴=包装度（1—5），纵轴=细分阶段；格内为缩略图阵列，外框色=情绪，大小≈字数；悬停高亮同情绪并显示详情。",
    "【数据总结·视觉复杂度】\\n1—3 级占绝大多数，脸+字+少量动作即可传意。\\n\\n【对应本图】\\n渐变面积层读各级条数（左轴），紫虚折线读该级平均字数（右轴）；双轴对应不同量纲，无柱形。",
    "【数据总结·情绪×场景（矩阵）】\\n同一情绪在不同社交场景里承担的功能不同：通用聊天偏缓冲，群聊互损偏对线，私聊偏关系试探。\\n\\n【对应本图】\\n横轴=情绪，纵轴=社交场景；气泡半径=平均视觉复杂度（更“花”更大），悬停显示该格样本数。",
    "【数据总结·黑白/彩色】\\n黑白为主，彩色约占两成，模板感强。\\n\\n【对应本图】\\n每阶段两根分组柱：黑白与彩色的绝对张数并列比较，避免把阶段误读成占比环的一部分。",
    "【数据总结·动作】\\n无动作过半，其余多为打电脑、摆手、打电话等语气动作。\\n\\n【对应本图】\\n极坐标扇段（玫瑰区）：每段角向对应一类动作，径向长度映射条数；点击扇段筛选。",
    "【数据总结·包装度】\\n低包装仍多，中高包装承担阴阳、自嘲、拖延缓冲等。\\n\\n【对应本图】\\n脊线/Joy：每行一阶段，横轴包装 1—5，峰高为相对占比；点击填色筛阶段。",
    "【数据总结·包装链】\\n原情绪多无语/无奈、不爽/攻击等，包装后常落轻吐槽、阴阳、自嘲。\\n\\n【对应本图】\\n左右列 Top5，贝塞尔弦带粗细=路径条数；类目文字外移，避免与节点重叠；悬停看「原情→包后」配对，点击双筛。",
    "【数据总结·直接性×包装】\\n直接、半直接与包装度交叉，可见「怎么说」与「包几层」的关系。\\n\\n【对应本图】\\n离散矩阵格 + 气泡面积=交叉条数；悬停主情绪与缩略图，非连续散点云、非热力格。"
  ];"""

narr_new = """  const CHART_NARRATIVE_TEXTS = [
    "【数据总结·表达直接性】\\n间接与半直接占比较高，「明说」相对少；表情包承担缓冲与转义。\\n\\n【对应本图】\\n环形图：各直接性档位占比；点击扇区筛「表达直接性」。",
    "【数据总结·细分阶段】\\n从场景萌芽、关系分层、礼貌化、情绪包装到婉拒与万能模板，阶段越长文本与修辞往往越重。\\n\\n【对应本图】\\n横向条形：各细分阶段条数；点击条筛阶段。",
    "【数据总结·原情×包后】\\n原始情绪与包装后表达存在稳定迁移路径，自嘲、阴阳、礼貌壳等是高频落点。\\n\\n【对应本图】\\n热力矩阵：原始情绪×包装后交叉频数；点击格双筛。",
    "【数据总结·包装与真实感】\\n包装度与「贴近真实情绪指数」同现：高包装未必低真实，需结合社交功能读。\\n\\n【对应本图】\\n抖动散点：横轴包装分档，纵轴贴近真实指数；点色=情绪。",
    "【数据总结·社交功能】\\n轻吐槽、围观附和、自嘲摆烂、阴阳怪气等功能并存，构成当下接话生态。\\n\\n【对应本图】\\n矩形树图：面积∝各社交功能条数；点击块筛「社交功能分类」。",
    "【数据总结·关系与风险】\\n同学/同事与陌生网友占比高；高风险常与边界、婉拒或攻击性话术同现。\\n\\n【对应本图】\\n横向堆叠条：每行一关系对象，段=低/中/高风险构成；点击段双筛。"
  ];"""

if narr_old not in html:
    raise SystemExit("CHART_NARRATIVE_TEXTS block not found")
html = html.replace(narr_old, narr_new, 1)

render_old = """    addPanel(
      "细分阶段 × 包装度（缩略图矩阵）",
      "横轴包装 1—5；纵轴三阶段；格内放缩略图，外框色=情绪，大小≈字数；悬停高亮。",
      function (box) { chartGridSubPackThumb(box, rowsExact()); },
      "缩略图矩阵"
    );
    addPanel(
      "视觉复杂度 · 面积层 + 双轴折线",
      "渐变面积=各级条数（左轴）；紫虚折线=该级均字数（右轴）。",
      function (box) { chartPolarSpikeComplexity(box, rowsMarg(F.复杂度)); },
      "复杂度面积"
    );
    addPanel(
      "情绪 × 社交场景（复杂度气泡矩阵）",
      "横轴情绪，纵轴社交场景；气泡大小=平均视觉复杂度；悬停显示样本数。",
      function (box) { chartMatrixEmotionSceneComplexity(box, rowsExact()); },
      "情绪×场景矩阵"
    );
    addPanel(
      "黑白/彩色 · 分组柱（按阶段）",
      "每阶段两根柱：黑白张数 vs 彩色张数（绝对值）。",
      function (box) { chartDualAreaBWSub(box, rowsExact()); },
      "分组双色"
    );
    addPanel(
      "动作特征 · 极坐标扇段（玫瑰）",
      "Top8 动作均分圆周，外径∝条数；中心为参照环。",
      function (box) { chartPictoBarsAction(box, rowsMarg(F.动作)); },
      "动作极区"
    );
    addPanel(
      "包装度 · 脊线（按细分）",
      "三行 Joy/ridge；横轴包装 1—5。",
      function (box) { chartRidgePackBySub(box, rowsExact()); },
      "脊线包装"
    );
    addPanel(
      "原始情绪 → 包装后（弦带）",
      "贝塞尔粗线表示路径流量；悬停看配对。",
      function (box) { chartChordLiteOrigPack(box, rowsExact()); },
      "弦带流转"
    );
    addPanel(
      "表达直接性 × 包装（矩阵气泡 · 拉伸强化）",
      "纵向拉伸；气泡面积=交叉条数；圈线/光晕编码平均复杂度；悬停主情绪与图。",
      function (box) { chartMatrixBubbleDirectPack(box, rowsExact()); },
      "矩阵气泡"
    );"""

render_new = """    addPanel(
      "表达直接性 · 环形占比",
      "各档位占比一目了然；点击扇区筛选。",
      function (box) { s3ChartDonutDirect(box, rowsExact()); },
      "环形·直接性"
    );
    addPanel(
      "细分阶段 · 横向条形",
      "长标签易读；条长∝条数；点击筛选阶段。",
      function (box) { s3ChartHBarSubstage(box, rowsExact()); },
      "条形·阶段"
    );
    addPanel(
      "原始情绪 × 包装后 · 热力矩阵",
      "交叉频数用色深表达；点击格同时筛原情与包后。",
      function (box) { s3ChartHeatmapOrigPack(box, rowsExact()); },
      "热力·原情包后"
    );
    addPanel(
      "包装度 × 贴近真实指数 · 抖动散点",
      "离散包装档 + 纵向指数；点内抖动防重叠；点色=情绪。",
      function (box) { s3ChartStripPackReal(box, rowsExact()); },
      "散点·包装真实"
    );
    addPanel(
      "社交功能分类 · 矩形树图",
      "面积∝条数；观察功能结构；点击块筛选。",
      function (box) { s3ChartTreemapSocial(box, rowsExact()); },
      "树图·社交功能"
    );
    addPanel(
      "关系对象 × 风险 · 横向堆叠条",
      "每行总量归一；段=低/中/高构成；点击段双筛。",
      function (box) { s3ChartStackRelRisk(box, rowsExact()); },
      "堆叠·关系风险"
    );"""

if render_old not in html:
    raise SystemExit("renderCharts addPanel block not found")
html = html.replace(render_old, render_new, 1)

html_path.write_text(html, encoding="utf-8")
print("OK: 场景三.html patched")
