#!/bin/bash
# DigiLab Beauty - 単発タスク実行スクリプト
# 使い方:
#   bash scripts/run_task.sh "ブログ記事を1本生成してください"
#   bash scripts/run_task.sh --file scripts/prompts/generate_blog.txt

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$REPO_DIR/logs"
mkdir -p "$LOG_DIR"

LOGFILE="$LOG_DIR/task_$(date '+%Y%m%d_%H%M%S').log"

if [[ "${1:-}" == "--file" && -n "${2:-}" ]]; then
  PROMPT=$(cat "$2")
else
  PROMPT="${1:-}"
fi

if [[ -z "$PROMPT" ]]; then
  echo "使い方: $0 \"プロンプト文\" または $0 --file プロンプトファイル.txt"
  exit 1
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] タスク実行: ${PROMPT:0:60}..." | tee "$LOGFILE"
echo "---" >> "$LOGFILE"

echo "$PROMPT" | claude -p --add-dir "$REPO_DIR" 2>&1 | tee -a "$LOGFILE"

echo "---" >> "$LOGFILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 完了. ログ: $LOGFILE" | tee -a "$LOGFILE"
