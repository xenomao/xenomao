# PR #14 マージ・本番移行チェックリスト

## マージ前（必須）

- [ ] GitHub Actions `Check Instagram automation` が成功
- [ ] Netlify Deploy Previewのルートと`/instagram/`がHTTP 200で表示
- [ ] `/instagram/`に検証エラーが出ていない
- [ ] 法人名が`一般社団法人デジラボビューティ`、投稿先が`@digilab.beauty_official`
- [ ] 画像仕様がJPEG（PNG不可）、8MB以下、幅320〜1440px、比率4:5〜1.91:1
- [ ] 公開リポジトリに機密・未発表情報・個人情報を置かない運用で合意
- [ ] 追跡済みのルート`.env`に実秘密がないことを責任者が確認。実秘密があればマージ前に失効・再発行し、履歴対策を別途実施
- [ ] mainの最新変更とのマージ結果を確認

## Meta・GitHub設定（実投稿前）

- [ ] Instagramプロアカウントと正しいFacebookページのリンクを確認
- [ ] MetaアプリのLive状態、App Review、Business Verification、必要権限を確認
- [ ] `IG_USER_ID`と`IG_ACCESS_TOKEN`をActions Secretsへ登録
- [ ] `IG_EXPECTED_USERNAME=digilab.beauty_official`をActions Variableへ登録
- [ ] `IG_GRAPH_API_VERSION=v26.0`をActions Variableへ登録
- [ ] トークンの失効日・更新責任者・更新手順を記録
- [ ] Actions手動実行`preflight`が想定ユーザー名で成功

## 段階ロールアウト

1. [ ] `IG_PUBLISH_ENABLED=false`のままマージ
2. [ ] サンプルではない実投稿1件を`draft`で作成し、プレビュー確認
3. [ ] 人が`--approve`を実行し、承認者・予約時刻・内容ハッシュを確認
4. [ ] Actionsの`dry-run`で対象が1件だけであることを確認
5. [ ] `IG_PUBLISH_ENABLED=true`へ変更
6. [ ] Actions手動実行で`mode=publish`、確認欄`PUBLISH`として初回1件を投稿
7. [ ] Instagram表示、画像、本文、ハッシュタグ、投稿時刻、media ID、`posted/`移動を確認
8. [ ] 問題がなければ約15分間隔の自動運用を継続

## 障害時

- [ ] `publishing`の投稿を自動で`ready`に戻さない
- [ ] Instagram上に投稿済みか人が確認
- [ ] 投稿済みなら`--recover ... --result posted --media-id ...`
- [ ] 未投稿なら`--recover ... --result retry`後、再確認・再承認
- [ ] Metaトークン、権限、Graph API変更、画像URLのHTTPS公開を確認
