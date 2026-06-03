# Plan 001: AI 使用状況の可視化

Issue: https://github.com/mikkegt/mikkegt/issues/1

## ゴール

GitHub プロフィール README に Claude Code 使用状況サマリー SVG を表示し、毎日自動更新する。

## アーキテクチャ

```
~/.claude/projects/*.jsonl                 (ローカル transcripts)
        |
        v
scripts/aggregate_ai_usage.py              (Python 集計)
        |
        +--> data/ai-usage.json            (生データ: 公開可)
        +--> images/ai-usage.svg           (可視化 SVG)
        |
        v
scripts/run_daily.sh                       (集計 → git push)
        |
        v
launchd/com.mikkegt.ai-usage.plist         (毎日 03:00 JST)
        |
        v
README.md が ai-usage.svg を参照
```

## ファイル構成

| パス | 役割 |
|------|------|
| `scripts/aggregate_ai_usage.py` | transcripts 集計 + SVG 生成 |
| `scripts/run_daily.sh` | 集計 → commit → push のラッパー |
| `launchd/com.mikkegt.ai-usage.plist` | launchd 定義 (リポジトリ管理) |
| `data/ai-usage.json` | 集計結果 (生成物、コミット対象) |
| `images/ai-usage.svg` | 可視化 SVG (生成物、コミット対象) |
| `plans/001-ai-usage-visualization.md` | 本プラン |

## 集計対象

直近 30 日のセッション (`mtime` で絞る)。

抽出する数値:
- セッション数 (= JSONL ファイル数)
- ツール呼び出し総数
- ツール別 Top 5 (回数)
- スキル別 Top 3 (回数、`Skill` ツールの `input.skill` を集計)
- 日次ツール呼び出し数 (直近 30 日のスパークライン用)

## SVG デザイン

縦 200px × 横 800px 程度の単一 SVG (CSS アニメーション込み):

```
+----------------------------------------------------------+
|  🤖 AI Pair Programming (last 30 days)                   |
|                                                          |
|   123          4,567         8                           |
|   sessions     tool calls    skills used                 |
|                                                          |
|  Top tools:  [Bash ████████ 1234]                        |
|              [Read ██████   980]                         |
|              [Edit ████     412]                         |
|                                                          |
|  Top skills: [shinkoku:journal ███ 42]                   |
|                                                          |
|  Daily activity (sparkline):                             |
|  ▁▂▃▅▇▅▃▂▁▂▃▅▇▅▃▂▁▂▃▅▇▅▃▂▁▂▃▅▇▅                         |
+----------------------------------------------------------+
```

動き要素 (今風):
- 数字を 0 からカウントアップする CSS アニメーション (`@keyframes count`)
- バーが左から伸びるアニメーション
- スパークラインが描画されていくアニメーション (stroke-dasharray)

## launchd 仕様

- Label: `com.mikkegt.ai-usage`
- 実行タイミング: 毎日 03:00 JST
- StandardOutPath / StandardErrorPath: `/tmp/com.mikkegt.ai-usage.{out,err}.log`
- ProgramArguments: `/bin/zsh -lc 'cd <repo> && scripts/run_daily.sh'`

セットアップ手順:
```sh
cp launchd/com.mikkegt.ai-usage.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.mikkegt.ai-usage.plist
```

## プライバシー

- transcripts の本文 (会話・コード) は読み取らない
- 集計値 (ツール名・スキル名・回数・日付) のみ書き出す
- ツール `input` フィールドは Skill 名抽出のみに使い、その他は捨てる

## 実装ステップ

1. Python 集計スクリプト
2. SVG 生成 (同じスクリプト内、外部ライブラリなし)
3. launchd plist
4. ラッパーシェル
5. 一度ローカル実行して JSON / SVG を生成
6. README 更新
7. commit & push

## 改訂履歴

### 2026-06-03 — 可視化を「使い方」寄りに刷新 (pixel_sweets テーマ)

「Claude Code をどう使っているか」をアピールする方向で、本番テーマ pixel_sweets を更新。

- **① 活動リズム (時間帯)**: 日次スパークラインを廃止し、tool 呼び出しを
  JST の時間帯 (0-23) ごとに集計した 24 本の縦バーに変更 (`render_hour_rhythm`)。
  「いつ使うか」が一目で分かる。集計は呼び出し単位の timestamp で 30 日窓フィルタ。
- **③ スキルのカテゴリ集計**: 「Top skills (個別)」を 2 カテゴリのバーに変更。
  - **Custom** (自作): `~/.claude/skills/` に実在するスキル
  - **Plugin**: 名前空間付き (`plugin:skill`、コロンで判定)
  - 判定は Skill ツール (`name:"Skill"`) と**スラッシュコマンド** (`/foo`、
    user メッセージ内 `<command-name>`) の両方を拾う。両者は別イベントなので合算。
  - 組み込みコマンド (`/exit` `/model` 等) は「使い方のアピール」にならないため除外。
- **ヘッドライン**: `SKILLS` = Custom + Plugin の総呼び出し回数 (`command_total`)。
  従来の「ユニークスキル数」から「合算回数」に意味変更。
- **バーアニメ**: GitHub README はスクロール検知できず読込時 1 回再生のため、
  伸びる時間を 1.2s → 2.5s に延長 (`BAR_ANIM_DURATION_S`)。
- 新 CLI 引数 `--skills-dir` (既定 `~/.claude/skills`) で自作スキル一覧を取得。
- dark / cute テーマは従来構成 (Top skills + スパークライン) のまま互換維持。
