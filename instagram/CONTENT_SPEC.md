# Instagram投稿生成・承認仕様

一般社団法人デジラボビュティのInstagram `@digilab.beauty_official` 用です。AIは下書きを作れますが、外部公開は人の承認後に限ります。

## 1投稿のファイル

`instagram/queue/` に同じslugのJSONとJPEGを置きます。

```text
2026-09-03-ai-counseling.json
2026-09-03-ai-counseling.jpg
```

- slug: 半角英小文字・数字・ハイフン。JSONの`slug`とファイル名を一致させる
- 画像: Meta APIが対応するJPEGのみ。8MB以下、幅320〜1440px、比率4:5〜1.91:1
- 推奨: 1080×1080または1080×1350、sRGB、上下左右約100pxのセーフエリア
- 外部URL画像、サブディレクトリ、`../`は不可。承認ハッシュは画像本体も対象
- このリポジトリは公開です。未発表・機密・個人情報を含む素材は保存しない

## JSON（生成時は必ずdraft）

```json
{
  "slug": "2026-09-03-ai-counseling",
  "media_type": "IMAGE",
  "images": ["2026-09-03-ai-counseling.jpg"],
  "caption": "本文",
  "hashtags": ["#美容AI", "#デジラボビュティ"],
  "alt_text": "画像内容の説明",
  "scheduled_for": "2026-09-03T19:00:00+09:00",
  "status": "draft"
}
```

- `media_type`: `IMAGE`（1枚）または`CAROUSEL`（2〜10枚）
- `caption`: ハッシュタグ込み2200文字以内
- `hashtags`: `#`始まり・空白なし・重複なし・最大30個
- `scheduled_for`: 投稿希望日時。`+09:00`などタイムゾーン必須。承認時には必須
- `status`: AI生成時は`draft`。`ready`を手入力しない
- 医療・効果効能の断定、未確認の数値、権利未確認素材、個人情報を入れない

## ブランド表記

- 法人名: `一般社団法人デジラボビュティ`
- Instagram: `@digilab.beauty_official`
- 配色: 白基調×パステルラベンダー
- トーン: 清潔・信頼・先進、美容業界のプロ向け
- CTAは原則1つ（公式LINEまたはプロフィールリンク）

## 人による承認

画像、本文、ハッシュタグ、代替テキスト、予約時刻、権利・法令をプレビューで確認後、次を実行します。

```bash
python instagram/publish.py --approve 2026-09-03-ai-counseling \
  --approved-by "承認者名" \
  --schedule "2026-09-03T19:00:00+09:00"
```

コマンドが`approval.content_sha256`を記録し、`ready`へ変更します。承認後に本文・画像・予約時刻を変えるとハッシュ不一致で投稿が止まり、再承認が必要です。
