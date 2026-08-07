# Instagram 画像生成 → 自動投稿の仕組み

FABLE5 が生成した画像とキャプションを **キューに置くだけで、Instagram(@digilab.beauty_official)へ自動投稿**する仕組みです。

```
 ┌──────────┐   画像+JSONを生成      ┌──────────────┐   status=ready のみ    ┌───────────┐
 │  FABLE5  │ ───────────────────▶ │ instagram/queue/ │ ────────────────────▶ │ publish.py │ ──▶ Instagram
 └──────────┘  CONTENT_SPEC.md 準拠  └──────────────┘   予約時刻を過ぎたもの   └───────────┘        Graph API
                                              ▲                                       │
                                     担当者が status を ready に            投稿成功 → instagram/posted/ へ移動
```

- **役割分担**: FABLE5 = コンテンツ生成 / このリポジトリ = 投稿自動化
- **画像ホスティング**: 追加サービス不要。GitHub の raw URL をそのまま Instagram Graph API に渡す
- **依存**: 標準ライブラリのみ(Python 3.9+)

---

## ディレクトリ構成

```
instagram/
├── README.md              このファイル
├── CONTENT_SPEC.md        FABLE5 への生成ルール(画像仕様・JSONスキーマ)
├── publish.py             パブリッシャ本体(CLI)
├── igpost/                ライブラリ
│   ├── post.py            投稿スペックの読込・検証・整形
│   └── igclient.py        Instagram Graph API クライアント
├── queue/                 投稿待ち(FABLE5 がここに置く)
│   └── example-*.json     サンプル(status=draft・投稿されない)
├── posted/                投稿済みアーカイブ(自動移動)
├── requirements.txt
└── config.example.env     環境変数サンプル
```

---

## 1. 初回セットアップ(Meta 側・一度だけ)

Instagram のフィード自動投稿には Meta の **Graph API** を使います。以下が必要です。

1. Instagram を**プロアカウント**(ビジネス/クリエイター)にする
2. Facebook ページと連携する
3. [Meta for Developers](https://developers.facebook.com/) でアプリを作成し、
   **Instagram Graph API** を追加、`instagram_basic` と `instagram_content_publish` 権限を取得
4. 次の2つを取得する:
   - **IG_USER_ID**: Instagram プロアカウントの user id(数値)
   - **IG_ACCESS_TOKEN**: 長期アクセストークン(約60日で失効するため定期更新)

> 詳細手順は Meta 公式の "Content Publishing" ガイドを参照してください。

### GitHub Secrets に登録

リポジトリの **Settings → Secrets and variables → Actions** で登録:

| Secret 名 | 値 |
| --- | --- |
| `IG_USER_ID` | Instagram user id |
| `IG_ACCESS_TOKEN` | 長期アクセストークン |
| `IG_IMAGE_BASE_URL` | (任意)画像公開URLベース。未設定なら raw URL を自動生成 |

---

## 2. 日々の運用フロー

1. **FABLE5 に生成を指示**(`CONTENT_SPEC.md` に従う)
   - `instagram/queue/<slug>.png` と `instagram/queue/<slug>.json` が作られる
   - 生成直後は `status: "draft"` 推奨
2. **確認して公開許可**
   - JSON を確認し、`status` を `"ready"` に変更(必要なら `scheduled_for` を設定)
3. **commit / push**
4. **自動投稿**
   - GitHub Actions が **毎日 JST 10:00 / 19:00** に実行(手動実行も可)
   - `status=ready` かつ `scheduled_for` を過ぎた投稿だけが対象
   - 投稿成功したファイルは `instagram/posted/` へ自動移動しコミット

---

## 3. ローカルでの確認

```bash
# スペックの検証のみ(APIを呼ばない)
python instagram/publish.py --validate

# 投稿せず対象と最終キャプションを表示(ドライラン)
python instagram/publish.py --dry-run

# 実際に投稿(要 環境変数)
cp instagram/config.example.env instagram/.env   # 値を設定
export $(grep -v '^#' instagram/.env | xargs)
python instagram/publish.py
```

---

## 4. 手動実行(GitHub Actions)

**Actions → "Publish Instagram queue" → Run workflow** から実行できます。
`dry_run` を `true` にすると投稿せず対象確認のみ行います。

---

## 投稿スペック(最小例)

```json
{
  "slug": "2026-08-10-ai-counseling",
  "images": ["2026-08-10-ai-counseling.png"],
  "caption": "AIカウンセリングで、接客はもっと“あなたらしく”。",
  "hashtags": ["#美容AI", "#エステサロン", "#digilabbeauty"],
  "status": "ready"
}
```

スキーマの全項目は [`CONTENT_SPEC.md`](./CONTENT_SPEC.md) を参照。

---

## 注意事項

- **画像は公開リポジトリの raw URL 経由で Instagram に取得**されます。非公開にしたい素材は置かないこと
- アクセストークンは**期限切れ**に注意(失効すると投稿が 400 で失敗)。定期的に更新を
- Instagram の仕様上限: キャプション 2200 文字 / ハッシュタグ 30 個 / カルーセル 10 枚(パブリッシャが検証)
- Graph API のコンテンツ公開は**1日あたりの投稿数上限**があります(通常25件/24時間)
