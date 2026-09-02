# Instagram安全投稿ワークフロー

一般社団法人デジラボビューティの公式Instagram `@digilab.beauty_official` へ、人が承認した予約投稿だけを送る仕組みです。

## 安全設計

1. AI・担当者は`draft`として画像とJSONを作成
2. Netlify Deploy Previewの`/instagram/`で人が確認
3. `--approve`が本文・画像・予約時刻のSHA-256を記録して`ready`化
4. GitHub Actionsが約15分ごとに期限到来分を`publishing`として先にコミット
5. Meta APIで投稿し、成功時だけ`posted/`へ移動してmedia IDを記録

先に`publishing`を保存するため、投稿成功後にGitHubへの記録が失敗しても次回の自動実行は同じ投稿を再送しません。停止投稿はInstagram上の実在を確認してから手動復旧します。

## ローカル確認

```bash
python -m unittest discover -s instagram/tests -v
python instagram/publish.py --validate
python instagram/publish.py --dry-run
python instagram/build_preview.py --output /tmp/instagram-preview/index.html
```

## 承認

```bash
python instagram/publish.py --approve <slug> \
  --approved-by "承認者名" \
  --schedule "2026-09-03T19:00:00+09:00"
git add instagram/queue && git commit && git push
```

`status: ready`の手入力は禁止です。ハッシュがなければ検証で停止します。

## GitHub設定

Actions Secrets:

- `IG_USER_ID`
- `IG_ACCESS_TOKEN`

Actions Variables:

- `IG_EXPECTED_USERNAME=digilab.beauty_official`
- `IG_GRAPH_API_VERSION=v26.0`
- `IG_PUBLISH_ENABLED=false`（初期値。ロールアウト完了後だけ`true`）
- `IG_IMAGE_BASE_URL`（通常は不要。未設定時は実行対象コミットのraw URL）

手動実行の既定は`dry-run`です。`publish`を選んでも、mainブランチ・`IG_PUBLISH_ENABLED=true`・確認欄の`PUBLISH`が揃わない限り実投稿しません。`preflight`は投稿せず、トークンが想定アカウントを指すか確認します。

## Meta設定

この実装はInstagram API with Facebook Loginを前提とします。

- InstagramプロアカウントとFacebookページを正しくリンク
- Metaアプリを本番利用できる状態にし、必要なApp Review・Business Verificationを完了
- 少なくとも`instagram_basic`と`instagram_content_publish`を付与。ページ・IG user ID取得フローで必要なページ権限も確認
- トークンの有効期限と失効時の更新責任者を決める
- `preflight`結果が必ず`@digilab.beauty_official`になることを確認
- Graph APIバージョンは定期的に更新。現在の既定はv26.0

固定の投稿上限値には依存せず、Meta管理画面・`content_publishing_limit`で実アカウントの利用状況を確認してください。

## 予約精度

ワークフローは毎時7/22/37/52分に起動します。`scheduled_for`は「この時刻以降の最初の正常実行で投稿」の意味で、GitHub ActionsやMeta側の遅延により時刻ぴったりは保証されません。

## 停止投稿の復旧

`status=publishing`は自動再送しません。先にInstagramを確認します。

```bash
# すでにInstagramへ出ていた場合
python instagram/publish.py --recover <slug> --result posted --media-id <MEDIA_ID>

# 出ていないことを確認し、内容確認からやり直す場合
python instagram/publish.py --recover <slug> --result retry
```

`retry`は`draft`へ戻し承認を消すため、再承認が必須です。
