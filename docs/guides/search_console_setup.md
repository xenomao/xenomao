# Google Search Console 登録手順（tiiny.site のLPをそのまま使う場合）

対象LP: `https://blue-augustina-26.tiiny.site`
※ digilab-beauty.com へ移行せず、現状のtiiny.site URLのまま登録する手順です。

---

## 前提と注意（重要）

- Search Console への登録・所有権確認は **あなたのGoogleアカウントでの操作が必須** です（Claudeが代行できない部分）。
- tiiny.site の **サブドメインはDNSを操作できない** ため、「ドメイン」プロパティは使えません。
  → **「URLプレフィックス」プロパティ + 「HTMLタグ」確認** を使います（下記手順）。
- ⚠️ tiiny.site の無料サイトは **クローラー(bot)に403を返す挙動** が確認されています。
  この場合、所有権確認やインデックス登録が **失敗・遅延する可能性** があります。
  確認が通らない／インデックスされない場合は、tiiny.siteの有料プラン（カスタムドメイン・bot許可）か
  独自ドメイン `digilab-beauty.com` への移行が必要になります。

---

## 手順

### STEP 1. Search Console でプロパティを追加
1. https://search.google.com/search-console/ にGoogleアカウントでログイン。
2. 左上「プロパティを追加」→ **「URLプレフィックス」** を選択。
3. `https://blue-augustina-26.tiiny.site/` を入力して「続行」。

### STEP 2. 確認コードを取得
1. 確認方法の一覧から **「HTMLタグ」** を選ぶ。
2. 表示される
   `<meta name="google-site-verification" content="◯◯◯◯◯..." />`
   の **content の値（◯◯◯の部分）** をコピー。

### STEP 3. LPに確認タグを埋め込んで再アップロード
1. デプロイしているHTMLファイル（リポジトリでは
   `marketing/digilab_beauty_flyer.html` または `marketing/web/index.html`）の
   `<head>` 内にある以下の枠を編集:
   ```html
   <!-- ▼▼▼ Google Search Console 所有権確認タグ ▼▼▼ ... -->
   <meta name="google-site-verification" content="XXXX...">
   ```
2. `XXXX...` を STEP 2 でコピーした値に置き換え、**前後のコメント記号（`<!--` `-->`）を外す**。
3. 編集したHTMLを **tiiny.site に再アップロード（差し替え）** する。
4. ブラウザで `https://blue-augustina-26.tiiny.site` を開き、ソース表示（Ctrl+U）で
   `google-site-verification` のタグが入っていることを確認。

### STEP 4. 所有権を確認
1. Search Console の画面に戻り「確認」ボタンを押す。
2. 成功すれば所有権確認完了。
   - 失敗する場合 → tiiny.siteのbot 403が原因の可能性大。STEP「前提と注意」を参照。

### STEP 5. インデックス登録をリクエスト（ここが検索に出すための肝）
1. Search Console 上部の検索窓に `https://blue-augustina-26.tiiny.site/` を入力 →「URL検査」。
2. 「インデックス登録をリクエスト」をクリック。
3. 数日〜2週間ほどで反映。`site:blue-augustina-26.tiiny.site` で確認。

---

## 完了チェックリスト
- [ ] URLプレフィックスでプロパティ追加
- [ ] HTMLタグの確認コードをLPに貼って再アップロード
- [ ] 所有権確認OK
- [ ] URL検査でインデックス登録をリクエスト
- [ ] 1〜2週間後に `site:blue-augustina-26.tiiny.site` でインデックス確認
