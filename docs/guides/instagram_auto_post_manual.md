# Instagram 自動投稿マニュアル

対象アカウント: **@digilab.beauty_official**(一般社団法人デジラボビューティー)
最終更新: 2026-08-06

Instagramへの投稿を自動化する方法を、手軽な順に3段階でまとめます。
まず **方法A** で運用を回し、投稿本数が増えてきたら **方法C** に移行するのが現実的です。

---

## 0. 方法の比較

| | 方法A: Meta Business Suite | 方法B: ノーコードSaaS | 方法C: API + GitHub Actions |
|---|---|---|---|
| 費用 | 無料 | 月0〜数千円 | 無料(GitHub Actions無料枠) |
| 導入時間 | 10分 | 30分 | 2〜3時間(初回のみ) |
| 予約投稿 | ✅ | ✅ | ✅(本リポジトリのスクリプト) |
| 複数人での運用 | ✅ | ✅ | △(Git操作が必要) |
| 他ツールとの連携 | ❌ | ○ | ✅(ブログ更新と連動など) |
| 完全自動化 | ❌(都度手入力) | △ | ✅ |
| 向いている状況 | 週1〜2投稿 | 複数SNS同時運用 | 定型投稿を継続的に量産 |

> **前提(全方法共通)**: Instagramアカウントが **プロアカウント(ビジネス)** であり、
> Facebookページと連携済みであること。個人アカウントでは自動投稿はできません。

---

## 1. 方法A: Meta Business Suite で予約投稿(まずこれ)

追加ツール不要・無料。担当者が複数人でも運用しやすい方法です。

1. https://business.facebook.com/latest/home にアクセスし、
   デジラボビューティーのビジネスアカウントでログイン
2. 左メニュー **「コンテンツ」→「投稿を作成」**
3. 投稿先で **Instagram** を選択(Facebookページ同時投稿も可)
4. 画像・動画をアップロードし、キャプションとハッシュタグを入力
5. 右下 **「予約設定」** を選び、日時(JST)を指定して **「予約する」**
6. **「コンテンツ」→「予約済み」** タブで一覧・編集・取消ができる

**運用のコツ**

- 月初に1か月分をまとめて予約すると、投稿の抜けがなくなります
- 投稿時間の目安は **平日 12:00 / 19:00〜21:00**(サロン関係者の閲覧が多い時間帯)
- 予約できるのは最大75日先まで。月次で予約を積み増す運用にします

---

## 2. 方法B: ノーコードSaaSで自動化

複数SNS(Instagram / X / Facebook / note)を横断運用する場合に有効です。

| ツール | 特徴 | 無料枠 |
|---|---|---|
| Buffer | シンプルな予約投稿。UIが軽い | 3チャンネル・10投稿まで |
| Later | ビジュアルカレンダーで月間計画が立てやすい | 1SNSセットまで |
| Make / Zapier | 「スプレッドシートに書いたら投稿」等の自動化が組める | 月数百タスクまで |

**Make を使った定番の自動化例**

```
Google スプレッドシート(投稿日時・画像URL・本文)
  → Make が5分おきに新規行を検知
  → 予約時刻になったら Instagram モジュールで投稿
  → 投稿URLをスプレッドシートに書き戻す
```

いずれのツールも、初回に **Facebookログインでの権限許可** が必要です(方法Cの Step 1 と同じ前提)。

---

## 3. 方法C: Content Publishing API で完全自動化

本リポジトリに実装済みの構成です。JSONに投稿内容を書いてプッシュすれば、
GitHub Actions が毎時チェックして予約時刻に自動投稿します。

### 構成ファイル

| ファイル | 役割 |
|---|---|
| `scripts/instagram_auto_post.py` | 投稿スクリプト本体 |
| `marketing/instagram/post_queue.json` | 投稿キュー(実データ・自分で作成) |
| `marketing/instagram/post_queue.example.json` | 投稿キューの記入例 |
| `.github/workflows/instagram_auto_post.yml` | 毎時実行するワークフロー |
| `public/instagram/` | 投稿画像・動画の置き場(GitHub Pagesで公開) |

### 処理の流れ

```
post_queue.json(予約時刻・画像URL・キャプション)
  → GitHub Actions(毎時05分)
  → 予約時刻を過ぎた未投稿を抽出
  → POST /{ig-user-id}/media          … メディアコンテナ作成
  → GET  /{container-id}?status_code  … 動画は処理完了まで待機
  → POST /{ig-user-id}/media_publish  … 公開
  → 投稿URLをキューに書き戻してコミット
```

---

### Step 1. アカウントの前提を整える

1. Instagramアプリ → 設定 → **「アカウントの種類とツール」→「プロアカウントに切り替える」**
   → カテゴリは「教育」または「非営利団体」を選択
2. Facebookページ(デジラボビューティー)と連携
   → Instagram設定 →「ページをリンク」
3. https://business.facebook.com/ の **ビジネス設定** で、
   Instagramアカウントとページが同じビジネスポートフォリオに入っていることを確認

### Step 2. Metaアプリを作成する

1. https://developers.facebook.com/apps/ →「アプリを作成」
2. ユースケース: **「Instagramの投稿を管理する」**(Manage Instagram posts)を選択
3. アプリ名: `digilab-beauty-instagram` / 連絡先: digilabbeauty@gmail.com
4. 作成後、アプリ設定でビジネスポートフォリオを紐付ける
5. 必要な権限(アクセス許可)を追加する

| ログイン方式 | 必要な権限 |
|---|---|
| Instagramログイン(推奨・シンプル) | `instagram_business_basic`, `instagram_business_content_publish` |
| Facebookログイン | `instagram_basic`, `instagram_content_publish`, `pages_show_list`, `pages_read_engagement` |

> 開発モードのままでも、アプリの管理者・開発者ロールのアカウントに対しては動作します。
> 自団体のアカウントに投稿するだけなら **アプリ審査(App Review)は不要** です。

### Step 3. Instagram ビジネスアカウントID(IG_USER_ID)を取得する

[グラフAPIエクスプローラ](https://developers.facebook.com/tools/explorer/) で作成したアプリを選び、
アクセストークンを生成してから次を実行します。

```bash
# Facebookログイン方式の場合
curl -s "https://graph.facebook.com/v25.0/me/accounts?access_token=${TOKEN}"
# → ページID(page-id)を取得

curl -s "https://graph.facebook.com/v25.0/${PAGE_ID}?fields=instagram_business_account&access_token=${TOKEN}"
# → instagram_business_account.id が IG_USER_ID(17桁前後の数値)
```

```bash
# Instagramログイン方式の場合
curl -s "https://graph.instagram.com/v25.0/me?fields=id,username&access_token=${TOKEN}"
```

### Step 4. 長期アクセストークンを用意する

短期トークン(1〜2時間)のままでは自動投稿が止まります。次のどちらかにします。

**(推奨)システムユーザートークン — 無期限**

1. ビジネス設定 →「ユーザー」→「システムユーザー」→ 追加(役割: 管理者)
2. 「アセットを割り当て」でアプリ・Facebookページ・Instagramアカウントを割り当て
3. 「新しいトークンを生成」→ アプリと必要な権限を選択 → トークンをコピー
4. 有効期限は **「無期限」** を選択

**(代替)長期ユーザートークン — 60日**

```bash
curl -s "https://graph.facebook.com/v25.0/oauth/access_token\
?grant_type=fb_exchange_token\
&client_id=${APP_ID}\
&client_secret=${APP_SECRET}\
&fb_exchange_token=${SHORT_LIVED_TOKEN}"
```

60日で失効するため、**カレンダーに55日後の更新リマインダーを登録** してください。

トークンの権限と有効期限は次で確認できます。
https://developers.facebook.com/tools/debug/accesstoken/

### Step 5. GitHub Secrets を登録する

リポジトリの **Settings → Secrets and variables → Actions → New repository secret**

| 名前 | 値 |
|---|---|
| `IG_USER_ID` | Step 3 で取得したID |
| `IG_ACCESS_TOKEN` | Step 4 で取得したトークン |

> トークンは絶対にコードやコミットに含めないこと。誤ってコミットした場合は
> Meta側でトークンを失効(再生成)させてから、Secretsを入れ直します。

### Step 6. 画像・動画を公開URLで用意する

Instagram APIは **公開URL経由でしかメディアを取得できません**(ローカルファイル添付は不可)。
本リポジトリでは GitHub Pages をそのまま画像置き場に使います。

1. `public/instagram/` に画像を置く(例: `20260810_kentei.jpg`)
2. `main` にプッシュすると `deploy-lp.yml` が自動デプロイ
3. 公開URLは `https://xenomao.github.io/xenomao/instagram/20260810_kentei.jpg`
4. ブラウザのシークレットウィンドウで開き、**ログインなしで表示できること** を必ず確認

> Googleドライブの共有リンク・Dropbox・期限付き署名URLは失敗しやすいため使わないこと。

### Step 7. 投稿キューを書く

`marketing/instagram/post_queue.example.json` をコピーして
`marketing/instagram/post_queue.json` を作り、投稿内容を追記していきます。

```json
{
  "posts": [
    {
      "id": "20260810_kentei",
      "type": "IMAGE",
      "image_url": "https://xenomao.github.io/xenomao/instagram/20260810_kentei.jpg",
      "caption": "本文…\n\n#美容AI #サロン経営 #digilabbeauty",
      "scheduled_at": "2026-08-10T19:00:00",
      "status": "scheduled"
    }
  ]
}
```

**項目一覧**

| 項目 | 必須 | 内容 |
|---|---|---|
| `id` | ✅ | 一意のID。`YYYYMMDD_内容` の形式を推奨 |
| `type` | ✅ | `IMAGE` / `CAROUSEL` / `REELS` / `STORIES` |
| `image_url` | 画像時 | 公開URL(JPEG) |
| `video_url` | 動画時 | 公開URL(MP4) |
| `children` | カルーセル時 | 2〜10件の `{"image_url": …}` 配列 |
| `caption` | | 本文。2,200文字以内・ハッシュタグ30個以内(ストーリーズは不可) |
| `scheduled_at` | ✅ | 予約時刻。**JST**・`2026-08-10T19:00:00` 形式 |
| `status` | ✅ | 投稿前は `scheduled`。投稿後にスクリプトが `published` へ更新 |
| `cover_url` | | リールのカバー画像URL |
| `share_to_feed` | | リールをフィードにも表示するか(既定: `true`) |
| `location_id` | | 位置情報のFacebookページID |

投稿後は、スクリプトが `published_at` / `media_id` / `permalink` を自動で書き戻します。

### Step 8. テスト投稿で動作確認する

```bash
pip install requests

export IG_USER_ID="17841400000000000"
export IG_ACCESS_TOKEN="EAAG..."

# 1) 対象の確認だけ(投稿されない)
python scripts/instagram_auto_post.py --dry-run

# 2) 1件だけ即時投稿してみる
python scripts/instagram_auto_post.py --post-id 20260810_kentei

# 3) 予約時刻を過ぎたものをまとめて投稿
python scripts/instagram_auto_post.py
```

最初は必ず **テスト用の画像1枚** で `--post-id` を試し、
実際にInstagramへ表示されること・キャプションの改行が崩れていないことを確認します。

### Step 9. 自動実行を有効にする

`.github/workflows/instagram_auto_post.yml` が **毎時05分** にキューを確認します。

- 手動実行: リポジトリの **Actions →「Instagram 自動投稿」→ Run workflow**
  (`dry_run` にチェックを入れると確認のみ)
- 投稿結果は Actions のログと、キューへの自動コミットで追跡できます
- 一時停止したいときは Actions 画面から該当ワークフローを **Disable**

> スケジュール実行はGitHub側の負荷で数分〜十数分遅れることがあります。
> 「19:00ちょうど」が重要な投稿は方法Aで予約してください。

---

## 4. メディア仕様と制限(2026年8月時点)

| 項目 | 制限 |
|---|---|
| API経由の投稿数 | **1アカウントあたり24時間で50件**(ストーリーズを除く) |
| 画像形式 | JPEG(PNGは不可の場合あり)・8MB以下 |
| 画像サイズ | 幅320〜1440px / アスペクト比 4:5〜1.91:1 |
| カルーセル | 2〜10枚 |
| リール | MP4・MOV / 1GB以下 / 3秒〜15分 / 9:16推奨 |
| ストーリーズ | 画像、または60秒以内の動画。キャプション不可 |
| キャプション | 2,200文字以内 / ハッシュタグ30個以内 / @メンション20個以内 |
| メディアコンテナ | 作成から24時間で失効 |

投稿枠の残数はスクリプトが実行時に確認しますが、手動でも取得できます。

```bash
curl -s "https://graph.facebook.com/v25.0/${IG_USER_ID}/content_publishing_limit\
?fields=config,quota_usage&access_token=${IG_ACCESS_TOKEN}"
```

**APIではできないこと**

- API自体に予約投稿機能はない(本スクリプトのようにスケジューラを自前で持つ)
- 個人アカウントへの投稿
- 投稿後のキャプション編集(削除して再投稿するしかない)
- 他人の投稿のリポスト、ハッシュタグ検索の自動収集

---

## 5. 投稿前チェックリスト

自動化しても、**内容の責任は投稿者にあります**。キューへ追加する前に確認してください。

- [ ] 薬機法: 「痩せる」「シミが消える」など効能を断定する表現がないか
- [ ] 景表法: 「No.1」「最安」等の根拠のない優良誤認・有利誤認表現がないか
- [ ] 個人情報: 会員・受講者の顔写真や氏名の掲載許諾を得ているか
- [ ] 著作権: 画像・音源が商用利用可能なものか(生成AI画像は生成元の規約を確認)
- [ ] リンク: プロフィールのリンク先が最新か(キャプション内のURLはタップできない)
- [ ] 表記: 団体名は「一般社団法人デジラボビューティー」、ロゴ表記は "Digilab beauty"
- [ ] ハッシュタグ: 固定タグ `#digilabbeauty` を含めているか
- [ ] 予約時刻が **JST** で正しいか(UTCと取り違えていないか)

---

## 6. トラブルシューティング

| 症状・エラー | 原因と対処 |
|---|---|
| `code=190` | トークン失効。Step 4 で再取得し、Secretsを更新 |
| `code=200` / 権限エラー | 権限不足。`instagram_content_publish` が付与されているかトークンデバッガで確認 |
| `code=9004` / `2207050` | 画像URLをInstagramが取得できない。公開URLか・サイズ超過でないかを確認 |
| `code=2207026` | 動画形式が非対応。MP4(H.264 + AAC)に変換する |
| `code=36003` 相当のアスペクト比エラー | 画像比率が 4:5〜1.91:1 の範囲外。トリミングする |
| `(#4) Application request limit reached` | 24時間の投稿上限(50件)またはAPI呼び出し上限。時間を置いて再実行 |
| コンテナが `EXPIRED` | 作成から24時間放置された。再実行すれば新しいコンテナが作られる |
| Actionsは成功なのに投稿されない | `status` が `scheduled` 以外、または `scheduled_at` が未来のまま |
| 改行が反映されない | JSON内では `\n` で改行を表現する(実際の改行は入れない) |

失敗した投稿は `status` が `error` になり、`error` フィールドに原因が記録されます。
原因を直したら `status` を `scheduled` に戻せば、次回の実行で再試行されます。

---

## 7. 保守作業

| 頻度 | 作業 |
|---|---|
| 55日ごと | 長期ユーザートークンの更新(システムユーザートークンなら不要) |
| 四半期ごと | Graph APIのバージョン確認。現在 `v25.0`(2026年2月リリース) |
| 随時 | 各バージョンはリリースから約2年でサポート終了。[変更履歴](https://developers.facebook.com/docs/graph-api/changelog)を確認し、ワークフローの `GRAPH_API_VERSION` を更新 |
| 月次 | 投稿キューの古い `published` エントリを整理 |

---

## 参考リンク

- [Instagram Platform - Content Publishing](https://developers.facebook.com/docs/instagram-platform/content-publishing)
- [Graph API 変更履歴](https://developers.facebook.com/docs/graph-api/changelog)
- [アクセストークンデバッガ](https://developers.facebook.com/tools/debug/accesstoken/)
- [Meta Business Suite](https://business.facebook.com/latest/home)
