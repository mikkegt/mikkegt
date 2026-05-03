# mikkegt プロフィールリポジトリ

## このリポジトリは何

GitHub の **profile README 専用リポジトリ** (`mikkegt/mikkegt`)。
`README.md` が https://github.com/mikkegt のトップに表示される。

## 自動更新が 2 系統ある

両方とも毎日 03:00 JST に走り、それぞれ別のファイルを更新して main に push する。
触るときは **どちらも push してくる前提**で動くこと。

| 系統 | 何をする | どこで動く | 更新ファイル |
|------|----------|-----------|-------------|
| GitHub Actions | 3D 貢献グラフ生成 | `.github/workflows/profile-3d.yml` (ubuntu-latest) | `profile-3d-contrib/*.svg` |
| launchd (ローカル Mac) | Claude Code 使用統計 SVG 生成 | `launchd/com.mikkegt.ai-usage.plist` (~/Library/LaunchAgents/ にコピー済み) | `images/ai-usage.svg`, `images/ai-usage-cute.svg`, `data/ai-usage.json` |

launchd ログ: `/tmp/com.mikkegt.ai-usage.{out,err}.log`
launchd 状態確認: `launchctl list | grep ai-usage`

## push 前に必ず pull

main 直 push 運用 + 上記の自動コミットがあるので、**ローカルからの push が rejected されることが日常的にある**。
- まず `git pull --ff-only origin main` を試す
- 進めなければ `git merge --no-ff origin/main -m "merge: ..."` で取り込む
- **`git rebase` と `git push --force` は禁止** (グローバル `git.md` ルール)

## ローカル検証

```sh
# どちらのテーマも単体で生成できる
python3 scripts/aggregate_ai_usage.py \
  --projects-dir ~/.claude/projects \
  --json-out data/ai-usage.json \
  --svg-out images/ai-usage.svg \
  --days 30 --theme dark   # or --theme cute
```

レイアウトを変えたら `python3 -c "import xml.etree.ElementTree as ET; ET.parse('images/ai-usage.svg')"` で XML 妥当性確認。

## テーマを追加するとき

`scripts/aggregate_ai_usage.py` の `THEMES` dict に新テンプレートを足すだけ。
既存テンプレートで使っている placeholder (`{sessions}` `{top_tools_svg}` `{sparkline}` 等) を維持する。
`run_daily.sh` も新テーマぶん 1 ブロック追加。

**注意**: cute テーマには `Nyan1-Go` / `Nyan2-Go` という名前が出てくる。これは**ユーザーの実猫の名前**なので、勝手に変えない。

## 設計ドキュメント

- `plans/001-ai-usage-visualization.md` — AI 使用可視化機能の設計と決定事項

## 過去に検討して見送った話

- **OSS としての一般配布**: 設定の外出し・ドキュメント整備の手間に見合わないと判断 (2026-05)。再提案不要。
