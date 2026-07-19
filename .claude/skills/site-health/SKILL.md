---
name: site-health
description: DigiLab Beauty の公開サイト(GitHub Pages)の死活とデプロイ反映状況を確認する。単発チェックのほか、/loop や Routine と組み合わせたタイム型の定期監視の1回分として使う。判定は scripts/check_site_health.sh の終了コードで行う。
---

# 公開サイト死活監視(タイム型ループの1回分)

公開URL(LP・検定LP・診断・コンプラ問題集・OGP画像)がすべて生きているか、
本番配信内容がローカル public/ と一致しているかを機械判定する。

## 手順

1. `bash scripts/check_site_health.sh` を実行する。
2. 結果を読み、次のとおり対応する:
   - **終了コード 0 かつ WARN なし**: 「全URL正常」とだけ簡潔に報告して終了。定期実行中なら余計な作業はしない。
   - **WARN あり(内容不一致)**: mainの `public/` は更新済みだが gh-pages 未反映の可能性が高い。どのURLが不一致かを報告し、gh-pages への反映が必要である旨を伝える(勝手に gh-pages へプッシュしない。ユーザーの指示を待つ)。
   - **NG あり(HTTP 200以外)**: 対象URLと HTTPステータスを報告する。`.github/workflows/deploy-lp.yml` の直近の実行結果と Settings→Pages の設定確認を提案する。

## 定期監視として使う場合

- ローカルPC稼働中のみでよい場合: `/loop 30m /site-health`
- PCを閉じても回したい場合(クラウドRoutine): docs/loop_design.md の「タイム型」の節にある Routine 設定手順に従う。

いずれの場合も、正常時は報告のみで停止(次回実行を待つ)。異常時のみ上記の対応を行う。
