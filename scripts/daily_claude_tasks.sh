#!/bin/bash
# DigiLab Beauty - Claude CLI 日次自動実行スクリプト
# 使い方: bash scripts/daily_claude_tasks.sh
# cron設定例: 0 9 * * * cd /home/user/xenomao && bash scripts/daily_claude_tasks.sh >> logs/claude_daily.log 2>&1

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$REPO_DIR/logs"
DATE=$(date '+%Y-%m-%d')
LOGFILE="$LOG_DIR/claude_daily_${DATE}.log"

mkdir -p "$LOG_DIR"

log() {
  echo "[$(date '+%H:%M:%S')] $1" | tee -a "$LOGFILE"
}

run_claude() {
  local task_name="$1"
  local prompt="$2"
  log "▶ タスク開始: $task_name"
  echo "$prompt" | claude -p --add-dir "$REPO_DIR" 2>&1 | tee -a "$LOGFILE"
  log "✅ タスク完了: $task_name"
  echo "" >> "$LOGFILE"
}

# ─────────────────────────────────────────────
log "========================================"
log "DigiLab Beauty 日次タスク開始: $DATE"
log "========================================"

# タスク1: タスクリストの確認と未完了タスクの実行
run_claude "タスクリスト確認" \
"作業ディレクトリ: $REPO_DIR
docs/strategy/seminar_membership_daily_tasks_may19.md を読み込み、
今日($DATE)が期日の[ ]（未完了）タスクを全て確認してください。
実行可能なもの（ファイル生成・文章作成・コード修正）があれば
その場で実行し、完了したタスクを[x]に更新してください。
完了できなかったタスクとその理由も報告してください。"

# タスク2: ブログ記事の品質チェック
run_claude "ブログ記事チェック" \
"作業ディレクトリ: $REPO_DIR
blog/ ディレクトリ内の記事を確認し、以下をチェックしてください:
1. CTAリンク（digilab-beauty.com）が正しく記載されているか
2. 会員登録への誘導文が含まれているか
3. 問題があればその場で修正し、修正内容を報告してください。"

# タスク3: 成果物の生成漏れチェック
run_claude "成果物チェック" \
"作業ディレクトリ: $REPO_DIR
marketing/member_benefits/ を確認し、以下のファイルが存在するか確認してください:
- ai_starter_guide.html
- newsletter_vol1.html
- membership_cards.html
不足があればその場で生成してください。"

# タスク4: Gitコミット
log "▶ タスク開始: 変更のGitコミット"
cd "$REPO_DIR"
if ! git diff --quiet || ! git diff --cached --quiet; then
  git add -A
  git commit -m "Auto: 日次タスク実行 $DATE" || true
  git push origin HEAD || log "⚠ Push失敗（ネットワークエラーの可能性）"
  log "✅ Gitコミット・プッシュ完了"
else
  log "ℹ 変更なし - コミットスキップ"
fi

log "========================================"
log "全タスク完了: $DATE"
log "========================================"
