#!/usr/bin/env bash
# LP同期チェッカー(Verifier)
# marketing/ の本体と public/ の配信用コピーが完全一致しているかを機械判定する。
# 終了コード = 不一致ペア数(0なら全ペア同期済み)。
# ループ設計上の役割: ゴール型ループの「定量的停止条件」。詳細は docs/loop_design.md 参照。

set -u

# 同期ペア定義(本体:配信用コピー)。ペアを増やす場合はここに追記する。
PAIRS=(
  "marketing/digilab_beauty_lp.html:public/index.html"
  "marketing/kentei_lp.html:public/kentei/index.html"
  "marketing/salon_ai_shindan.html:public/shindan/index.html"
)

cd "$(dirname "$0")/.." || exit 99

fail=0
for pair in "${PAIRS[@]}"; do
  src="${pair%%:*}"
  dst="${pair##*:}"
  if [[ ! -f "$src" ]]; then
    echo "NG: $src が存在しません"
    fail=$((fail + 1))
    continue
  fi
  if [[ ! -f "$dst" ]]; then
    echo "NG: $dst が存在しません"
    fail=$((fail + 1))
    continue
  fi
  if diff -q "$src" "$dst" >/dev/null; then
    echo "OK: $src == $dst"
  else
    echo "NG: $src != $dst (内容が不一致。両方を同期すること)"
    fail=$((fail + 1))
  fi
done

if [[ $fail -eq 0 ]]; then
  echo "RESULT: 全 ${#PAIRS[@]} ペア同期済み"
else
  echo "RESULT: ${fail} ペアが不一致"
  echo "NOTE: public/ を更新した場合、gh-pages ブランチにも反映しないと本番に出ない(CLAUDE.md参照)"
fi
exit "$fail"
