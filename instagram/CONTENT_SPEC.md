# FABLE5 向け 投稿生成スペック(Instagram)

このドキュメントは、**FABLE5 が Instagram 投稿用の画像とキャプションを生成する際に従うルール**です。
FABLE5 は生成物を `instagram/queue/` に次の2ファイルとして保存します(同一 `slug`)。

```
instagram/queue/<slug>.png     ← 投稿画像
instagram/queue/<slug>.json    ← 投稿スペック(下記スキーマ)
```

パブリッシャ(`instagram/publish.py`)がこのキューを読み、条件を満たす投稿を Instagram へ自動投稿します。

---

## 1. slug(ファイル名)の付け方

- 形式: `YYYY-MM-DD-短い英語ラベル`(例: `2026-08-10-ai-counseling`)
- 使用可能文字: 半角英小文字・数字・ハイフンのみ(snake でなく kebab)
- `.json` と `.png` の slug は**必ず一致**させること

---

## 2. 画像仕様

| 項目 | 指定 |
| --- | --- |
| サイズ | 正方形 **1080 × 1080 px**(推奨)/ 縦長 1080 × 1350 px も可 |
| 形式 | PNG(または JPG)・sRGB |
| 文字量 | 画像内テキストは**見出し+一言**程度に抑える(可読性重視) |
| セーフエリア | 上下左右に約 100px の余白を確保(UIで隠れないように) |

### ブランドガイド(必守)

- 配色: **白基調 × パステルラベンダー**。ダークパープルの旧配色は使わない
- ロゴ表記: **"Digilab beauty"**(Poppins系・ワイドトラッキング)
- トーン: 清潔・信頼・先進。美容業界のプロ向け
- 連絡先を載せる場合: `digilabbeauty@gmail.com` / 公式LINE / Instagram `@digilab.beauty_official`
- 医療・効果効能の断定表現は避ける(薬機法・景表法に配慮)

---

## 3. 投稿スペック JSON スキーマ

```json
{
  "slug":          "2026-08-10-ai-counseling",
  "media_type":    "IMAGE",
  "images":        ["2026-08-10-ai-counseling.png"],
  "caption":       "本文(1行目がフックになるように)…",
  "hashtags":      ["#美容AI", "#エステサロン"],
  "alt_text":      "画像の内容を説明する代替テキスト",
  "scheduled_for": "2026-08-10T10:00:00+09:00",
  "status":        "ready"
}
```

| フィールド | 必須 | 説明 |
| --- | --- | --- |
| `slug` | ✔ | ファイル名と一致 |
| `media_type` | – | `IMAGE`(1枚・既定)または `CAROUSEL`(2〜10枚) |
| `images` | ✔ | `queue/` 相対のファイル名。カルーセルは順番どおりに列挙 |
| `caption` | ✔ | 本文。最大 2200 文字(ハッシュタグ込み)。1行目で内容が伝わるように |
| `hashtags` | – | `#` 始まり・**最大30個**。本文の後ろに自動連結される |
| `alt_text` | – | アクセシビリティ用の代替テキスト(推奨) |
| `scheduled_for` | – | ISO8601(**タイムゾーン付き**)。この時刻以降に投稿。`null`/未指定なら即時対象 |
| `status` | – | `draft`(下書き・投稿しない)/ `ready`(投稿可)/ `posted`(投稿済み)。**生成直後は `draft` 推奨**、確認後に `ready` へ |

### キャプション作法
- 1行目 = フック(結論・ベネフィット)
- 改行で読みやすく。過度な絵文字は避ける
- CTA(プロフィールのリンク / 公式LINE)を1つ入れる
- ハッシュタグは本文に混ぜず `hashtags` 配列へ

---

## 4. 生成後の流れ

1. FABLE5 が `<slug>.png` と `<slug>.json`(`status: "draft"`)を `instagram/queue/` に保存
2. 担当者が内容を確認し、`status` を `"ready"` に変更(必要なら `scheduled_for` を設定)
3. Git に commit / push
4. GitHub Actions(スケジュール or 手動)が `publish.py` を実行し、条件を満たす投稿を自動投稿
5. 投稿成功したファイルは `instagram/posted/` へ自動移動

> ローカル確認: `python instagram/publish.py --validate`(検証)/ `--dry-run`(投稿せず対象表示)
