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
