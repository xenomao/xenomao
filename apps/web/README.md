# DigiLab Beauty — LP（Next.js）

DigiLab Beauty のランディングページ群。`docs/HANDOFF_to_ClaudeCode.md` の仕様にもとづき、
デモHTML（`docs/reference/`）を Next.js に移植したもの。

- **Stack**: Next.js 16（App Router）/ React 19 / TypeScript / Tailwind CSS v4
- **デプロイ想定**: Vercel（リポジトリの **Root Directory を `web/`** に設定）

---

## デザイン原則（厳守 / HANDOFF準拠）

- 下地は **必ず白**（`color-scheme: light only`）。ダーク背景は使わない。
- グラデは「**青 → 紫 → ピンク**」の波動。**ブラック × ゴールドは永久禁止**。
- 装飾は淡いパステルの blur 円（低opacity）。人物写真・ストック画像は使わない（権利クリアのSVGのみ）。
- フォント: 見出し `Cormorant Garamond` / 和文 `Shippori Mincho`（Google Fonts を `<head>` で読込）。
- カラートークンは `src/app/globals.css` の `:root` に定義。

---

## ディレクトリ構成

```
web/
├─ src/
│  ├─ app/
│  │  ├─ layout.tsx        # フォント読込・メタデータ・aurora背景・.wrap（全ページ共通）
│  │  ├─ globals.css       # デザイントークン + デモCSSの移植（白基調・波動）
│  │  └─ page.tsx          # メインLP（/）: Hero + Tabs + footer
│  ├─ components/
│  │  ├─ Hero.tsx          # 共通ヒーロー（「美質の波動」SVG）
│  │  ├─ Tabs.tsx          # ['use client'] サロン/企業 切替（両ペイン保持）
│  │  ├─ SalonPane.tsx     # サロン・個人面（診断 + セミナー予告 + LINE動線）
│  │  ├─ Quiz.tsx          # ['use client'] 自己診断（6軸・レーダーチャート・112点換算）
│  │  ├─ BizPane.tsx       # 企業・団体面（112点フレーム + 3レベル + 資料請求）
│  │  └─ LineButton.tsx    # 公式LINE 大ボタン（緑・env駆動）
│  └─ lib/
│     ├─ links.ts          # 外部URL（LINE/Instagram/Stripe/問い合わせ）の環境変数管理
│     └─ quiz.ts           # 診断データ（QUIZ/RANKS/WEAK/AXES）と純粋ロジック
├─ docs/
│  ├─ HANDOFF_to_ClaudeCode.md   # 元の引き継ぎ指示書（仕様の正）
│  └─ reference/                  # 移植元デモHTML・現状PDFのテキスト
└─ .env.example           # 環境変数テンプレート
```

---

## セットアップ・開発

```bash
cd web
npm install
cp .env.example .env.local   # 各URLを設定
npm run dev                  # http://localhost:3000
```

### 本番ビルド

```bash
npm run build
npm start
```

---

## 環境変数（`.env.local`）

すべてクライアントから参照するため `NEXT_PUBLIC_` プレフィックス。未設定時は `"#"` にフォールバック。

| 変数 | 用途 |
|---|---|
| `NEXT_PUBLIC_LINE_URL` | 公式LINE 友だち追加URL |
| `NEXT_PUBLIC_INSTAGRAM_URL` | Instagram プロフィールURL |
| `NEXT_PUBLIC_STRIPE_CHECKOUT_URL` | Stripe Checkout（月額サブスク）※決済は最終フェーズ |
| `NEXT_PUBLIC_BUSINESS_CONTACT_URL` | 企業向け 資料請求・問い合わせ |

---

## 自己診断（Quiz）の設計

- 悩み起点の **6軸**: `[集客, リピート, 単価・指名, 時間・運営, 発信・口コミ, 数字・経営]`
- 立場（サロン経営者 / 個人セラピスト）別に各6問。**112点換算スコア + 6軸レーダー + 最弱軸の自動検出**。
- 最弱軸 → 経営ベネフィット言語 + 連動セミナーを提示（「AI」という語は前面に出さない）。
- **状態は useState のみ・localStorage不使用**。計算はクライアント内で完結し、**サーバー送信なし**（個情法配慮）。

---

## 実装状況 / 次フェーズ

### ✅ 本セッション（土台 + LP骨組み）
- Next.js 16 + TS + Tailwind の土台構築
- デザインシステム（白基調・波動・指定フォント）移植
- メインLP（`/`）: ヒーロー / サロン・企業タブ / 自己診断（レーダー付き）
- 外部URLの環境変数化

### ⏭ 次フェーズ（HANDOFFの優先順位）
1. **★最重要**: `/business` — 企業向け資料を **DigiLab AI Code of Practice（10原則）** を核とする
   規範性のある構成へ作り替え（現状の企業面はデモ準拠の軽量版）。
2. `/line`（2階層目・LINE友だち追加ページ）/ `/welcome`（決済後サンクス）の移植。
3. **Stripe決済**（月額1,000円サブスク）— 最終フェーズ。`NEXT_PUBLIC_STRIPE_CHECKOUT_URL` を起点に。

---

## 法務メモ（ローンチ前に要対応）

- 本LPはデモ（たたき台）。掲載表現は **法務監修前**。
- セミナー仮タイトルの「予約が埋まる」「自動集客」等は **景表法の優良誤認リスク** → 「学ぶ内容」基準へ要調整。
- ローンチ前に **薬機法・景表法・特商法・個情法** の最終確認（実弁護士監修）が必須。
