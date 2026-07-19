#!/usr/bin/env bash
# LP同期ガード(プロアクティブ型フック)
# Claude Code の PostToolUse フックとして動作する(.claude/settings.json で登録)。
# Edit/Write で marketing/ または public/ の同期対象HTMLが変更された直後に
# check_lp_sync.sh を実行し、不一致があればエージェントに警告を返す(exit 2)。
# 対象外ファイルの編集では何もしない(exit 0)。

set -u

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty' 2>/dev/null)

[[ -z "$file_path" ]] && exit 0

# 同期対象ファイルのみ反応する
case "$file_path" in
  */marketing/digilab_beauty_lp.html | */public/index.html | \
  */marketing/kentei_lp.html | */public/kentei/index.html | \
  */marketing/salon_ai_shindan.html | */public/shindan/index.html) ;;
  *) exit 0 ;;
esac

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
result=$("$script_dir/check_lp_sync.sh" 2>&1)
code=$?

if [[ $code -ne 0 ]]; then
  {
    echo "【LP同期ガード】同期対象ファイルが編集されましたが、本体と配信用コピーが不一致です。"
    echo "$result"
    echo "対応: もう一方のファイルにも同じ変更を反映し、scripts/check_lp_sync.sh が 0 で終了することを確認してください。"
  } >&2
  exit 2
fi
exit 0
