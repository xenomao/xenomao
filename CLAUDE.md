# DigiLab Beauty プロジェクト

一般社団法人デジラボビューティ(美容業界のAI・DX支援団体)のリポジトリ。

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

### 検定LP(美容AIセキュリティ基礎検定 3級)

- 本体: `marketing/kentei_lp.html` / 配信用コピー: `public/kentei/index.html`(内容は同一。更新時は両方を同期すること)
- 公開URL: https://xenomao.github.io/xenomao/kentei/
- LP本体(`digilab_beauty_lp.html` / `public/index.html`)のグローバルナビ「検定」からリンク
- デザインは「検定・認定証」らしい権威性を出すため、**ディープネイビー×ゴールド**の専用スタイル(明朝: Shippori Mincho / Noto Serif JP)。パステルラベンダーはサブアクセント。認定エンブレム(シール)はSVGで生成
- OGP画像: `public/kentei/ogp.png`(1200×630・ネイビー×ゴールド・認定シール入り)。`og:image`は絶対URL(https://xenomao.github.io/xenomao/kentei/ogp.png)で指定
- 配信の実体: 現状Pagesは **`gh-pages` ブランチ** から配信されている(Settings→Pages の Source が「Deploy from a branch」)。`public/` を更新したら、`gh-pages` にも反映しないと本番に出ない点に注意

### サロンAI活用度診断

- 配信: `public/shindan/index.html` / 本体: `marketing/salon_ai_shindan.html`(内容は同一。更新時は両方を同期すること)
- 公開URL: https://xenomao.github.io/xenomao/shindan/
- 全10問・約2分のセルフ診断

### サロン・セルフチェック(経営6軸)

- 配信: `public/selfcheck/index.html` / 本体: `marketing/digilab_beauty_self_check.html`(内容は同一。更新時は両方を同期すること)
- 公開URL: https://xenomao.github.io/xenomao/selfcheck/
- 全18問・約1分。DQSをもとに集客／リピート／単価・指名／時間・運営／発信・口コミ／数字・経営の6軸で自己評価を整理する
- AI活用度診断(`/shindan/`)とは別物。あちらはAI活用レベル、こちらは経営全般の現在地
- 結果画面のCTAは新規向けの「友だち追加」型。既存の公式LINE友だちへ配信する際は、配信文側で「結果のスクショを送ってください」と案内すること

### 成果物一覧

- 全成果物(公開URL・ガイドライン・ツール・アプリ・販促資料)の棚卸しは `docs/asset_inventory.md` を参照
- KPIダッシュボード(社内用): `tools/kpi_dashboard.html`(+ マニュアル)。公開はしない
- AI駆動オペレーション組織図(社内用): `tools/digilab_ai_org_chart.html`。**公開はしない**(`noindex` 指定・運用詳細を含む)。人間2職位＋AIエージェント8体の運営設計と、AIに委任しない4領域(検定・認証の合否判定/個人情報/監事の監査/3法・利益相反の最終判断)を定義。体制変更のたびに更新すること
- Phase 1 運用手順書(社内用): `tools/ai_ops_phase1_manual.html`。**公開はしない**(`noindex`)。教材AI(A1)＋監督AI(A7)のプロンプト雛形・差し戻しルール・入力禁止情報・記録表・2週間後の判断基準
- 過去ブランチに散在していた成果物は2026-07-06にmainへ集約済み(アプリは `apps/` 配下)

### 美容AI用語集(AI活用で押さえる基本用語)

- 本体: `marketing/ai_glossary.html` / 配信用コピー: `public/glossary/index.html`(内容は同一。更新時は両方を同期すること)
- 公開URL: https://xenomao.github.io/xenomao/glossary/
- LP本体のグローバルナビ「用語集」からリンク
- 内容: メタデータ / エンベディング / ベクトル / RAG の4語を、美容サロンの実務に置き換えて定義。各語に「定義・サロンでの意味・使いどころ・よくある誤解」を持たせ、末尾に薬機法/景表法/個人情報保護法の観点と理解度チェックを付す
- **定義の正本はこのページ**。schema.org の `DefinedTermSet` / `DefinedTerm` で構造化し、`public/llms.txt` の "Defined terms" にも同じ定義を記載する。用語を追加・改訂したら、HTMLのJSON-LDとllms.txtの両方を必ず更新すること(片方だけの更新はAIに矛盾した定義を渡すことになる)
- 配色は白基調×パステルラベンダー、見出しは Shippori Mincho B1 × Cormorant Garamond。装飾絵文字は使わない

### AI活用ガバナンス方針(公開)

- 本体: `marketing/digilab_ai_governance.html` / 配信用コピー: `public/governance/index.html`(内容は同一。更新時は両方を同期すること)
- 公開URL: https://xenomao.github.io/xenomao/governance/
- LP本体のグローバルナビ「AI方針」からリンク
- 内容: 意思決定の構造 / **AIに委任しない4領域** / AIを活用する領域 / 成果物の確認プロセス / 現在の運用段階 / 適用範囲と改定
- **景表法上の注意**: 「AI駆動で運営中」といった実績表示はしない。現に運用している範囲を「現在の運用段階」として明記し、予定は予定と書き分けること。実態が先に変わった場合のみ記載を更新する
- 社内用の `tools/digilab_ai_org_chart.html` と**「AIに委任しない4領域」の記載を一致させること**(片方だけ改定しない)
- 改定時は本文の改定日・版数、および `public/llms.txt` の "AI governance" セクションも更新する

### 動画撮影前チェックリスト

- 本体: `marketing/video_checklist.html`。**現状は法務顧問確認前のドラフトのため未公開**（`noindex` 指定）。確認後に `public/video-checklist/index.html` として配信する
- 用途: 美容サロンが撮影を始める前にスマホで確認する。動画は公開後の部分修正ができないため、確認点を「公開前」ではなく**「撮影前」**に置いている(他の教材と設計が異なる)
- 構成: 全23項目・6群。A 撮る内容(薬機法4) / B ビフォーアフター(景表法・打消し表示5) / C 体験談・口コミ(ステマ規制4) / D 映る人(個人情報・肖像権5) / E 音源・素材(著作権2) / F AIを使う場合3。末尾に公開前の最終確認3点と判定
- 各項目にA1〜F3の番号を付与。法務確認や現場での指摘を項目単位で行えるようにするため、**番号は改訂時も可能な限り維持する**(項目追加は群の末尾へ)
- 配布用PDF: `marketing/video_checklist.pdf`(A4・3ページ)。HTMLから生成。**ブランドの明朝フォントを反映した最終版が必要な場合は、ブラウザでHTMLを開いて印刷→PDF保存すること**(生成環境ではWebフォントを取得できずゴシックにフォールバックする)
- **ステマ規制の責任主体はサロン(広告主)**。依頼を受けた投稿者は規制対象外。この点をC群の注記で明示している(出典: 消費者庁)
- チェック状態は保存しない(1撮影ごとに使う想定)。印刷対応

### 法令・コンプライアンス問題集

- 配信: `public/compliance/index.html`(元はNetlify公開のHTMLをそのまま移設。単一HTML・印刷対応)
- 公開URL: https://xenomao.github.io/xenomao/compliance/
- 内容: 特商法・景表法・薬機法・個人情報保護法・SNS・AIガイドラインの10問+解答解説。「AI美容カウンセリング技能資格(ビューティーフェロー3級)」に基づく学習用教材

## ブランド

- デザイン: 白基調 × パステルラベンダー(概要資料PDF準拠)。ダークパープルの旧配色は使わない
- ロゴ表記: "Digilab beauty"(Poppins系・ワイドトラッキング)
- 法人名の正式表記: **`一般社団法人デジラボビューティ`**(末尾に長音「ー」を付けない)。誤記の `デジラボビュティ`(「ビュー」の長音欠落)・旧表記の `デジラボビューティー` は使わない
- 連絡先: digilabbeauty@gmail.com

## 組織情報(LP掲載中・2026年7月時点)

- 理事長: 鎌田麻央 / 副理事長: 井上めぐみ / 監事: 岡島紀子 / 法務顧問: 栗原啓太 / 顧問: 森越道大(一般社団法人デジタルサロン協会事務局長)
- 実務部会: AI教育・セミナー(田中裕美・鈴木啓生) / 広報・メディア(新井智也・SAE) / コミュニティ(樋口奈津子・林田真美)
- 賛助会員の料金はLP上では「年会費¥100,000〜」のみ表示(個別プラン金額は非掲載)

## 規約

- ドキュメントは日本語
- ファイル名は snake_case
- **団体名の正式表記は「一般社団法人デジラボビューティ」**(末尾に長音「ー」を付けない / 「デジラボビュティ」は誤記)。公開ページ・JSON-LD・llms.txt では表記を必ず統一する
