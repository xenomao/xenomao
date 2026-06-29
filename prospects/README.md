# prospects/ ― 賛助会員 営業リスト構築キット

デジラボビューティの賛助会員獲得に向けた、美容業界×IT/AI 営業リスト（目標1万件）を
**合法かつ実用的に**構築するためのツール一式です。

## なぜ「自動生成1万件」を同梱しないのか

会社名・住所・電話番号・メールアドレスは**実在する情報**です。AIがこれらを「生成」すると
架空データになり、(1) 営業に使えない (2) 偶然実在する第三者へ営業が飛ぶ恐れ
(3) 特定電子メール法・個人情報保護法の観点で問題、という三重のリスクがあります。

そこでこのキットは「**実データを集めるための仕組み**」を提供します。
既存の `db/esthetic_industry_dd_19companies.csv`（手作業で検証済みの実在19社）と同じ
品質を、1万件までスケールさせるのが目的です。

## 構成

```
prospects/
├── README.md                       … このファイル
├── segmentation_plan.md            … 1万件のセグメント別内訳と推奨データ源
├── templates/
│   └── prospect_list_template.csv  … 営業リストの項目設計（Excel可）
├── scripts/
│   ├── fetch_houjin_bangou.py      … 国税庁 法人番号DBから実在企業を抽出
│   └── requirements.txt
└── output/                         … 生成物の出力先
```

## クイックスタート

### 1. ベースとなる実在企業（会社名・住所）を集める

```bash
cd prospects/scripts
pip install -r requirements.txt

# 都道府県別CSVを https://www.houjin-bangou.nta.go.jp/download/ から取得後:
python fetch_houjin_bangou.py bulk \
    --input 13_tokyo_all.csv \
    --output ../output/beauty_tokyo.csv \
    --limit 10000
```

→ 会社名・住所・法人番号が**実データ**で出力されます。
   （電話・メール・担当部署は空欄。次の工程で補完）

### 2. 連絡先をエンリッチする

`segmentation_plan.md` の「推奨データ源」に従い、各社の
電話番号・問い合わせ窓口・担当部署を補完します。
店舗系は Google Places、BtoB は展示会出展者一覧・許諾済み企業DBが有効。

### 3. オプトイン・重複排除・品質チェック

テンプレートの `オプトイン状況` / `法人番号` 列で送信可否と重複を管理し、
サンプリングで到達性を確認してから営業投入します。

## コンプライアンス

詳細は `segmentation_plan.md` の「法令・コンプライアンス チェックリスト」を参照。
広告メールは原則オプトイン、個人情報は適正取得・利用目的明示が必須です。
