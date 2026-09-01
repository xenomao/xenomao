# DigiLab Beauty プロジェクト

一般社団法人デジラボビューティー(美容業界のAI・DX支援団体)のリポジトリ。

## 重要: 機密データの所在

**DB・営業リストは非公開リポジトリ `xenomao/digilab-beauty-data` に移動済み(2026-07-03)。**
このリポジトリ(公開)には機密データを置かないこと。移動済みファイル:

- `db/digilab_beauty.db` / `db/digilab_beauty_db_schema.sql`(営業管理DB)
- `db/esthetic_industry_dd_19companies.csv`(DD対象19社リスト)
- `docs/reports/sales_list_final_report.md`(18社営業リスト・戦略)

詳細は非公開リポジトリの `MOVE_LOG.md` を参照。
※ 本リポジトリの過去のコミット履歴にはファイルが残っている(履歴書き換え未実施)。

## LP(ランディングページ)

- 本体: `marketing/digilab_beauty_lp.html`(単一HTML・画像はbase64埋め込み)
- 配信用コピー: `public/index.html`(内容は同一。更新時は両方を同期すること)
- 公開URL: https://xenomao.github.io/xenomao/
- デプロイ: `main` の `public/` 配下を変更してプッシュすると `.github/workflows/deploy-lp.yml` がGitHub Pagesへ自動デプロイ
- 素材(写真・QRコードSVG): `marketing/assets/`
- QRコード: Instagram(@digilab.beauty_official)と公式LINE(https://lin.ee/O8g2Egp)。生成時は読み取り検証を行うこと

### 検定LP(ビューティAI検定 3級)

- 本体: `marketing/kentei_lp.html` / 配信用コピー: `public/kentei/index.html`(内容は同一。更新時は両方を同期すること)
- 名称は2026-09-01に「美容AIセキュリティ基礎検定 3級」から改称。名称のルールは `docs/strategy/certification_naming_standard.md` が正(表記ゆれ禁止)
- 公開URL: https://xenomao.github.io/xenomao/kentei/
- LP本体(`digilab_beauty_lp.html` / `public/index.html`)のグローバルナビ「検定」からリンク
- デザインは「検定・認定証」らしい権威性を出すため、**ディープネイビー×ゴールド**の専用スタイル(明朝: Shippori Mincho / Noto Serif JP)。パステルラベンダーはサブアクセント。認定エンブレム(シール)はSVGで生成
- OGP画像: `public/kentei/ogp.png`(1200×630・ネイビー×ゴールド・認定シール入り)。`og:image`は絶対URL(https://xenomao.github.io/xenomao/kentei/ogp.png)で指定
- 配信の実体: 現状Pagesは **`gh-pages` ブランチ** から配信されている(Settings→Pages の Source が「Deploy from a branch」)。`public/` を更新したら、`gh-pages` にも反映しないと本番に出ない点に注意

### サロンAI活用度診断

- 配信: `public/shindan/index.html` / 本体: `marketing/salon_ai_shindan.html`(内容は同一。更新時は両方を同期すること)
- 公開URL: https://xenomao.github.io/xenomao/shindan/
- 全10問・約2分のセルフ診断

### 成果物一覧

- 全成果物(公開URL・ガイドライン・ツール・アプリ・販促資料)の棚卸しは `docs/asset_inventory.md` を参照
- KPIダッシュボード(社内用): `tools/kpi_dashboard.html`(+ マニュアル)。公開はしない
- 過去ブランチに散在していた成果物は2026-07-06にmainへ集約済み(アプリは `apps/` 配下)

### 法令・コンプライアンス問題集

- 配信: `public/compliance/index.html`(元はNetlify公開のHTMLをそのまま移設。単一HTML・印刷対応)
- 公開URL: https://xenomao.github.io/xenomao/compliance/
- 内容: 特商法・景表法・薬機法・個人情報保護法・SNS・AIガイドラインの10問+解答解説。**ビューティAI検定 3級の公式練習問題**として位置づけ(旧「AI美容カウンセリング技能資格(ビューティーフェロー3級)」の名称は廃止)


## 認証事業(ビューティAI認証制度)

- 制度の総称は **ビューティAI認証制度**(Beauty AI Certification Standard)。3階層で構成
  - 個人: ビューティAI検定 3級/2級/1級 → ビューティAIフェロー → シニアフェロー → 認定インストラクター
  - 事業所: AIセーフサロン認証(スタンダード/ゴールド)
  - ツール提供者: ビューティAIトラストマーク
- **名称の正は `docs/strategy/certification_naming_standard.md`**。「検定(個人が受ける)/認定(個人に与える上位資格)/認証(事業所・ツールに与える)」を混用しないこと
- 事業設計(価格・収益モデル・ロードマップ): `docs/strategy/digilab_ai_certification_business_design.md`
- 出題・審査基準: `docs/strategy/digilab_certification_curriculum_blueprint.md`
- 競合分析: `docs/strategy/cosme_kentei_business_teardown.md`
- LP掲載の2級・1級の受検料は**理事会承認前の予定額**。承認前に `main` / `gh-pages` へ反映しないこと

## ブランド

- デザイン: 白基調 × パステルラベンダー(概要資料PDF準拠)。ダークパープルの旧配色は使わない
- ロゴ表記: "Digilab beauty"(Poppins系・ワイドトラッキング)
- 連絡先: digilabbeauty@gmail.com

## 組織情報(LP掲載中・2026年7月時点)

- 理事長: 鎌田麻央 / 副理事長: 井上めぐみ / 監事: 岡島紀子 / 法務顧問: 栗原啓太 / 顧問: 森越道大(一般社団法人デジタルサロン協会事務局長)
- 実務部会: AI教育・セミナー(田中裕美・鈴木啓生) / 広報・メディア(新井智也・SAE) / コミュニティ(樋口奈津子・林田真美)
- 賛助会員の料金はLP上では「年会費¥100,000〜」のみ表示(個別プラン金額は非掲載)

## 規約

- ドキュメントは日本語
- ファイル名は snake_case
