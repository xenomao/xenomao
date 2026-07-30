#!/usr/bin/env bash
# 公開サイト死活監視(Verifier)
# GitHub Pages 上の公開URLがすべて HTTP 200 を返すかを機械判定する。
# 終了コード = 到達不能URL数(0なら全URL正常)。
# あわせてローカル public/ の内容と本番配信内容の一致も確認し、
# 「mainは更新したが gh-pages 未反映」の検知を行う(こちらは警告のみで終了コードに含めない)。
# ループ設計上の役割: タイム型ループ(/loop や Routine)の監視対象。詳細は docs/ops/loop_design.md 参照。

set -u

BASE="https://xenomao.github.io/xenomao"

# 監視URL(パス:対応するローカル配信ファイル。ローカル対応がないものは「-」)
TARGETS=(
  "/:public/index.html"
  "/kentei/:public/kentei/index.html"
  "/shindan/:public/shindan/index.html"
  "/compliance/:public/compliance/index.html"
  "/sponsor/:public/sponsor/index.html"
  "/kamata/:public/kamata/index.html"
  "/pureline/:public/pureline/index.html"
  "/beauty2040/:public/beauty2040/index.html"
  "/privacy.html:public/privacy.html"
  "/kentei/ogp.png:-"
)

cd "$(dirname "$0")/.." || exit 99

fail=0
warn=0
for target in "${TARGETS[@]}"; do
  path="${target%%:*}"
  local_file="${target##*:}"
  url="${BASE}${path}"

  status=$(curl -sS -o /tmp/site_health_body -w "%{http_code}" --max-time 20 "$url" 2>/dev/null)
  if [[ "$status" != "200" ]]; then
    if [[ -z "$status" || "$status" == "000" ]]; then
      echo "NG: $url -> 接続失敗(ネットワーク制限のある環境ではプロキシ拒否の可能性あり)"
    else
      echo "NG: $url -> HTTP $status"
    fi
    fail=$((fail + 1))
    continue
  fi
  echo "OK: $url -> 200"

  if [[ "$local_file" != "-" && -f "$local_file" ]]; then
    live_hash=$(sha256sum /tmp/site_health_body | cut -d' ' -f1)
    local_hash=$(sha256sum "$local_file" | cut -d' ' -f1)
    if [[ "$live_hash" != "$local_hash" ]]; then
      echo "WARN: $url の本番内容がローカル $local_file と不一致(gh-pages 未反映の可能性)"
      warn=$((warn + 1))
    fi
  fi
done

echo "RESULT: 到達不能 ${fail} 件 / 内容不一致警告 ${warn} 件"
exit "$fail"
