#!/bin/bash
# DigiLab Beauty - cron自動実行のセットアップスクリプト
# 実行方法: bash scripts/setup_cron.sh
# ※ このスクリプトはcronが使えるサーバー・PCで実行してください

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CLAUDE_PATH="$(which claude)"

if [[ -z "$CLAUDE_PATH" ]]; then
  echo "❌ claudeコマンドが見つかりません。Claude Code CLIをインストールしてください。"
  echo "   インストール: npm install -g @anthropic-ai/claude-code"
  exit 1
fi

echo "✅ claude CLI: $CLAUDE_PATH"
echo "✅ リポジトリ: $REPO_DIR"
echo ""
echo "以下のcronジョブを登録します:"
echo "  毎朝9時  - 日次タスク自動実行"
echo "  毎週月曜 - 週次レポート生成"
echo ""

read -p "登録しますか？ [y/N]: " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
  echo "キャンセルしました。"
  exit 0
fi

# 現在のcrontabを退避
TMPFILE=$(mktemp)
crontab -l 2>/dev/null > "$TMPFILE" || true

# 重複チェック
if grep -q "digilab_beauty\|daily_claude_tasks" "$TMPFILE" 2>/dev/null; then
  echo "⚠ すでにDigiLab Beautyのcronジョブが登録されています。スキップします。"
  cat "$TMPFILE"
  rm "$TMPFILE"
  exit 0
fi

# cronジョブを追記
cat >> "$TMPFILE" << EOF

# ── DigiLab Beauty 自動タスク ──────────────────────────────
# 毎朝9時: 日次タスク実行（タスクリスト確認・成果物生成・Git push）
0 9 * * * cd $REPO_DIR && bash scripts/daily_claude_tasks.sh >> logs/cron.log 2>&1

# 毎週月曜12時: 週次レポートと翌週タスク確認
0 12 * * 1 cd $REPO_DIR && echo "今週の進捗をdocs/strategy/seminar_membership_daily_tasks_may19.md から確認し、翌週分のタスクで未着手のものを優先度順に整理してください" | $CLAUDE_PATH -p --add-dir $REPO_DIR >> logs/cron.log 2>&1
# ─────────────────────────────────────────────────────────────
EOF

crontab "$TMPFILE"
rm "$TMPFILE"

echo ""
echo "✅ cron登録完了！"
echo ""
crontab -l | grep -A 10 "DigiLab Beauty"
