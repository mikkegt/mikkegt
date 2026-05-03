# launchd セットアップ

ローカル Mac で AI 使用統計を毎日自動更新するための launchd 設定。

## インストール

```sh
cp launchd/com.mikkegt.ai-usage.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.mikkegt.ai-usage.plist
```

## 動作確認

```sh
# 即時実行
launchctl start com.mikkegt.ai-usage

# ログ確認
tail -f /tmp/com.mikkegt.ai-usage.out.log /tmp/com.mikkegt.ai-usage.err.log

# 状態確認
launchctl list | grep ai-usage
```

## アンインストール

```sh
launchctl unload ~/Library/LaunchAgents/com.mikkegt.ai-usage.plist
rm ~/Library/LaunchAgents/com.mikkegt.ai-usage.plist
```

## メモ

- `StartCalendarInterval` は **ローカル時刻** で解釈される
- マシンがスリープ中で時刻を逃したら次の起動時に走る
- `git push` するので SSH 鍵がエージェントに登録されている必要あり
