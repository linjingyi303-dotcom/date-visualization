# -*- coding: utf-8 -*-
"""Embeds data.json into 场景一.html; syncs images to ./meme-img for file:// opening."""
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
data = json.loads((ROOT / "data.json").read_text(encoding="utf-8"))
payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"))

SRC_IMG = ROOT.parent / "数据" / "场景一" / "对应图片"
DST_IMG = ROOT / "meme-img"
if SRC_IMG.is_dir():
    DST_IMG.mkdir(exist_ok=True)
    for p in SRC_IMG.iterdir():
        if p.is_file() and p.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}:
            shutil.copy2(p, DST_IMG / p.name)
    print("Synced images -> meme-img/", len(list(DST_IMG.iterdir())), "files")
else:
    print("WARN: image folder not found:", SRC_IMG)

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>熊猫头 Meme 数据实验室</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;700;900&display=swap" rel="stylesheet" />
    <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        :root {
            --bg: #050505;
            --c1: #59E2FD;
            --c2: #6C58EE;
            --c3: #F54595;
            --c4: #FCE500;
            --text: #ffffff;
            --ink: #000000;
        }
        html { scroll-behavior: smooth; }
        body { background: var(--bg); color: var(--text); font-family: "Noto Sans SC", sans-serif; overflow-x: hidden; }

        /* ===== 固定背景（与 meme4 统一：细密波点） ===== */
        .halftone-bg {
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 0;
            background-image: radial-gradient(rgba(255, 255, 255, 0.15) 1px, transparent 1px);
            background-size: 6px 6px; pointer-events: none;
        }
        #particleCanvas { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: 1; pointer-events: none; }
        #progress-bar { position: fixed; top: 0; left: 0; height: 5px; width: 0%; z-index: 9999; background: var(--c4); box-shadow: 0 0 12px var(--c4); transition: width 0.1s; }

        /* ===== 页面区块 ===== */
        .page-section {
            position: relative; width: 100vw; min-height: 100vh;
            padding: 60px 0; overflow: hidden; z-index: 10;
            display: flex; align-items: center; justify-content: center;
            border-bottom: 2px solid #111;
        }
        .viz-layout { display: flex; width: 100%; padding: 0 4vw; gap: 4vw; align-items: flex-start; }
        .viz-guide {
            flex: 0 0 300px; display: flex; flex-direction: column; justify-content: flex-start;
            padding-top: 20px; position: sticky; top: 60px;
        }
        .step-badge {
            display: inline-block; background: #fff; color: #000; padding: 4px 12px;
            font-size: 12px; font-weight: 900; margin-bottom: 16px; font-family: 'Courier New', monospace;
            box-shadow: 4px 4px 0 var(--c3); letter-spacing: 2px;
        }
        .guide-title {
            font-size: clamp(1.6rem, 4vw, 50px); line-height: 1.1; margin-bottom: 16px;
            color: var(--c1); font-weight: 900; text-shadow: 3px 3px 0 var(--c2);
        }
        .guide-desc { font-size: 14px; color: #aaa; line-height: 1.8; margin-bottom: 20px; }
        .guide-legend { margin-top: 10px; }
        .legend-item { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; font-size: 13px; cursor: pointer; }
        .legend-dot { width: 16px; height: 16px; flex-shrink: 0; border: 2px solid #000; }

        /* ===== 可视化容器 ===== */
        .viz-screen-container {
            flex: 1; min-height: 75vh; background: #0a0a0a; border: 4px solid #333;
            position: relative; box-shadow: inset 0 0 50px rgba(0,0,0,1), 12px 12px 0 #000; overflow: hidden;
        }
        /* meme4 风格：RGB 扫描纹理 */
        .viz-screen-container::before {
            content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%),
                linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
            background-size: 100% 4px, 3px 100%; pointer-events: none; z-index: 4;
        }
        .viz-screen-container::after {
            content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 100%;
            background: repeating-linear-gradient(0deg, transparent, transparent 3px, rgba(0,0,0,0.08) 3px, rgba(0,0,0,0.08) 4px);
            pointer-events: none; z-index: 5;
        }
        .screen-header {
            display: flex; justify-content: space-between; align-items: center;
            background: #0e0e0e; padding: 10px 18px; border-bottom: 2px solid #1a1a1a;
            font-family: 'Courier New', monospace; font-size: 12px; color: #666;
        }
        .status-blink { display: inline-block; width: 8px; height: 8px; background: var(--c1); border-radius: 50%; margin-right: 8px; animation: blink 1.2s infinite; }
        @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.1} }
        .viz-wrap { width: 100%; min-height: calc(75vh - 40px); background: transparent; overflow: visible; padding: 16px; }

        /* ===== 控制按钮 ===== */
        .viz-ctrls { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
        .viz-btn {
            background: #111; color: #fff; border: 2px solid #333; padding: 8px 18px;
            font-family: "Noto Sans SC", sans-serif; font-size: 13px; font-weight: 700;
            cursor: pointer; box-shadow: 3px 3px 0 #000; transition: all 0.15s; user-select: none;
        }
        .viz-btn:hover { transform: translate(-2px,-2px); box-shadow: 5px 5px 0 #000; background: #1a1a1a; border-color: #555; }
        .viz-btn.active { background: var(--c4); color: #000; border-color: #000; box-shadow: 3px 3px 0 var(--c1); }

        /* ===== 图片星系 ===== */
        .orbit-field { width: 100%; height: 100%; min-height: 600px; position: relative; overflow: hidden; }
        .meme-pop {
            position: absolute; cursor: pointer; z-index: 10;
            transition: z-index 0s;
        }
        .meme-frame {
            border: 3px solid rgba(255,255,255,0.5); background: #000;
            box-shadow: 6px 6px 0 rgba(108,88,238,0.5); overflow: hidden;
            transition: border-color 0.3s, box-shadow 0.3s;
        }
        .meme-frame img { display: block; width: 100%; height: auto; image-rendering: pixelated; }
        .meme-note-panel {
            position: absolute; left: 50%; bottom: calc(100% + 12px);
            transform: translateX(-50%) translateY(8px) scale(0.8);
            background: var(--c4); color: #000; padding: 10px 14px; width: 200px;
            font-size: 13px; font-weight: 700; border: 2px solid #000;
            box-shadow: 6px 6px 0 #000; opacity: 0; pointer-events: none;
            transition: opacity 0.25s, transform 0.25s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            z-index: 200; line-height: 1.5;
        }
        .meme-note-panel::after {
            content: ''; position: absolute; top: 100%; left: 50%; transform: translateX(-50%);
            border: 6px solid transparent; border-top-color: #000;
        }

        /* ===== 阶段树（固定可视高度，内部滚动） ===== */
        .phase-tree-wrap { width: 100%; position: relative; overflow-y: auto; overflow-x: hidden; height: 480px; max-height: 52vh; border: 2px solid #1a1a1a; background: rgba(0,0,0,0.35); }
        .phase-bud {
            position: absolute; overflow: hidden; cursor: pointer;
            border: 3px solid rgba(255,255,255,0.6); box-shadow: 6px 6px 0 #000;
            background: #000; transition: border-color 0.2s, box-shadow 0.2s;
        }
        .phase-bud:hover { border-color: var(--c4) !important; box-shadow: 8px 8px 0 var(--c2) !important; z-index: 100; }
        .phase-bud img { display: block; width: 100%; height: 100%; object-fit: cover; image-rendering: pixelated; }

        /* ===== 灯箱 ===== */
        .lightbox {
            position: fixed; inset: 0; z-index: 10050; display: flex;
            align-items: center; justify-content: center; flex-direction: column; gap: 16px;
            opacity: 0; pointer-events: none; transition: opacity 0.3s;
        }
        .lightbox.on { opacity: 1; pointer-events: auto; }
        .lightbox-backdrop { position: absolute; inset: 0; background: rgba(0,0,0,0.92); backdrop-filter: blur(12px); cursor: pointer; }
        .lightbox-frame { position: relative; z-index: 1; border: 5px solid #fff; box-shadow: 15px 15px 0 #000; background: #000; }
        #lightbox-img { max-width: 80vw; max-height: 75vh; display: block; image-rendering: pixelated; }
        .lightbox-hint { position: relative; z-index: 1; color: #aaa; font-size: 14px; font-family: 'Courier New', monospace; }

        /* ===== 提示框 ===== */
        .tooltip {
            position: fixed; pointer-events: none; background: #000; color: #fff;
            padding: 8px 14px; font-size: 13px; font-weight: 700; border: 2px solid var(--c3);
            z-index: 10000; opacity: 0; box-shadow: 5px 5px 0 var(--c4); line-height: 1.5;
            transition: opacity 0.15s; max-width: 260px;
        }

        /* ===== 图表中文坐标轴 ===== */
        .axis-label { font-size: 13px; fill: #aaa; font-family: "Noto Sans SC", sans-serif; }
        .chart-title { font-size: 16px; fill: var(--c1); font-weight: 900; font-family: "Noto Sans SC", sans-serif; }

        @media (max-width: 900px) {
            .viz-layout { flex-direction: column; padding: 20px; }
            .viz-guide { position: static; flex: none; }
            .viz-screen-container { min-height: 60vh; }
        }
    </style>
</head>
<body>
    <div id="progress-bar"></div>
    <div id="lightbox" class="lightbox">
        <div class="lightbox-backdrop" id="lb-back"></div>
        <div class="lightbox-frame"><img id="lightbox-img" src="" alt=""/></div>
        <p class="lightbox-hint" id="lb-hint"></p>
    </div>
    <div class="halftone-bg"></div>
    <canvas id="particleCanvas"></canvas>
    <div class="tooltip" id="tooltip"></div>
    <main id="main"></main>

<script>
const DATA = __DATA_PLACEHOLDER__;

// ===== 颜色配置 =====
const PX = { c1:"#59E2FD", c2:"#6C58EE", c3:"#F54595", c4:"#FCE500", ink:"#000", text:"#fff" };
const PAL = [PX.c1, PX.c2, PX.c3, PX.c4];

// ===== 工具函数 =====
function esc(s){ return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/"/g,"&quot;"); }
function seeded(i){ return k=>{ const x=Math.sin(i*12.9898+k*78.233)*43758.5453; return x-Math.floor(x); }; }
function imageSrc(fn){ return "meme-img/"+String(fn).split("/").map(encodeURIComponent).join("/"); }
function getNote(r){ return (r[NOTE_KEY]||"（暂无备注）").trim(); }
const NOTE_KEY = DATA.columns.find(c=>String(c).includes("编码备注"))||"编码备注";

function aggregate(rows,key){
    const m=new Map();
    rows.forEach(r=>{ const v=String(r[key]||"（空）").trim(); m.set(v,(m.get(v)||0)+1); });
    return Array.from(m,([k,c])=>({key:k,count:c})).sort((a,b)=>b.count-a.count);
}

function orderColumns(cols){
    const skip=new Set(["文件名","编码备注","图片"]);
    const head=["图片"];
    const priority=["阶段","早期典型传播平台","图像来源类型","文字数量","情绪包装度（1-5）","黑白/彩色","图片清晰度","情绪表达是否直接","人物原型","动作特征","模板类型"];
    const rest=cols.filter(c=>!skip.has(c)&&!new Set(priority).has(c));
    return [...head.filter(c=>cols.includes(c)),...priority.filter(c=>cols.includes(c)),...rest];
}

// ===== 灯箱 =====
function openLightbox(src){
    const lb=document.getElementById("lightbox"), im=document.getElementById("lightbox-img"), hint=document.getElementById("lb-hint");
    im.src=src; lb.classList.add("on");
    if(hint){ hint.textContent=""; typewriterEl(hint,"按 Esc 或点击背景关闭",26,420); }
    gsap.fromTo(im,{scale:0.6,rotation:-5,opacity:0},{scale:1,rotation:0,opacity:1,duration:0.5,ease:"back.out(2)"});
}
function closeLightbox(){ document.getElementById("lightbox").classList.remove("on"); }
document.getElementById("lb-back").onclick = closeLightbox;
document.addEventListener("keydown",e=>{ if(e.key==="Escape") closeLightbox(); });

// ===== 提示框 =====
const TIP = document.getElementById("tooltip");
function showTip(event, html){
    TIP.innerHTML = html; TIP.style.opacity="1";
    TIP.style.left=event.clientX+16+"px"; TIP.style.top=event.clientY+16+"px";
}
function moveTip(event){ TIP.style.left=event.clientX+16+"px"; TIP.style.top=event.clientY+16+"px"; }
function hideTip(){ TIP.style.opacity="0"; }

// ===== 打字机效果（中文按字） =====
function typewriterEl(el, full, msPerChar=28, startDelay=0){
    if(!el||full==null) return;
    const chars=[...String(full)];
    el.textContent="";
    setTimeout(()=>{
        let i=0;
        const id=setInterval(()=>{
            if(i>=chars.length){ clearInterval(id); return; }
            el.textContent+=chars[i++];
        },msPerChar);
    },startDelay);
}
function typeD3Text(sel, full, startDelay=0, msPerChar=22){
    if(!sel||!full) return;
    const chars=[...String(full)];
    sel.text("");
    setTimeout(()=>{
        let i=0;
        const id=setInterval(()=>{
            if(i>=chars.length){ clearInterval(id); return; }
            sel.text((sel.text()||"")+chars[i++]);
        },msPerChar);
    },startDelay);
}

function vizSize(host){ const r=host.getBoundingClientRect(); return {w:Math.max(r.width,600),h:Math.max(r.height,500)}; }

function pixelSvg(host,w,h){
    return d3.select(host).append("svg").attr("viewBox",`0 0 ${w} ${h}`).attr("width",w).attr("height",h).attr("shape-rendering","crispEdges");
}

// ===== 通用坐标轴样式 =====
function styleAxis(g){
    g.selectAll("path,line").attr("stroke","#333");
    g.selectAll("text").attr("fill","#888").style("font-size","12px").style("font-family","'Noto Sans SC', sans-serif");
}

// ========================
// 图表1：图片星系
// ========================
function renderImageGalaxy(host, rows){
    const field=document.createElement("div"); field.className="orbit-field";
    rows.slice(0,80).forEach((r,i)=>{
        const fn=r["文件名"]; if(!fn) return;
        const wrap=document.createElement("div"); wrap.className="meme-pop";
        const sr=seeded(i*7);
        const wpx=100+sr(0)*130;
        wrap.style.cssText=`width:${wpx}px;left:${3+sr(1)*83}%;top:${3+sr(2)*83}%;`;

        const frame=document.createElement("div"); frame.className="meme-frame";
        const img=document.createElement("img"); img.src=imageSrc(fn); img.loading="lazy";
        frame.appendChild(img);

        const panel=document.createElement("div"); panel.className="meme-note-panel";
        panel.textContent="";

        wrap.appendChild(frame); wrap.appendChild(panel);

        // 点击打开灯箱
        wrap.onclick=e=>{ e.stopPropagation(); openLightbox(img.src); };

        // 常驻左右轻晃（不依赖点击）
        const swayAmp=4+sr(4)*5, swayDur=1.2+sr(5)*0.8;
        gsap.set(wrap,{transformOrigin:"50% 50%"});
        let idleTl=null;
        function startIdleSway(){
            if(idleTl) idleTl.kill();
            gsap.set(wrap,{rotation:-swayAmp,x:-swayAmp*0.35});
            idleTl=gsap.to(wrap,{rotation:swayAmp,x:swayAmp*0.35,duration:swayDur,repeat:-1,yoyo:true,ease:"sine.inOut"});
        }

        // 鼠标悬浮 - 暂停晃动 + 强烈弹跳
        wrap.addEventListener("mouseenter",()=>{
            if(idleTl){ idleTl.kill(); idleTl=null; }
            gsap.to(wrap,{rotation:0,x:0,duration:0.2});
            wrap.style.zIndex=100;
            typewriterEl(panel,getNote(r),18,0);
            panel.style.opacity="1";
            panel.style.transform="translateX(-50%) translateY(0) scale(1)";
            gsap.to(frame,{scale:1.1,rotation:3,borderColor:"#fff",duration:0.3,ease:"back.out(2)"});
            gsap.to(frame,{boxShadow:`12px 12px 0 ${PX.c2}`,duration:0.3});
        });
        wrap.addEventListener("mouseleave",()=>{
            wrap.style.zIndex=10;
            panel.textContent="";
            panel.style.opacity="0";
            panel.style.transform="translateX(-50%) translateY(8px) scale(0.8)";
            gsap.to(frame,{scale:1,rotation:0,borderColor:"rgba(255,255,255,0.5)",duration:0.4});
            gsap.to(frame,{boxShadow:`6px 6px 0 rgba(108,88,238,0.5)`,duration:0.4});
            startIdleSway();
        });

        field.appendChild(wrap);
        gsap.fromTo(wrap,{scale:0,opacity:0,rotation:sr(3)*40-20},{scale:1,opacity:1,rotation:0,duration:1,delay:i*0.025,ease:"elastic.out(1,0.6)",onComplete:()=>startIdleSway()});
    });
    host.appendChild(field);
}

// ========================
// 图表2：阶段生长树
// ========================
function renderPhaseUniverse(host, rows, col){
    // 从数据中动态获取阶段列表
    const phaseSet = new Map();
    rows.forEach(r=>{ const v=String(r[col]||"").trim(); if(v) phaseSet.set(v,(phaseSet.get(v)||0)+1); });
    const phases = Array.from(phaseSet.keys()).sort();
    const allOptions = ["全部",...phases];
    let currentPhase = "全部";

    // 控制按钮
    const ctrl=document.createElement("div"); ctrl.className="viz-ctrls";
    allOptions.forEach((p, bi)=>{
        const btn=document.createElement("button"); btn.className="viz-btn"+(p===currentPhase?" active":"");
        btn.textContent="";
        typewriterEl(btn,p,22,bi*120);
        btn.onclick=()=>{
            ctrl.querySelectorAll(".viz-btn").forEach(b=>b.classList.remove("active"));
            btn.classList.add("active"); currentPhase=p; updateTree();
        };
        ctrl.appendChild(btn);
    });
    host.appendChild(ctrl);

    const wrap=document.createElement("div"); wrap.className="phase-tree-wrap"; host.appendChild(wrap);

    function updateTree(){
        wrap.innerHTML="";
        const MAX_NODES=36;
        const filtered=(currentPhase==="全部"?rows:rows.filter(r=>String(r[col]).trim()===currentPhase)).slice(0,MAX_NODES);
        const n=filtered.length; if(!n) return;

        const hostW=Math.max(host.getBoundingClientRect().width||800, 600);
        const rowH=48;
        const sz=42;
        const treeH=Math.max(420, Math.ceil(n/2)*rowH+100);
        wrap.style.height="";
        wrap.style.maxHeight="52vh";

        const svg=d3.select(wrap).append("svg").attr("width",hostW).attr("height",treeH).attr("shape-rendering","crispEdges");
        const midX=hostW/2;

        // 主干从底部生长
        const trunk=svg.append("line")
            .attr("x1",midX).attr("y1",treeH-16).attr("x2",midX).attr("y2",treeH-16)
            .attr("stroke",PX.c2).attr("stroke-width",10).attr("stroke-linecap","square");
        trunk.transition().duration(700).ease(d3.easeCubicOut).attr("y2",36);

        // 相位颜色
        const phaseColor={};
        phases.forEach((p,pi)=>{ phaseColor[p]=PAL[pi%4]; });

        filtered.forEach((r,i)=>{
            const delay=400+i*32;
            const side=i%2===0?-1:1;
            const yPos=treeH-88-Math.floor(i/2)*rowH;
            const xPos=midX+side*(72+(i%3)*28);
            const phaseVal=String(r[col]||"").trim();
            const bColor=phaseColor[phaseVal]||PX.c1;

            // 枝干线
            const branch=svg.append("line")
                .attr("x1",midX).attr("y1",yPos).attr("x2",midX).attr("y2",yPos)
                .attr("stroke",bColor).attr("stroke-width",3).attr("opacity",0.6);
            branch.transition().duration(380).delay(delay).attr("x2",xPos).attr("opacity",1);

            // 节点图片
            const bud=document.createElement("div"); bud.className="phase-bud";
            bud.style.cssText=`width:${sz}px;height:${sz}px;left:${xPos-sz/2}px;top:${yPos-sz/2}px;border-color:${bColor};`;
            const img=document.createElement("img"); img.src=imageSrc(r["文件名"]||""); img.loading="lazy";
            bud.appendChild(img);
            bud.onclick=()=>openLightbox(img.src);
            bud.addEventListener("mouseenter",ev=>{
                showTip(ev,`<b>${phaseVal}</b><br>${getNote(r)}`);
                gsap.to(bud,{scale:1.3,rotation:-4,duration:0.3,ease:"back.out(2)"});
                branch.transition().duration(200).attr("stroke","#fff").attr("stroke-width",5);
            });
            bud.addEventListener("mousemove",moveTip);
            bud.addEventListener("mouseleave",()=>{
                hideTip();
                gsap.to(bud,{scale:1,rotation:0,duration:0.4});
                branch.transition().duration(400).attr("stroke",bColor).attr("stroke-width",3);
            });
            wrap.appendChild(bud);
            gsap.fromTo(bud,{scale:0,rotation:-12},{scale:1,rotation:0,duration:0.45,delay:delay/1000+0.15,ease:"back.out(2)"});
        });

        // 图注（打字效果）
        const legendY=18;
        phases.forEach((p,pi)=>{
            const lx=16+pi%3*200, ly=legendY+Math.floor(pi/3)*22;
            svg.append("rect").attr("x",lx).attr("y",ly-10).attr("width",12).attr("height",12).attr("fill",PAL[pi%4]).attr("stroke","#000").attr("stroke-width",1);
            typeD3Text(svg.append("text").attr("x",lx+16).attr("y",ly).attr("fill","#ccc").style("font-size","11px").style("font-family","'Noto Sans SC',sans-serif"), p, 200+pi*80, 28);
        });
        setTimeout(()=>{ wrap.scrollTop=0; }, 100);
    }
    updateTree();
}

// ========================
// 图表3：贝塞尔流向图
// ========================
function renderSankeyish(host, rows, col){
    const {w,h}=vizSize(host);
    const agg=aggregate(rows,col);
    const svg=pixelSvg(host,w,h);
    const xL=160,xR=w-200,yR=h/2;
    const maxC=d3.max(agg,d=>d.count);
    const ys=d3.scalePoint().domain(agg.map(d=>d.key)).range([80,h-80]).padding(0.4);

    typeD3Text(svg.append("text").attr("x",xL).attr("y",40).attr("class","chart-title"), "来源分布流向图", 0, 20);

    agg.forEach((d,i)=>{
        const y=ys(d.key);
        const sw=6+(d.count/maxC)*38;
        const color=PAL[i%4];
        const p=d3.path(); p.moveTo(xL,y); p.bezierCurveTo((xL+xR)/2,y,(xL+xR)/2,yR,xR,yR);
        const totalLen=800;
        const path=svg.append("path").attr("d",p.toString()).attr("fill","none")
            .attr("stroke",color).attr("stroke-width",sw).attr("opacity",0.55)
            .attr("stroke-dasharray",totalLen).attr("stroke-dashoffset",totalLen);
        path.transition().duration(1500).delay(i*120).ease(d3.easeCubicOut).attr("stroke-dashoffset",0);

        // 标签
        svg.append("rect").attr("x",xL-140).attr("y",y-14).attr("width",120).attr("height",22).attr("fill","#111").attr("stroke",color).attr("stroke-width",2);
        typeD3Text(svg.append("text").attr("x",xL-80).attr("y",y+5).attr("text-anchor","middle").attr("fill","#fff").style("font-size","12px").style("font-family","'Noto Sans SC',sans-serif"), d.key, 260+i*130, 18);
        typeD3Text(svg.append("text").attr("x",xL-8).attr("y",y+5).attr("fill",color).style("font-size","14px").style("font-weight","900"), String(d.count), 300+i*130, 16);

        // 悬浮交互 (D3v7: event, datum)
        path.on("mouseover",(event)=>{
            d3.select(path.node()).transition().duration(150).attr("opacity",1).attr("stroke-width",sw+12);
            showTip(event,`<b>${d.key}</b><br>数量：${d.count} 张<br>占比：${Math.round(d.count/rows.length*100)}%`);
        }).on("mousemove",moveTip).on("mouseout",()=>{
            d3.select(path.node()).transition().duration(300).attr("opacity",0.55).attr("stroke-width",sw);
            hideTip();
        });
    });

    svg.append("rect").attr("x",xR-5).attr("y",yR-60).attr("width",30).attr("height",120).attr("fill",PX.c4).attr("stroke","#000").attr("stroke-width",3);
    const tailD=420+agg.length*140;
    typeD3Text(svg.append("text").attr("x",xR+35).attr("y",yR-10).attr("fill",PX.c4).style("font-size","15px").style("font-weight","900"), "熊猫头", tailD, 22);
    typeD3Text(svg.append("text").attr("x",xR+35).attr("y",yR+12).attr("fill",PX.c4).style("font-size","15px").style("font-weight","900"), "模因库", tailD+280, 22);
}

// ========================
// 图表4：像素砖块矩阵
// ========================
function renderBrickWall(host, rows, col){
    const {w,h}=vizSize(host);
    const agg=aggregate(rows,col);
    const brick=22,gap=5;
    const perRow=Math.max(1,Math.floor((w-200)/(brick+gap)));
    const svg=pixelSvg(host,w,Math.max(h,1000));

    typeD3Text(svg.append("text").attr("x",20).attr("y",30).attr("class","chart-title"), "平台分布像素矩阵（每格=1条记录）", 0, 20);

    let y0=60;
    agg.forEach((d,ri)=>{
        const color=PAL[ri%4];
        svg.append("rect").attr("x",14).attr("y",y0-4).attr("width",8).attr("height",8).attr("fill",color);
        typeD3Text(svg.append("text").attr("x",26).attr("y",y0+4).attr("fill",color).style("font-size","15px").style("font-weight","900"), `${d.key}  ×${d.count}`, 60+ri*100, 18);

        const maxShow=Math.min(d.count,200);
        for(let k=0;k<maxShow;k++){
            const rr=Math.floor(k/perRow), cc=k%perRow;
            const rx=20+cc*(brick+gap), ry=y0+24+rr*(brick+gap);
            const rect=svg.append("rect").attr("x",rx).attr("y",ry).attr("width",brick).attr("height",0).attr("fill",color).attr("stroke","#000").attr("stroke-width",1.5);
            rect.transition().duration(350).delay(k*6+ri*80).ease(d3.easeBackOut).attr("height",brick);
            rect.on("mouseover",(event)=>{
                d3.select(rect.node()).attr("fill","#fff");
                showTip(event,`<b>${d.key}</b><br>第 ${k+1} 条记录`);
            }).on("mousemove",moveTip).on("mouseout",()=>{
                d3.select(rect.node()).attr("fill",color);
                hideTip();
            });
        }
        // 数量标注
        typeD3Text(svg.append("text").attr("x",20+perRow*(brick+gap)+10).attr("y",y0+24+14).attr("fill","#555").style("font-size","14px"), `共 ${d.count}`, 90+ri*100, 16);
        y0+=30+Math.ceil(maxShow/perRow)*(brick+gap)+20;
    });
}

// ========================
// 图表5：阶梯波形直方图
// ========================
function renderStepWave(host, rows, col){
    const {w,h}=vizSize(host);
    const vals=rows.map(r=>+r[col]).filter(x=>!isNaN(x)&&isFinite(x));
    if(!vals.length) return;
    const bins=d3.bin().thresholds(20)(vals);
    const px=80,py=60,mx=w-60,my=h-80;
    const xS=d3.scaleLinear().domain([bins[0].x0,bins[bins.length-1].x1]).range([px,mx]);
    const yS=d3.scaleLinear().domain([0,d3.max(bins,b=>b.length)]).range([my,py]);
    const svg=pixelSvg(host,w,h);

    typeD3Text(svg.append("text").attr("x",px).attr("y",40).attr("class","chart-title"), "文字数量分布直方图", 0, 20);
    typeD3Text(svg.append("text").attr("x",(px+mx)/2).attr("y",h-10).attr("class","axis-label").attr("text-anchor","middle"), "文字字数（个）", 180, 18);
    typeD3Text(svg.append("text").attr("x",16).attr("y",(py+my)/2).attr("class","axis-label").attr("text-anchor","middle").attr("transform",`rotate(-90,16,${(py+my)/2})`), "图片数量", 320, 18);

    // 阴影填充
    const area=d3.area().curve(d3.curveStepAfter).x(d=>xS(d.x0)).y0(yS(0)).y1(d=>yS(d.length));
    svg.append("path").datum(bins).attr("fill",PX.c1).attr("opacity",0.15).attr("d",area);

    bins.forEach((b,i)=>{
        if(b.length===0) return;
        const bw=Math.max(2,xS(b.x1)-xS(b.x0)-2);
        const rect=svg.append("rect").attr("x",xS(b.x0)).attr("y",yS(0)).attr("width",bw).attr("height",0).attr("fill",PX.c1).attr("stroke","#000").attr("stroke-width",1.5);
        rect.transition().duration(900).delay(i*35).ease(d3.easeCubicOut).attr("y",yS(b.length)).attr("height",yS(0)-yS(b.length));
        // 顶部数值标注
        if(b.length>0) typeD3Text(svg.append("text").attr("x",xS(b.x0)+bw/2).attr("y",yS(b.length)-5).attr("text-anchor","middle").attr("fill",PX.c4).style("font-size","11px"), String(b.length), 480+i*35, 12);
        rect.on("mouseover",(event)=>{
            d3.select(rect.node()).attr("fill",PX.c4);
            showTip(event,`<b>字数：${b.x0}~${b.x1}</b><br>图片数量：${b.length} 张`);
        }).on("mousemove",moveTip).on("mouseout",()=>{ d3.select(rect.node()).attr("fill",PX.c1); hideTip(); });
    });
    styleAxis(svg.append("g").attr("transform",`translate(0,${my})`).call(d3.axisBottom(xS).ticks(8)));
    styleAxis(svg.append("g").attr("transform",`translate(${px},0)`).call(d3.axisLeft(yS).ticks(6)));
}

// ========================
// 图表6：像素环形饼图
// ========================
function renderPixelDonut(host, rows, col){
    const {w,h}=vizSize(host);
    const agg=aggregate(rows,col);
    const total=d3.sum(agg,d=>d.count);
    const r=Math.min(w-200,h-100)*0.38;
    const pie=d3.pie().value(d=>d.count).sort(null);
    const arc=d3.arc().innerRadius(r*0.48).outerRadius(r);
    const arcHover=d3.arc().innerRadius(r*0.44).outerRadius(r*1.08);
    const svg=pixelSvg(host,w,h);
    const g=svg.append("g").attr("transform",`translate(${w/2-60},${h/2})`);

    typeD3Text(svg.append("text").attr("x",20).attr("y",30).attr("class","chart-title"), "黑白/彩色占比", 0, 20);

    g.selectAll("path").data(pie(agg)).join("path")
        .attr("fill",(d,i)=>PAL[i%4]).attr("stroke","#000").attr("stroke-width",4)
        .attr("d",d=>arc({...d,endAngle:d.startAngle}))
        .transition().duration(1000).ease(d3.easeCubicOut)
        .attrTween("d",d=>{ const interp=d3.interpolate(d.startAngle,d.endAngle); return t=>arc({...d,endAngle:interp(t)}); });

    g.selectAll("path").on("mouseover",(event,d)=>{
        d3.select(event.currentTarget).transition().duration(150).attr("d",arcHover(d));
        showTip(event,`<b>${d.data.key}</b><br>数量：${d.data.count}<br>占比：${Math.round(d.data.count/total*100)}%`);
    }).on("mousemove",moveTip).on("mouseout",(event,d)=>{
        d3.select(event.currentTarget).transition().duration(300).attr("d",arc(d));
        hideTip();
    });

    typeD3Text(g.append("text").attr("text-anchor","middle").attr("y",8).attr("fill","#fff").style("font-size","28px").style("font-weight","900"), String(total), 400, 22);
    typeD3Text(g.append("text").attr("text-anchor","middle").attr("y",28).attr("fill","#888").style("font-size","12px"), "总计", 520, 20);

    // 图注到侧边
    const legendX=w/2+r+30, legendStartY=h/2-agg.length*20;
    agg.forEach((d,i)=>{
        svg.append("rect").attr("x",legendX).attr("y",legendStartY+i*32).attr("width",18).attr("height",18).attr("fill",PAL[i%4]).attr("stroke","#000").attr("stroke-width",2);
        typeD3Text(svg.append("text").attr("x",legendX+26).attr("y",legendStartY+i*32+14).attr("fill","#ddd").style("font-size","14px").style("font-family","'Noto Sans SC',sans-serif"), `${d.key}  (${d.count})`, 620+i*90, 18);
    });
}

// ========================
// 图表7：像素信号塔
// ========================
function renderPixelTowers(host, rows, col){
    const {w,h}=vizSize(host);
    const agg=aggregate(rows,col);
    const n=agg.length||1;
    const svg=pixelSvg(host,w,h);
    const maxC=d3.max(agg,d=>d.count);
    const colW=(w-180)/n;
    const blockH=Math.min(25,Math.floor((h-200)/15));
    const maxBlocks=Math.floor((h-200)/blockH);

    typeD3Text(svg.append("text").attr("x",90).attr("y",35).attr("class","chart-title"), "清晰度分级信号塔", 0, 20);
    typeD3Text(svg.append("text").attr("x",(90+(w-90))/2).attr("y",h-10).attr("class","axis-label").attr("text-anchor","middle"), "清晰度等级", 200, 18);

    agg.forEach((d,i)=>{
        const x=90+i*colW;
        const blocks=Math.max(1,Math.ceil((d.count/maxC)*maxBlocks));
        const color=PAL[i%4];
        for(let b=0;b<blocks;b++){
            const by=h-90-b*blockH;
            const rect=svg.append("rect").attr("x",x+10).attr("y",by).attr("width",colW-20).attr("height",blockH-3).attr("fill",color).attr("stroke","#000").attr("stroke-width",1.5).attr("opacity",0);
            rect.transition().duration(250).delay(i*80+b*40).attr("opacity",1).attr("y",h-90).attr("y",by);
            rect.on("mouseover",(event)=>{
                d3.select(rect.node()).attr("fill","#fff");
                showTip(event,`<b>${d.key}</b><br>数量：${d.count}张<br>当前层：第 ${b+1}/${blocks} 格`);
            }).on("mousemove",moveTip).on("mouseout",()=>{ d3.select(rect.node()).attr("fill",color); hideTip(); });
        }
        // 数值标注
        typeD3Text(svg.append("text").attr("x",x+colW/2).attr("y",h-90-blocks*blockH-8).attr("text-anchor","middle").attr("fill",color).style("font-size","14px").style("font-weight","900"), String(d.count), 400+i*120, 16);
        typeD3Text(svg.append("text").attr("x",x+colW/2).attr("y",h-65).attr("text-anchor","middle").attr("fill","#ccc").style("font-size","13px").style("font-family","'Noto Sans SC',sans-serif"), d.key, 440+i*120, 18);
    });
    // Y 轴
    const yS=d3.scaleLinear().domain([0,maxC]).range([h-90,h-90-maxBlocks*blockH]);
    styleAxis(svg.append("g").attr("transform","translate(88,0)").call(d3.axisLeft(yS).ticks(5)));
}

// ========================
// 图表8：像素雷达图
// ========================
function renderPixelRadar(host, rows, col){
    const {w,h}=vizSize(host);
    const agg=aggregate(rows,col).slice(0,8);
    const n=agg.length; if(!n) return;
    const r=Math.min(w,h)*0.35;
    const svg=pixelSvg(host,w,h);
    const g=svg.append("g").attr("transform",`translate(${w/2},${h/2})`);
    const maxC=d3.max(agg,d=>d.count);
    const aStep=(Math.PI*2)/n;

    typeD3Text(svg.append("text").attr("x",20).attr("y",30).attr("class","chart-title"), "人物原型分布雷达图", 0, 20);

    const points=agg.map((d,i)=>{ const dist=(d.count/maxC)*r; return [Math.cos(i*aStep-Math.PI/2)*dist,Math.sin(i*aStep-Math.PI/2)*dist]; });

    [0.2,0.4,0.6,0.8,1].forEach(f=>{
        const gp=agg.map((_,i)=>[Math.cos(i*aStep-Math.PI/2)*r*f,Math.sin(i*aStep-Math.PI/2)*r*f]);
        g.append("polygon").attr("points",gp.join(" ")).attr("fill","none").attr("stroke","#2a2a2a").attr("stroke-width",1.5).attr("stroke-dasharray",f<1?"4 3":"none");
        if(f===1||f===0.5) typeD3Text(g.append("text").attr("x",-8).attr("y",-r*f).attr("fill","#555").style("font-size","10px").attr("text-anchor","end"), String(Math.round(maxC*f)), f===1?80:200, 12);
    });
    agg.forEach((_,i)=>{
        g.append("line").attr("x1",0).attr("y1",0).attr("x2",Math.cos(i*aStep-Math.PI/2)*r).attr("y2",Math.sin(i*aStep-Math.PI/2)*r).attr("stroke","#222").attr("stroke-width",1);
    });

    const poly=g.append("polygon").attr("points",points.map(()=>"0,0").join(" ")).attr("fill",PX.c3).attr("fill-opacity",0.35).attr("stroke",PX.c3).attr("stroke-width",4).attr("stroke-linejoin","bevel");
    poly.transition().duration(1200).ease(d3.easeElasticOut.amplitude(1).period(0.5)).attr("points",points.join(" "));

    // 顶点圆和标签
    points.forEach(([px,py],i)=>{
        const c=g.append("circle").attr("cx",0).attr("cy",0).attr("r",0).attr("fill",PX.c4).attr("stroke","#000").attr("stroke-width",2);
        c.transition().duration(800).delay(1000+i*80).attr("cx",px).attr("cy",py).attr("r",7);
        c.on("mouseover",(event)=>showTip(event,`<b>${agg[i].key}</b><br>${agg[i].count} 张`))
         .on("mousemove",moveTip).on("mouseout",hideTip);
        const tx=Math.cos(i*aStep-Math.PI/2)*(r+45), ty=Math.sin(i*aStep-Math.PI/2)*(r+45);
        typeD3Text(g.append("text").attr("x",tx).attr("y",ty).attr("text-anchor","middle").attr("dominant-baseline","middle").attr("fill","#ddd").style("font-size","13px").style("font-family","'Noto Sans SC',sans-serif"), agg[i].key, 900+i*100, 18);
    });
}

// ========================
// 图表9：镜像蝴蝶对比图
// ========================
function renderMirrorButterfly(host, rows, col){
    const {w,h}=vizSize(host);
    const agg=aggregate(rows,col);
    const svg=pixelSvg(host,w,h);
    const midX=w/2, maxC=d3.max(agg,d=>d.count);
    const total=d3.sum(agg,d=>d.count);
    const barH=Math.min(60,Math.floor((h-160)/Math.max(agg.length,1)));

    typeD3Text(svg.append("text").attr("x",midX).attr("y",35).attr("text-anchor","middle").attr("class","chart-title"), "情绪表达方式对比", 0, 20);
    svg.append("line").attr("x1",midX).attr("y1",55).attr("x2",midX).attr("y2",h-60).attr("stroke","#333").attr("stroke-width",3).attr("stroke-dasharray","6 4");
    typeD3Text(svg.append("text").attr("x",midX).attr("y",h-25).attr("text-anchor","middle").attr("class","axis-label"), "← 间接表达　　　直接表达 →", 220, 18);

    // X 轴
    const xRight=d3.scaleLinear().domain([0,maxC]).range([midX,w-60]);
    const xLeft=d3.scaleLinear().domain([0,maxC]).range([midX,60]);
    styleAxis(svg.append("g").attr("transform",`translate(0,${h-60})`).call(d3.axisBottom(xRight).ticks(5)));

    agg.forEach((d,i)=>{
        const side=i%2===0?-1:1;
        const barW=(d.count/maxC)*(w/2-80);
        const y=80+Math.floor(i/2)*( barH+18);
        const color=PAL[i%4];
        const rx=side===-1?midX-barW:midX;

        const rect=svg.append("rect").attr("x",midX).attr("y",y).attr("width",0).attr("height",barH).attr("fill",color).attr("stroke","#000").attr("stroke-width",2);
        rect.transition().duration(900).delay(i*150).ease(d3.easeBackOut).attr("x",rx).attr("width",barW);

        // 数值标注
        const tx=side===-1?rx-8:rx+barW+8;
        typeD3Text(svg.append("text").attr("x",tx).attr("y",y+barH/2+5).attr("text-anchor",side===-1?"end":"start").attr("fill",color).style("font-size","14px").style("font-weight","900"), `${d.key} (${d.count})`, 500+i*140, 18);

        rect.on("mouseover",(event)=>{
            d3.select(rect.node()).attr("fill","#fff");
            showTip(event,`<b>${d.key}</b><br>数量：${d.count}张<br>占比：${Math.round(d.count/total*100)}%`);
        }).on("mousemove",moveTip).on("mouseout",()=>{ d3.select(rect.node()).attr("fill",color); hideTip(); });
    });
}

// ========================
// 图表10：电平仪
// ========================
function renderLevelMeter(host, rows, col){
    const {w,h}=vizSize(host);
    const agg=aggregate(rows,col).sort((a,b)=>+a.key-+b.key);
    const n=agg.length||1;
    const svg=pixelSvg(host,w,h);
    const maxC=d3.max(agg,d=>d.count);
    const colW=(w-180)/n;
    const seg=12, segH=Math.min(28,Math.floor((h-200)/seg));

    typeD3Text(svg.append("text").attr("x",90).attr("y",35).attr("class","chart-title"), "情绪包装度分级电平仪", 0, 20);

    agg.forEach((d,i)=>{
        const x=90+i*colW;
        const activeSegs=Math.ceil((d.count/maxC)*seg);
        for(let s=0;s<seg;s++){
            const isOn=s<activeSegs;
            const color=isOn?(s<4?PX.c1:s<8?PX.c2:PX.c3):"#0d0d0d";
            const sy=h-120-s*segH;
            const rect=svg.append("rect").attr("x",x+15).attr("y",sy).attr("width",colW-30).attr("height",segH-4).attr("fill",isOn?color:"#0d0d0d").attr("stroke","#1a1a1a").attr("stroke-width",2).attr("opacity",0);
            rect.transition().duration(300).delay(i*80+s*45).attr("opacity",1);
            rect.on("mouseover",(event)=>{
                if(isOn) d3.select(rect.node()).attr("fill","#fff");
                showTip(event,`等级 ${d.key}<br>数量：${d.count}张<br>满格：${activeSegs}/${seg}`);
            }).on("mousemove",moveTip).on("mouseout",()=>{ if(isOn) d3.select(rect.node()).attr("fill",color); hideTip(); });
        }
        typeD3Text(svg.append("text").attr("x",x+colW/2).attr("y",h-120-activeSegs*segH-8).attr("text-anchor","middle").attr("fill",PAL[i%4]).style("font-size","15px").style("font-weight","900"), String(d.count), 380+i*100, 16);
        typeD3Text(svg.append("text").attr("x",x+colW/2).attr("y",h-85).attr("text-anchor","middle").attr("fill","#ccc").style("font-size","13px"), `等级${d.key}`, 420+i*100, 18);
    });
    const yS=d3.scaleLinear().domain([0,maxC]).range([h-120,h-120-seg*segH]);
    styleAxis(svg.append("g").attr("transform","translate(88,0)").call(d3.axisLeft(yS).ticks(5)));
}

// ========================
// 图表11：华夫图
// ========================
function renderWaffleGrid(host, rows, col){
    const {w,h}=vizSize(host);
    const agg=aggregate(rows,col);
    const total=d3.sum(agg,d=>d.count);
    const svg=pixelSvg(host,w,h);
    const side=10, cell=Math.min(38,Math.floor((Math.min(w,h)-120)/side));
    const ox=(w-side*cell)/2, oy=(h-side*cell)/2+10;

    typeD3Text(svg.append("text").attr("x",ox).attr("y",oy-20).attr("class","chart-title"), "模板类型华夫比例图（每格=1%）", 0, 20);

    let idx=0;
    agg.forEach((d,ci)=>{
        const count=Math.round((d.count/total)*100);
        for(let i=0;i<count&&idx<100;i++,idx++){
            const rr=Math.floor(idx/side), cc=idx%side;
            const color=PAL[ci%4];
            const rect=svg.append("rect").attr("x",ox+cc*cell).attr("y",oy+rr*cell).attr("width",cell-4).attr("height",cell-4).attr("fill",color).attr("stroke","#000").attr("stroke-width",2).attr("opacity",0);
            rect.transition().duration(400).delay(idx*12).attr("opacity",1);
            rect.on("mouseover",(event)=>{
                d3.select(rect.node()).attr("fill","#fff").attr("transform","scale(1.1)");
                showTip(event,`<b>${d.key}</b><br>${d.count}张 (约${count}%)`);
            }).on("mousemove",moveTip).on("mouseout",()=>{ d3.select(rect.node()).attr("fill",color).attr("transform","scale(1)"); hideTip(); });
        }
    });

    // 图注
    let lx=ox, ly=oy+side*cell+20;
    agg.forEach((d,i)=>{
        svg.append("rect").attr("x",lx).attr("y",ly).attr("width",16).attr("height",16).attr("fill",PAL[i%4]).attr("stroke","#000").attr("stroke-width",2);
        typeD3Text(svg.append("text").attr("x",lx+22).attr("y",ly+13).attr("fill","#ccc").style("font-size","13px").style("font-family","'Noto Sans SC',sans-serif"), `${d.key} (${Math.round(d.count/total*100)}%)`, 400+i*120, 18);
        lx+=(d.key.length*14+70);
        if(lx>w-100){ lx=ox; ly+=25; }
    });
}

// ========================
// 通用柱状图（兜底）
// ========================
function renderGenericBar(host, rows, col){
    const agg=aggregate(rows,col);
    const {w,h}=vizSize(host);
    const px=80,py=60,mx=w-40,my=h-90;
    const xS=d3.scaleBand().domain(agg.map(d=>d.key)).range([px,mx]).padding(0.35);
    const yS=d3.scaleLinear().domain([0,d3.max(agg,d=>d.count)]).range([my,py]).nice();
    const total=d3.sum(agg,d=>d.count);
    const svg=pixelSvg(host,w,h);

    typeD3Text(svg.append("text").attr("x",px).attr("y",38).attr("class","chart-title"), col+" 分布", 0, 20);

    agg.forEach((d,i)=>{
        const color=PAL[i%4];
        const rect=svg.append("rect").attr("x",xS(d.key)).attr("y",yS(0)).attr("width",xS.bandwidth()).attr("height",0).attr("fill",color).attr("stroke","#000").attr("stroke-width",2);
        rect.transition().duration(800).delay(i*60).ease(d3.easeBackOut).attr("y",yS(d.count)).attr("height",yS(0)-yS(d.count));
        typeD3Text(svg.append("text").attr("x",xS(d.key)+xS.bandwidth()/2).attr("y",yS(d.count)-8).attr("text-anchor","middle").attr("fill",color).style("font-size","14px").style("font-weight","900"), String(d.count), 280+i*90, 16);
        rect.on("mouseover",(event)=>{
            d3.select(rect.node()).attr("fill","#fff");
            showTip(event,`<b>${d.key}</b><br>${d.count}张 (${Math.round(d.count/total*100)}%)`);
        }).on("mousemove",moveTip).on("mouseout",()=>{ d3.select(rect.node()).attr("fill",color); hideTip(); });
    });
    styleAxis(svg.append("g").attr("transform",`translate(0,${my})`).call(d3.axisBottom(xS)));
    styleAxis(svg.append("g").attr("transform",`translate(${px},0)`).call(d3.axisLeft(yS).ticks(5)));
    typeD3Text(svg.append("text").attr("x",(px+mx)/2).attr("y",h-18).attr("class","axis-label").attr("text-anchor","middle"), col, 180, 18);
    typeD3Text(svg.append("text").attr("x",18).attr("y",(py+my)/2).attr("class","axis-label").attr("text-anchor","middle").attr("transform",`rotate(-90,18,${(py+my)/2})`), "数量", 320, 18);
}

// ========================
// 路由
// ========================
function renderColumn(host, col, rows){
    host.innerHTML="";
    if(col==="图片") renderImageGalaxy(host,rows);
    else if(col==="阶段") renderPhaseUniverse(host,rows,col);
    else if(col==="早期典型传播平台") renderBrickWall(host,rows,col);
    else if(col==="图像来源类型") renderSankeyish(host,rows,col);
    else if(col==="文字数量") renderStepWave(host,rows,col);
    else if(col==="黑白/彩色") renderPixelDonut(host,rows,col);
    else if(col==="图片清晰度") renderPixelTowers(host,rows,col);
    else if(col==="人物原型") renderPixelRadar(host,rows,col);
    else if(col==="情绪表达是否直接") renderMirrorButterfly(host,rows,col);
    else if(col==="情绪包装度（1-5）") renderLevelMeter(host,rows,col);
    else if(col==="模板类型") renderWaffleGrid(host,rows,col);
    else renderGenericBar(host,rows,col);
}

// ========================
// 页面构建
// ========================
const CHART_DESC={
    "图片":"所有样本图片的视觉星系展示。悬浮查看备注，点击放大灯箱。",
    "阶段":"按传播阶段分层的生长树。切换阶段查看对应图片演变。",
    "早期典型传播平台":"各传播平台的像素方块矩阵，每块代表1张图片。",
    "图像来源类型":"图像来源到核心模因库的贝塞尔流向图。",
    "文字数量":"图片中文字字数的分布直方图，反映创作倾向。",
    "黑白/彩色":"图片色调组成的环形饼图，反映视觉风格。",
    "图片清晰度":"各清晰度等级的像素信号塔，高度对应数量。",
    "人物原型":"人物角色的雷达图，展示各类型的覆盖面。",
    "情绪表达是否直接":"直接与间接情绪表达方式的蝴蝶对比图。",
    "情绪包装度（1-5）":"情绪包装等级的复古电平仪，颜色反映烈度。",
    "模板类型":"模板类别的华夫方格比例图，每格约1%。",
};

function buildMain(){
    const main=document.getElementById("main");
    const columns=orderColumns(DATA.columns);
    columns.forEach((col,idx)=>{
        const sec=document.createElement("section");
        sec.className="page-section"; sec.id="sec_"+idx;
        sec.dataset.secTyped="0";

        const layout=document.createElement("div"); layout.className="viz-layout";
        const guide=document.createElement("div"); guide.className="viz-guide";

        const badge=document.createElement("div"); badge.className="step-badge";
        badge.textContent=""; badge.dataset.twFull=`维度 ${String(idx+1).padStart(2,"0")}`;

        const title=document.createElement("h2"); title.className="guide-title";
        title.textContent=""; title.dataset.twFull=String(col);

        const desc=document.createElement("p"); desc.className="guide-desc";
        desc.textContent=""; desc.dataset.twFull=String(CHART_DESC[col]||"数据维度分析中...");

        const legend=document.createElement("div"); legend.className="guide-legend"; legend.id="legend_"+idx;

        guide.appendChild(badge); guide.appendChild(title); guide.appendChild(desc); guide.appendChild(legend);

        const screen=document.createElement("div"); screen.className="viz-screen-container";
        const header=document.createElement("div"); header.className="screen-header";

        const spanL=document.createElement("span");
        const blink=document.createElement("span"); blink.className="status-blink";
        const spanLText=document.createElement("span"); spanLText.textContent=""; spanLText.dataset.twFull="模块激活："+String(col);
        spanL.appendChild(blink); spanL.appendChild(spanLText);

        const spanR=document.createElement("span"); spanR.textContent=""; spanR.dataset.twFull="样本总量："+DATA.rows.length;

        header.appendChild(spanL); header.appendChild(spanR);

        const wrap=document.createElement("div"); wrap.className="viz-wrap";
        wrap.dataset.col=String(col); wrap.dataset.rendered="0";

        screen.appendChild(header); screen.appendChild(wrap);
        layout.appendChild(guide); layout.appendChild(screen);
        sec.appendChild(layout);
        main.appendChild(sec);
    });

    const secObs=new IntersectionObserver(entries=>{
        entries.forEach(e=>{
            if(!e.isIntersecting) return;
            const sec=e.target;
            if(sec.dataset.secTyped!=="0") return;
            sec.dataset.secTyped="1";
            const b=sec.querySelector(".step-badge");
            const t=sec.querySelector(".guide-title");
            const d=sec.querySelector(".guide-desc");
            const spans=sec.querySelectorAll(".screen-header > span");
            const spanLText=spans[0]&&spans[0].querySelector("span:not(.status-blink)");
            const spanR=spans[1];
            if(b&&b.dataset.twFull) typewriterEl(b,b.dataset.twFull,24,0);
            if(t&&t.dataset.twFull) typewriterEl(t,t.dataset.twFull,22,120);
            if(d&&d.dataset.twFull) typewriterEl(d,d.dataset.twFull,16,280);
            if(spanLText&&spanLText.dataset.twFull) typewriterEl(spanLText,spanLText.dataset.twFull,20,520);
            if(spanR&&spanR.dataset.twFull) typewriterEl(spanR,spanR.dataset.twFull,20,620);
        });
    },{threshold:0.08,rootMargin:"40px 0px"});
    document.querySelectorAll(".page-section").forEach(s=>secObs.observe(s));

    const obs=new IntersectionObserver(entries=>{
        entries.forEach(e=>{
            if(e.isIntersecting){
                const wrap=e.target;
                if(wrap.dataset.rendered==="0"){
                    wrap.dataset.rendered="1";
                    renderColumn(wrap,wrap.dataset.col,DATA.rows);
                }
            }
        });
    },{threshold:0.05,rootMargin:"100px"});
    document.querySelectorAll(".viz-wrap").forEach(el=>obs.observe(el));
}

// ========================
// 粒子背景（与 meme4 一致：GlitchPixel + 鼠标排斥）
// ========================
function initParticles(){
    const bgCanvas=document.getElementById("particleCanvas");
    const bgCtx=bgCanvas.getContext("2d");
    let width,height;
    const colors=[PX.c3,PX.c1,PX.c4,PX.c2,"#ffffff","#e91e63","#00bcd4","#ffeb3b"];
    const mouse={x:-1000,y:-1000};
    window.addEventListener("mousemove",e=>{ mouse.x=e.clientX; mouse.y=e.clientY; });
    function resize(){ width=bgCanvas.width=window.innerWidth; height=bgCanvas.height=window.innerHeight; }
    window.addEventListener("resize",resize); resize();

    class GlitchPixel{
        constructor(){ this.reset(); this.x=Math.random()*width; this.y=Math.random()*height; }
        reset(){
            this.size=Math.random()>0.7 ? (Math.random()*12+8) : (Math.random()*4+4);
            this.color=colors[Math.floor(Math.random()*colors.length)];
            this.speedX=(Math.random()-0.5)*1.5; this.speedY=(Math.random()-0.5)*1.5-0.5;
            this.opacity=Math.random()*0.8+0.2;
        }
        update(){
            const dx=mouse.x-this.x, dy=mouse.y-this.y;
            const dist=Math.sqrt(dx*dx+dy*dy);
            if(dist<100){ this.x-=(dx/dist)*2; this.y-=(dy/dist)*2; }
            this.x+=this.speedX; this.y+=this.speedY;
            if(this.x>width+20) this.x=-20; else if(this.x<-20) this.x=width+20;
            if(this.y>height+20) this.y=-20; else if(this.y<-20) this.y=height+20;
            if(Math.random()<0.002){ this.x+=(Math.random()-0.5)*40; this.color=colors[Math.floor(Math.random()*colors.length)]; }
        }
        draw(){ bgCtx.globalAlpha=this.opacity; bgCtx.fillStyle=this.color; bgCtx.fillRect(Math.floor(this.x),Math.floor(this.y),this.size,this.size); }
    }
    const particles=[];
    function particleCount(){ return Math.max(40, Math.floor(window.innerWidth/10)); }
    function refill(){ while(particles.length<particleCount()) particles.push(new GlitchPixel()); while(particles.length>particleCount()) particles.pop(); }
    refill();
    window.addEventListener("resize",()=>{ resize(); refill(); });
    function animateBg(){
        bgCtx.clearRect(0,0,width,height);
        particles.forEach(p=>{ p.update(); p.draw(); });
        bgCtx.globalAlpha=1;
        requestAnimationFrame(animateBg);
    }
    animateBg();
}

// ========================
// 滚动进度条
// ========================
window.addEventListener("scroll",()=>{
    const pct=(window.scrollY/(document.body.scrollHeight-window.innerHeight))*100;
    document.getElementById("progress-bar").style.width=pct+"%";
});

buildMain();
initParticles();
</script>
</body>
</html>
"""

out = HTML.replace("__DATA_PLACEHOLDER__", payload)
(ROOT / "场景一.html").write_text(out, encoding="utf-8")
print("Wrote 场景一.html, bytes:", len(out.encode("utf-8")))
