#!/usr/bin/env python3
"""Claude Code transcripts を集計し、サマリー JSON と SVG を出力する。

使い方:
    python3 aggregate_ai_usage.py \
        --projects-dir ~/.claude/projects \
        --json-out data/ai-usage.json \
        --svg-out images/ai-usage.svg \
        --days 30
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

WINDOW_DAYS_DEFAULT = 30
TOP_TOOLS = 5
TOP_SKILLS = 3
SVG_WIDTH_PX = 800
SVG_HEIGHT_PX = 360


def list_session_files(projects_dir: Path, cutoff: datetime) -> list[Path]:
    """対象期間内に更新された JSONL を返す。"""
    if not projects_dir.exists():
        return []
    cutoff_ts = cutoff.timestamp()
    files = []
    for project_dir in projects_dir.iterdir():
        if not project_dir.is_dir():
            continue
        for jsonl in project_dir.glob("*.jsonl"):
            if jsonl.stat().st_mtime >= cutoff_ts:
                files.append(jsonl)
    return files


def parse_tool_calls(jsonl_path: Path) -> list[dict]:
    """JSONL から tool_use エントリを抽出する。"""
    calls = []
    try:
        with jsonl_path.open() as f:
            for line in f:
                calls.extend(extract_calls_from_line(line))
    except (OSError, json.JSONDecodeError) as e:
        print(f"warn: skip {jsonl_path}: {e}", file=sys.stderr)
    return calls


def extract_calls_from_line(line: str) -> list[dict]:
    """1 行 (1 メッセージ) から tool_use 呼び出しを取り出す。"""
    line = line.strip()
    if not line:
        return []
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        return []
    timestamp = obj.get("timestamp")
    msg = obj.get("message")
    if not isinstance(msg, dict):
        return []
    content = msg.get("content")
    if not isinstance(content, list):
        return []
    return [
        build_call(c, timestamp)
        for c in content
        if isinstance(c, dict) and c.get("type") == "tool_use"
    ]


def build_call(content_item: dict, timestamp: str | None) -> dict:
    """tool_use コンテンツから集計用エントリを作る。"""
    name = content_item.get("name", "unknown")
    skill = None
    if name == "Skill":
        inp = content_item.get("input", {})
        if isinstance(inp, dict):
            skill = inp.get("skill")
    return {"tool": name, "skill": skill, "timestamp": timestamp}


def daily_buckets(calls: list[dict], cutoff: datetime) -> dict[str, int]:
    """日付 (YYYY-MM-DD) → 呼び出し数 の辞書を返す。"""
    buckets: dict[str, int] = defaultdict(int)
    for call in calls:
        day = call_to_day(call, cutoff)
        if day:
            buckets[day] += 1
    return buckets


def call_to_day(call: dict, cutoff: datetime) -> str | None:
    """call.timestamp を日付文字列に正規化。期間外は None。"""
    ts = call.get("timestamp")
    if not isinstance(ts, str):
        return None
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt < cutoff:
        return None
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d")


def aggregate(session_files: list[Path], cutoff: datetime) -> dict:
    """全集計を1つの dict にまとめる。"""
    all_calls: list[dict] = []
    for f in session_files:
        all_calls.extend(parse_tool_calls(f))
    tool_counts = Counter(c["tool"] for c in all_calls)
    skill_counts = Counter(c["skill"] for c in all_calls if c["skill"])
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window_days": (datetime.now(timezone.utc) - cutoff).days,
        "session_count": len(session_files),
        "tool_call_count": len(all_calls),
        "unique_tool_count": len(tool_counts),
        "unique_skill_count": len(skill_counts),
        "top_tools": tool_counts.most_common(TOP_TOOLS),
        "top_skills": skill_counts.most_common(TOP_SKILLS),
        "daily": dict(daily_buckets(all_calls, cutoff)),
    }


def daily_series(daily: dict[str, int], cutoff: datetime, today: datetime) -> list[int]:
    """cutoff から today までの日次系列 (欠損日は 0)。"""
    series = []
    day = cutoff.date()
    end = today.date()
    while day <= end:
        series.append(daily.get(day.strftime("%Y-%m-%d"), 0))
        day += timedelta(days=1)
    return series


def sparkline_path(series: list[int], x0: int, y0: int, w: int, h: int) -> str:
    """日次系列を SVG path 文字列にする。"""
    if not series:
        return ""
    peak = max(series) or 1
    step = w / max(len(series) - 1, 1)
    points = [
        (x0 + i * step, y0 + h - (v / peak) * h)
        for i, v in enumerate(series)
    ]
    head = f"M{points[0][0]:.1f},{points[0][1]:.1f}"
    tail = " ".join(f"L{x:.1f},{y:.1f}" for x, y in points[1:])
    return f"{head} {tail}"


def bar_row(label: str, value: int, max_value: int, y: int, max_bar: int) -> str:
    """Top tools/skills の 1 行ぶんの SVG を返す。"""
    width = (value / max_value) * max_bar if max_value else 0
    safe_label = escape_xml(label)
    return (
        f'<text x="20" y="{y}" class="row-label">{safe_label}</text>'
        f'<rect x="200" y="{y - 12}" height="14" width="{width:.1f}" '
        f'class="bar"><animate attributeName="width" from="0" to="{width:.1f}" '
        f'dur="1.2s" fill="freeze"/></rect>'
        f'<text x="{210 + width:.1f}" y="{y}" class="row-value">{value}</text>'
    )


def escape_xml(text: str) -> str:
    """SVG に埋め込む文字列を最小限エスケープ。"""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def render_top_section(items: list[tuple[str, int]], y_start: int, max_bar: int) -> str:
    """Top tools / skills セクションを描画。"""
    if not items:
        return ""
    max_value = max(v for _, v in items)
    rows = [
        bar_row(label, value, max_value, y_start + i * 22, max_bar)
        for i, (label, value) in enumerate(items)
    ]
    return "\n".join(rows)


def render_svg(stats: dict, series: list[int], theme: str) -> str:
    """サマリー SVG を組み立てる。"""
    spark = sparkline_path(series, x0=20, y0=300, w=SVG_WIDTH_PX - 40, h=40)
    template = THEMES[theme]
    return template.format(
        width=SVG_WIDTH_PX,
        height=SVG_HEIGHT_PX,
        sessions=stats["session_count"],
        tool_calls=stats["tool_call_count"],
        skills=stats["unique_skill_count"],
        window=stats["window_days"],
        top_tools_svg=render_top_section(stats["top_tools"], y_start=160, max_bar=400),
        top_skills_svg=render_top_section(stats["top_skills"], y_start=250, max_bar=400),
        sparkline=spark,
    )


SVG_TEMPLATE_DARK = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif">
  <style>
    .bg {{ fill: #0d1117; }}
    .title {{ fill: #c9d1d9; font-size: 18px; font-weight: 600; }}
    .subtitle {{ fill: #8b949e; font-size: 11px; }}
    .stat-num {{ fill: #58a6ff; font-size: 36px; font-weight: 700; }}
    .stat-label {{ fill: #8b949e; font-size: 11px; }}
    .section {{ fill: #c9d1d9; font-size: 12px; font-weight: 600; }}
    .row-label {{ fill: #c9d1d9; font-size: 12px; }}
    .row-value {{ fill: #8b949e; font-size: 11px; }}
    .bar {{ fill: url(#barGrad); rx: 3; }}
    .spark {{ fill: none; stroke: #3fb950; stroke-width: 2; }}
    .spark-area {{ fill: url(#sparkGrad); opacity: 0.5; }}
    @keyframes fadein {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    .anim {{ animation: fadein 0.6s ease-out both; }}
  </style>
  <defs>
    <linearGradient id="barGrad" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0%" stop-color="#58a6ff"/>
      <stop offset="100%" stop-color="#3fb950"/>
    </linearGradient>
    <linearGradient id="sparkGrad" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0%" stop-color="#3fb950" stop-opacity="0.6"/>
      <stop offset="100%" stop-color="#3fb950" stop-opacity="0"/>
    </linearGradient>
  </defs>

  <rect class="bg" width="{width}" height="{height}" rx="12"/>

  <g class="anim">
    <text x="20" y="32" class="title">🤖 AI Pair Programming with Claude Code</text>
    <text x="20" y="50" class="subtitle">last {window} days · powered by ~/.claude/projects</text>
  </g>

  <g class="anim" style="animation-delay: 0.1s">
    <text x="20"  y="100" class="stat-num">{sessions}</text>
    <text x="20"  y="118" class="stat-label">sessions</text>
    <text x="220" y="100" class="stat-num">{tool_calls}</text>
    <text x="220" y="118" class="stat-label">tool calls</text>
    <text x="460" y="100" class="stat-num">{skills}</text>
    <text x="460" y="118" class="stat-label">skills used</text>
  </g>

  <g class="anim" style="animation-delay: 0.2s">
    <text x="20" y="150" class="section">Top tools</text>
    {top_tools_svg}
  </g>

  <g class="anim" style="animation-delay: 0.3s">
    <text x="20" y="240" class="section">Top skills</text>
    {top_skills_svg}
  </g>

  <g class="anim" style="animation-delay: 0.4s">
    <text x="20" y="295" class="section">Daily activity</text>
    <path class="spark-area" d="{sparkline} L{spark_end_x},{spark_floor} L20,{spark_floor} Z"/>
    <path class="spark" d="{sparkline}">
      <animate attributeName="stroke-dasharray" from="0,2000" to="2000,0" dur="1.4s" fill="freeze"/>
    </path>
  </g>
</svg>
""".replace("{spark_end_x}", str(SVG_WIDTH_PX - 20)).replace("{spark_floor}", "340")


SVG_TEMPLATE_CUTE = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" font-family="-apple-system, BlinkMacSystemFont, 'Hiragino Maru Gothic ProN', 'Comic Sans MS', sans-serif">
  <style>
    .bg {{ fill: #fff5f9; }}
    .title {{ fill: #d6336c; font-size: 18px; font-weight: 700; }}
    .subtitle {{ fill: #b06b8a; font-size: 11px; }}
    .stat-num {{ fill: #ec4899; font-size: 36px; font-weight: 800; }}
    .stat-label {{ fill: #b06b8a; font-size: 11px; }}
    .section {{ fill: #d6336c; font-size: 12px; font-weight: 700; }}
    .row-label {{ fill: #6b3a52; font-size: 12px; }}
    .row-value {{ fill: #b06b8a; font-size: 11px; }}
    .bar {{ fill: url(#barGrad); rx: 7; }}
    .spark {{ fill: none; stroke: #f472b6; stroke-width: 2.5; stroke-linecap: round; stroke-linejoin: round; }}
    .spark-area {{ fill: url(#sparkGrad); opacity: 0.55; }}
    .paw {{ fill: #f9c2da; opacity: 0.55; }}
    .heart {{ fill: #ec4899; }}
    @keyframes fadein {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
    @keyframes bob {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-2px); }} }}
    @keyframes beat {{ 0%, 100% {{ transform: scale(1); }} 30% {{ transform: scale(1.25); }} }}
    .anim {{ animation: fadein 0.6s ease-out both; }}
    .bob {{ animation: bob 1.8s ease-in-out infinite; transform-origin: center; }}
    .beat {{ animation: beat 1.2s ease-in-out infinite; transform-origin: center; transform-box: fill-box; }}
  </style>
  <defs>
    <linearGradient id="barGrad" x1="0" x2="1" y1="0" y2="0">
      <stop offset="0%" stop-color="#f9a8d4"/>
      <stop offset="100%" stop-color="#c084fc"/>
    </linearGradient>
    <linearGradient id="sparkGrad" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0%" stop-color="#f472b6" stop-opacity="0.55"/>
      <stop offset="100%" stop-color="#f472b6" stop-opacity="0"/>
    </linearGradient>
    <symbol id="paw" viewBox="0 0 32 32">
      <circle cx="16" cy="20" r="7"/>
      <ellipse cx="7" cy="13" rx="3" ry="4"/>
      <ellipse cx="13" cy="8" rx="3" ry="4"/>
      <ellipse cx="19" cy="8" rx="3" ry="4"/>
      <ellipse cx="25" cy="13" rx="3" ry="4"/>
    </symbol>
  </defs>

  <rect class="bg" width="{width}" height="{height}" rx="22"/>

  <use href="#paw" class="paw" x="720" y="14"  width="28" height="28" transform="rotate(20 734 28)"/>
  <use href="#paw" class="paw" x="755" y="40"  width="20" height="20" transform="rotate(-15 765 50)"/>
  <use href="#paw" class="paw" x="700" y="320" width="22" height="22" transform="rotate(-10 711 331)"/>
  <use href="#paw" class="paw" x="740" y="300" width="16" height="16" transform="rotate(25 748 308)"/>

  <g class="anim">
    <text x="20" y="32" class="title">🐾 Coding with Claude (and the cats)</text>
    <text x="20" y="50" class="subtitle">last {window} days · 🐱 Nyan1-Go &amp; Nyan2-Go supervising</text>
  </g>

  <g class="anim" style="animation-delay: 0.1s">
    <text x="20"  y="100" class="stat-num">{sessions}</text>
    <text x="20"  y="118" class="stat-label">sessions ✨</text>
    <text x="220" y="100" class="stat-num">{tool_calls}</text>
    <text x="220" y="118" class="stat-label">tool calls 🛠️</text>
    <text x="460" y="100" class="stat-num">{skills}</text>
    <text x="460" y="118" class="stat-label">skills used 💖</text>
  </g>

  <g class="anim" style="animation-delay: 0.2s">
    <text x="20" y="150" class="section">🌷 Top tools</text>
    {top_tools_svg}
  </g>

  <g class="anim" style="animation-delay: 0.3s">
    <text x="20" y="240" class="section">🍡 Top skills</text>
    {top_skills_svg}
  </g>

  <g class="anim" style="animation-delay: 0.4s">
    <text x="20" y="295" class="section">🌸 Daily activity</text>
    <path class="spark-area" d="{sparkline} L{spark_end_x},{spark_floor} L20,{spark_floor} Z"/>
    <path class="spark" d="{sparkline}">
      <animate attributeName="stroke-dasharray" from="0,2000" to="2000,0" dur="1.6s" fill="freeze"/>
    </path>
    <g class="bob">
      <text x="{spark_end_x}" y="312" font-size="16" text-anchor="middle">🐱</text>
    </g>
    <path class="heart beat" d="M28 333 q-6 -6 -10 -2 q-4 4 0 8 l10 10 l10 -10 q4 -4 0 -8 q-4 -4 -10 2 z" transform="translate(720 0) scale(0.55)"/>
  </g>
</svg>
""".replace("{spark_end_x}", str(SVG_WIDTH_PX - 20)).replace("{spark_floor}", "340")


THEMES = {
    "dark": SVG_TEMPLATE_DARK,
    "cute": SVG_TEMPLATE_CUTE,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projects-dir", type=Path, required=True)
    parser.add_argument("--json-out", type=Path, required=True)
    parser.add_argument("--svg-out", type=Path, required=True)
    parser.add_argument("--days", type=int, default=WINDOW_DAYS_DEFAULT)
    parser.add_argument("--theme", choices=sorted(THEMES), default="dark")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=args.days)
    files = list_session_files(args.projects_dir.expanduser(), cutoff)
    stats = aggregate(files, cutoff)
    series = daily_series(stats["daily"], cutoff, now)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.svg_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(stats, ensure_ascii=False, indent=2))
    args.svg_out.write_text(render_svg(stats, series, args.theme))
    print(
        f"theme={args.theme} sessions={stats['session_count']} "
        f"tool_calls={stats['tool_call_count']} "
        f"skills={stats['unique_skill_count']}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
