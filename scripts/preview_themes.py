#!/usr/bin/env python3
"""テーマのプレビュー/ギャラリー生成ツール (本番運用には使わない)。

本番で使うテーマ (dark / cute / pixel_sweets) は aggregate_ai_usage.py に定義済み。
このスクリプトは、検討して採用を見送った実験テーマ
(terminal / minimal / neon / ocean / paper / pixel) を保管し、
全テーマを実データで描画して 1 枚の HTML に並べて見比べるためのもの。

使い方:
    python3 scripts/preview_themes.py
    # /tmp/ai-usage-preview/index.html をブラウザで開く (SMIL アニメは要ブラウザ)

新テーマを足したくなったらここで試作 → 良ければ aggregate_ai_usage.py へ移す。
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
import aggregate_ai_usage as agg  # noqa: E402

OUT_DIR = Path("/tmp/ai-usage-preview")
PROJECTS_DIR = Path.home() / ".claude/projects"
WINDOW_DAYS = 30

# --- 新規テーマ: terminal ---------------------------------------------------
TERMINAL = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">
  <style>
    .bg {{ fill: #0b0e14; }}
    .title {{ fill: #7ee787; font-size: 16px; font-weight: 600; }}
    .subtitle {{ fill: #4d5566; font-size: 11px; }}
    .stat-num {{ fill: #58d364; font-size: 34px; font-weight: 700; }}
    .stat-label {{ fill: #6e7681; font-size: 11px; }}
    .section {{ fill: #d29922; font-size: 12px; font-weight: 600; }}
    .row-label {{ fill: #adbac7; font-size: 12px; }}
    .row-value {{ fill: #6e7681; font-size: 11px; }}
    .bar {{ fill: #2ea043; rx: 0; }}
    .spark {{ fill: none; stroke: #58d364; stroke-width: 1.5; }}
    .spark-area {{ fill: url(#sparkGrad); opacity: 0.4; }}
    .rule {{ stroke: #21262d; stroke-width: 1; }}
    @keyframes fadein {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    .anim {{ animation: fadein 0.5s ease-out both; }}
  </style>
  <defs>
    <linearGradient id="barGrad" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0%" stop-color="#2ea043"/><stop offset="100%" stop-color="#2ea043"/>
    </linearGradient>
    <linearGradient id="sparkGrad" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0%" stop-color="#58d364" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="#58d364" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect class="bg" width="{width}" height="{height}" rx="8"/>
  <g class="anim">
    <text x="20" y="34" class="title">$ claude-code --stats --days {window}</text>
    <line class="rule" x1="20" y1="48" x2="{spark_end_x}" y2="48"/>
  </g>
  <g class="anim" style="animation-delay: 0.1s">
    <text x="20"  y="120" class="stat-num">{sessions}</text>
    <text x="20"  y="142" class="stat-label">sessions</text>
    <text x="220" y="120" class="stat-num">{tool_calls}</text>
    <text x="220" y="142" class="stat-label">tool_calls</text>
    <text x="460" y="120" class="stat-num">{skills}</text>
    <text x="460" y="142" class="stat-label">skills</text>
  </g>
  <g class="anim" style="animation-delay: 0.2s">
    <text x="20" y="180" class="section">top_tools:</text>
    {top_tools_svg}
  </g>
  <g class="anim" style="animation-delay: 0.3s">
    <text x="20" y="345" class="section">top_skills:</text>
    {top_skills_svg}
  </g>
  <g class="anim" style="animation-delay: 0.4s">
    <text x="20" y="430" class="section">activity:</text>
    <path class="spark-area" d="{sparkline} L{spark_end_x},{spark_floor} L20,{spark_floor} Z"/>
    <path class="spark" d="{sparkline}">
      <animate attributeName="stroke-dasharray" from="0,2000" to="2000,0" dur="1.2s" fill="freeze"/>
    </path>
    <text x="{spark_end_x}" y="478" class="subtitle" text-anchor="end">_</text>
  </g>
</svg>
""".replace("{spark_end_x}", str(agg.SVG_WIDTH_PX - 20)).replace("{spark_floor}", str(agg.SPARK_FLOOR))

# --- 新規テーマ: minimal ----------------------------------------------------
MINIMAL = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" font-family="-apple-system, BlinkMacSystemFont, 'Helvetica Neue', sans-serif">
  <style>
    .bg {{ fill: #fbfbfa; }}
    .title {{ fill: #9a9a93; font-size: 12px; font-weight: 600; letter-spacing: 2px; }}
    .subtitle {{ fill: #b9b9b2; font-size: 10px; letter-spacing: 1px; }}
    .stat-num {{ fill: #1a1a1a; font-size: 40px; font-weight: 600; }}
    .stat-label {{ fill: #9a9a93; font-size: 10px; letter-spacing: 1px; }}
    .section {{ fill: #9a9a93; font-size: 11px; font-weight: 600; letter-spacing: 1px; }}
    .row-label {{ fill: #1a1a1a; font-size: 12px; }}
    .row-value {{ fill: #9a9a93; font-size: 11px; }}
    .bar {{ fill: #e6e6e1; rx: 1; }}
    .spark {{ fill: none; stroke: #1a1a1a; stroke-width: 1.2; }}
    .spark-area {{ fill: none; }}
    .rule {{ stroke: #ececea; stroke-width: 1; }}
    @keyframes fadein {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    .anim {{ animation: fadein 0.7s ease-out both; }}
  </style>
  <defs>
    <linearGradient id="barGrad" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0%" stop-color="#e6e6e1"/><stop offset="100%" stop-color="#e6e6e1"/>
    </linearGradient>
    <linearGradient id="sparkGrad" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect class="bg" width="{width}" height="{height}"/>
  <g class="anim">
    <text x="20" y="40" class="title">AI USAGE</text>
    <text x="{spark_end_x}" y="40" class="subtitle" text-anchor="end">LAST {window} DAYS</text>
  </g>
  <g class="anim" style="animation-delay: 0.1s">
    <text x="20"  y="120" class="stat-num">{sessions}</text>
    <text x="20"  y="144" class="stat-label">SESSIONS</text>
    <text x="220" y="120" class="stat-num">{tool_calls}</text>
    <text x="220" y="144" class="stat-label">TOOL CALLS</text>
    <text x="460" y="120" class="stat-num">{skills}</text>
    <text x="460" y="144" class="stat-label">SKILLS</text>
  </g>
  <line class="rule" x1="20" y1="165" x2="{spark_end_x}" y2="165"/>
  <g class="anim" style="animation-delay: 0.2s">
    <text x="20" y="186" class="section">TOP TOOLS</text>
    {top_tools_svg}
  </g>
  <g class="anim" style="animation-delay: 0.3s">
    <text x="20" y="345" class="section">TOP SKILLS</text>
    {top_skills_svg}
  </g>
  <g class="anim" style="animation-delay: 0.4s">
    <text x="20" y="430" class="section">30-DAY TREND</text>
    <path class="spark" d="{sparkline}">
      <animate attributeName="stroke-dasharray" from="0,2000" to="2000,0" dur="1.5s" fill="freeze"/>
    </path>
  </g>
</svg>
""".replace("{spark_end_x}", str(agg.SVG_WIDTH_PX - 20)).replace("{spark_floor}", str(agg.SPARK_FLOOR))

# --- 新規テーマ: neon (synthwave) ------------------------------------------
NEON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" font-family="ui-monospace, Menlo, Consolas, monospace">
  <style>
    .bg {{ fill: #1a0b2e; }}
    .title {{ fill: #22d3ee; font-size: 18px; font-weight: 700; filter: url(#glow); }}
    .subtitle {{ fill: #a78bda; font-size: 11px; }}
    .stat-num {{ fill: #ff2e97; font-size: 36px; font-weight: 800; filter: url(#glow); }}
    .stat-label {{ fill: #a78bda; font-size: 11px; }}
    .section {{ fill: #22d3ee; font-size: 12px; font-weight: 700; }}
    .row-label {{ fill: #f0e7ff; font-size: 12px; }}
    .row-value {{ fill: #a78bda; font-size: 11px; }}
    .bar {{ fill: url(#barGrad); rx: 2; filter: url(#glow); }}
    .spark {{ fill: none; stroke: #22d3ee; stroke-width: 2; filter: url(#glow); }}
    .spark-area {{ fill: url(#sparkGrad); opacity: 0.5; }}
    .grid {{ stroke: #ff2e97; stroke-width: 0.5; opacity: 0.25; }}
    @keyframes fadein {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    .anim {{ animation: fadein 0.6s ease-out both; }}
  </style>
  <defs>
    <filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="2.2" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <linearGradient id="barGrad" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0%" stop-color="#ff2e97"/><stop offset="100%" stop-color="#22d3ee"/>
    </linearGradient>
    <linearGradient id="sparkGrad" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0%" stop-color="#22d3ee" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="#22d3ee" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect class="bg" width="{width}" height="{height}" rx="12"/>
  <line class="grid" x1="0" y1="455" x2="{width}" y2="455"/>
  <line class="grid" x1="0" y1="468" x2="{width}" y2="468"/>
  <g class="anim">
    <text x="20" y="36" class="title">▰▰ AI · CLAUDE CODE ▰▰</text>
    <text x="20" y="58" class="subtitle">last {window} days · neon edition</text>
  </g>
  <g class="anim" style="animation-delay: 0.1s">
    <text x="20"  y="120" class="stat-num">{sessions}</text>
    <text x="20"  y="142" class="stat-label">sessions</text>
    <text x="220" y="120" class="stat-num">{tool_calls}</text>
    <text x="220" y="142" class="stat-label">tool calls</text>
    <text x="460" y="120" class="stat-num">{skills}</text>
    <text x="460" y="142" class="stat-label">skills used</text>
  </g>
  <g class="anim" style="animation-delay: 0.2s">
    <text x="20" y="180" class="section">▶ Top tools</text>
    {top_tools_svg}
  </g>
  <g class="anim" style="animation-delay: 0.3s">
    <text x="20" y="345" class="section">▶ Top skills</text>
    {top_skills_svg}
  </g>
  <g class="anim" style="animation-delay: 0.4s">
    <text x="20" y="430" class="section">▶ Daily activity</text>
    <path class="spark-area" d="{sparkline} L{spark_end_x},{spark_floor} L20,{spark_floor} Z"/>
    <path class="spark" d="{sparkline}">
      <animate attributeName="stroke-dasharray" from="0,2000" to="2000,0" dur="1.4s" fill="freeze"/>
    </path>
  </g>
</svg>
""".replace("{spark_end_x}", str(agg.SVG_WIDTH_PX - 20)).replace("{spark_floor}", str(agg.SPARK_FLOOR))

# --- 新規テーマ: ocean (modern gradient) -----------------------------------
OCEAN = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif">
  <style>
    .title {{ fill: #e0f2fe; font-size: 18px; font-weight: 700; }}
    .subtitle {{ fill: #7dd3fc; font-size: 11px; }}
    .stat-num {{ fill: #38bdf8; font-size: 36px; font-weight: 800; }}
    .stat-label {{ fill: #93c5e8; font-size: 11px; }}
    .section {{ fill: #e0f2fe; font-size: 12px; font-weight: 700; }}
    .row-label {{ fill: #e0f2fe; font-size: 12px; }}
    .row-value {{ fill: #93c5e8; font-size: 11px; }}
    .bar {{ fill: url(#barGrad); rx: 7; }}
    .spark {{ fill: none; stroke: #5eead4; stroke-width: 2.5; stroke-linecap: round; }}
    .spark-area {{ fill: url(#sparkGrad); opacity: 0.5; }}
    @keyframes fadein {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    .anim {{ animation: fadein 0.6s ease-out both; }}
  </style>
  <defs>
    <linearGradient id="bgGrad" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0%" stop-color="#0a2540"/><stop offset="100%" stop-color="#0e7490"/>
    </linearGradient>
    <linearGradient id="barGrad" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0%" stop-color="#38bdf8"/><stop offset="100%" stop-color="#5eead4"/>
    </linearGradient>
    <linearGradient id="sparkGrad" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0%" stop-color="#5eead4" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="#5eead4" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect width="{width}" height="{height}" rx="16" fill="url(#bgGrad)"/>
  <g class="anim">
    <text x="20" y="36" class="title">🌊 AI Pair Programming · Claude Code</text>
    <text x="20" y="58" class="subtitle">last {window} days · powered by ~/.claude/projects</text>
  </g>
  <g class="anim" style="animation-delay: 0.1s">
    <text x="20"  y="120" class="stat-num">{sessions}</text>
    <text x="20"  y="142" class="stat-label">sessions</text>
    <text x="220" y="120" class="stat-num">{tool_calls}</text>
    <text x="220" y="142" class="stat-label">tool calls</text>
    <text x="460" y="120" class="stat-num">{skills}</text>
    <text x="460" y="142" class="stat-label">skills used</text>
  </g>
  <g class="anim" style="animation-delay: 0.2s">
    <text x="20" y="180" class="section">Top tools</text>
    {top_tools_svg}
  </g>
  <g class="anim" style="animation-delay: 0.3s">
    <text x="20" y="345" class="section">Top skills</text>
    {top_skills_svg}
  </g>
  <g class="anim" style="animation-delay: 0.4s">
    <text x="20" y="430" class="section">Daily activity</text>
    <path class="spark-area" d="{sparkline} L{spark_end_x},{spark_floor} L20,{spark_floor} Z"/>
    <path class="spark" d="{sparkline}">
      <animate attributeName="stroke-dasharray" from="0,2000" to="2000,0" dur="1.4s" fill="freeze"/>
    </path>
  </g>
</svg>
""".replace("{spark_end_x}", str(agg.SVG_WIDTH_PX - 20)).replace("{spark_floor}", str(agg.SPARK_FLOOR))

# --- 新規テーマ: paper (editorial) -----------------------------------------
PAPER = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" font-family="'Iowan Old Style', Georgia, 'Times New Roman', serif">
  <style>
    .bg {{ fill: #f6f1e7; }}
    .title {{ fill: #2b2b2b; font-size: 19px; font-weight: 700; }}
    .subtitle {{ fill: #8a8270; font-size: 11px; font-style: italic; }}
    .stat-num {{ fill: #1c1c1c; font-size: 38px; font-weight: 700; }}
    .stat-label {{ fill: #8a8270; font-size: 11px; font-style: italic; }}
    .section {{ fill: #6b4f2a; font-size: 12px; font-weight: 700; letter-spacing: 1px; }}
    .row-label {{ fill: #2b2b2b; font-size: 12px; }}
    .row-value {{ fill: #8a8270; font-size: 11px; }}
    .bar {{ fill: url(#barGrad); rx: 1; }}
    .spark {{ fill: none; stroke: #6b4f2a; stroke-width: 1.5; }}
    .spark-area {{ fill: url(#sparkGrad); opacity: 0.35; }}
    .rule {{ stroke: #d8cdb6; stroke-width: 1; }}
    @keyframes fadein {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
    .anim {{ animation: fadein 0.7s ease-out both; }}
  </style>
  <defs>
    <linearGradient id="barGrad" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0%" stop-color="#b08d57"/><stop offset="100%" stop-color="#cdb487"/>
    </linearGradient>
    <linearGradient id="sparkGrad" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0%" stop-color="#6b4f2a" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#6b4f2a" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect class="bg" width="{width}" height="{height}" rx="4"/>
  <g class="anim">
    <text x="20" y="36" class="title">The Claude Code Journal</text>
    <text x="20" y="56" class="subtitle">a record of the last {window} days</text>
    <line class="rule" x1="20" y1="66" x2="{spark_end_x}" y2="66"/>
  </g>
  <g class="anim" style="animation-delay: 0.1s">
    <text x="20"  y="124" class="stat-num">{sessions}</text>
    <text x="20"  y="146" class="stat-label">sessions</text>
    <text x="220" y="124" class="stat-num">{tool_calls}</text>
    <text x="220" y="146" class="stat-label">tool calls</text>
    <text x="460" y="124" class="stat-num">{skills}</text>
    <text x="460" y="146" class="stat-label">skills used</text>
  </g>
  <g class="anim" style="animation-delay: 0.2s">
    <text x="20" y="180" class="section">TOP TOOLS</text>
    {top_tools_svg}
  </g>
  <g class="anim" style="animation-delay: 0.3s">
    <text x="20" y="345" class="section">TOP SKILLS</text>
    {top_skills_svg}
  </g>
  <g class="anim" style="animation-delay: 0.4s">
    <text x="20" y="430" class="section">DAILY ACTIVITY</text>
    <path class="spark-area" d="{sparkline} L{spark_end_x},{spark_floor} L20,{spark_floor} Z"/>
    <path class="spark" d="{sparkline}">
      <animate attributeName="stroke-dasharray" from="0,2000" to="2000,0" dur="1.4s" fill="freeze"/>
    </path>
  </g>
</svg>
""".replace("{spark_end_x}", str(agg.SVG_WIDTH_PX - 20)).replace("{spark_floor}", str(agg.SPARK_FLOOR))

# --- 新規テーマ: pixel (retro 8-bit) ---------------------------------------
PIXEL = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" font-family="'Courier New', ui-monospace, monospace">
  <style>
    .bg {{ fill: #14182b; }}
    .title {{ fill: #ffd23f; font-size: 17px; font-weight: 700; letter-spacing: 1px; }}
    .subtitle {{ fill: #6c7293; font-size: 11px; }}
    .stat-num {{ fill: #41ead4; font-size: 34px; font-weight: 700; }}
    .stat-label {{ fill: #ff5d8f; font-size: 11px; font-weight: 700; }}
    .section {{ fill: #ffd23f; font-size: 12px; font-weight: 700; }}
    .row-label {{ fill: #e7ecff; font-size: 12px; }}
    .row-value {{ fill: #6c7293; font-size: 11px; }}
    .bar {{ fill: url(#barGrad); rx: 0; }}
    .spark {{ fill: none; stroke: #41ead4; stroke-width: 3; stroke-linejoin: miter; }}
    .spark-area {{ fill: url(#sparkGrad); opacity: 0.4; }}
    .px {{ fill: #ff5d8f; }}
    @keyframes blink {{ 50% {{ opacity: 0.2; }} }}
    .blink {{ animation: blink 1s steps(1) infinite; }}
  </style>
  <defs>
    <linearGradient id="barGrad" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0%" stop-color="#ff5d8f"/><stop offset="100%" stop-color="#ffd23f"/>
    </linearGradient>
    <linearGradient id="sparkGrad" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0%" stop-color="#41ead4" stop-opacity="0.5"/>
      <stop offset="100%" stop-color="#41ead4" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect class="bg" width="{width}" height="{height}"/>
  <rect class="px" x="0" y="0" width="{width}" height="6"/>
  <rect class="px" x="0" y="474" width="{width}" height="6"/>
  <text x="20" y="38" class="title">★ CLAUDE CODE · PLAYER 1 ★</text>
  <text x="20" y="58" class="subtitle">LAST {window} DAYS &gt;&gt; PRESS START</text>
  <text x="20"  y="120" class="stat-num">{sessions}</text>
  <text x="20"  y="142" class="stat-label">SESSIONS</text>
  <text x="220" y="120" class="stat-num">{tool_calls}</text>
  <text x="220" y="142" class="stat-label">TOOL CALLS</text>
  <text x="460" y="120" class="stat-num">{skills}</text>
  <text x="460" y="142" class="stat-label">SKILLS</text>
  <text x="20" y="180" class="section">▮ TOP TOOLS</text>
  {top_tools_svg}
  <text x="20" y="345" class="section">▮ TOP SKILLS</text>
  {top_skills_svg}
  <text x="20" y="430" class="section">▮ DAILY ACTIVITY</text>
  <path class="spark-area" d="{sparkline} L{spark_end_x},{spark_floor} L20,{spark_floor} Z"/>
  <path class="spark" d="{sparkline}"/>
  <text x="{spark_end_x}" y="462" class="stat-label blink" text-anchor="end">█</text>
</svg>
""".replace("{spark_end_x}", str(agg.SVG_WIDTH_PX - 20)).replace("{spark_floor}", str(agg.SPARK_FLOOR))

# pixel_sweets (採用テーマ) は aggregate_ai_usage.py に定義済みなのでここには持たない。
# 以下は採用を見送った実験テーマ。agg.THEMES に足してプレビューでだけ描画する。
agg.THEMES["terminal"] = TERMINAL
agg.THEMES["minimal"] = MINIMAL
agg.THEMES["neon"] = NEON
agg.THEMES["ocean"] = OCEAN
agg.THEMES["paper"] = PAPER
agg.THEMES["pixel"] = PIXEL


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=WINDOW_DAYS)
    files = agg.list_session_files(PROJECTS_DIR, cutoff)
    stats = agg.aggregate(files, cutoff)
    series = agg.daily_series(stats["daily"], cutoff, now)

    themes = ["pixel", "pixel_sweets", "dark", "cute", "terminal", "minimal", "neon", "ocean", "paper"]
    for theme in themes:
        svg = agg.render_svg(stats, series, theme)
        (OUT_DIR / f"{theme}.svg").write_text(svg)

    cards = "\n".join(
        f'<figure><figcaption>{t}</figcaption>'
        f'<img src="{t}.svg" width="800"></figure>'
        for t in themes
    )
    html = (
        "<!doctype html><meta charset=utf-8>"
        "<title>AI usage theme preview</title>"
        "<style>body{background:#30343c;font-family:sans-serif;margin:24px}"
        "figure{margin:0 0 32px}figcaption{color:#ddd;font:600 14px monospace;"
        "margin-bottom:8px}img{display:block;border:1px solid #555}</style>"
        f"<h1 style='color:#fff'>AI usage — 4 themes (sessions={stats['session_count']}, "
        f"tool_calls={stats['tool_call_count']})</h1>{cards}"
    )
    (OUT_DIR / "index.html").write_text(html)
    print(f"wrote {len(themes)} svgs + index.html to {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
