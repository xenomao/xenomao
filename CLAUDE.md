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

**未移動の機密データ(2026-07-30時点)**: ブランチ `claude/beauty-prospect-list-uoqu3j` に営業見込みリスト
(`prospects/output/beauty_prospect_10k.csv` 約3.5MB ほか)が残っている。**mainには取り込まないこと。**
非公開リポジトリへ移すまでブランチのまま保持する。

### 秘密情報(APIキー等)の扱い

- `.env` は**コミット禁止**(`.gitignore` 済み)。雛形は `.env.example` を使う
- APIキー・パスワードをソースにハードコードしない。必ず `os.getenv()` で環境変数から読む
- 2026-07-30に `.env` の追跡解除と `scripts/main.py` / `scripts/test_newsapi_simple.py` の
  ハードコードキー除去を実施。**過去コミットにはキーが残るため、露出したキーは無効化・再発行が必要**

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

### Beauty 2040(未来共創プロジェクト)

- 本体: `marketing/beauty_2040_lp.html` / 配信用コピー: `public/beauty2040/index.html`(内容は同一。更新時は両方を同期すること)
- 公開URL(予定): https://xenomao.github.io/xenomao/beauty2040/ ※ `gh-pages` 未反映のため本番未公開
- 立ち上げキット(TODO・リリース文・100人集客プラン): `docs/projects/beauty_2040/`

### ピュアライン様LP(問い合わせ特化)

- 本体: `marketing/pureline_lp.html` / 配信用コピー: `public/pureline/index.html`(内容は同一。更新時は両方を同期すること)
- 公開URL: https://xenomao.github.io/xenomao/pureline/(`gh-pages` に先行公開済み)
- 批評・再設計の根拠: `docs/reports/pureline_site_critique_and_relaunch.md`

### 成果物一覧

- 全成果物(公開URL・ガイドライン・ツール・アプリ・販促資料)の棚卸しは `docs/asset_inventory.md` を参照
- 未完了事項と次アクション(優先順位付き)は `docs/status/incomplete_items_and_next_actions.md` を参照
- KPIダッシュボード(社内用): `tools/kpi_dashboard.html`(+ マニュアル)。公開はしない
- 過去ブランチに散在していた成果物は2026-07-06と**2026-07-30**の2回、mainへ集約済み(アプリは `apps/` 配下)

### ディレクトリ構成(2026-07-30 整理後)

| ディレクトリ | 中身 |
|---|---|
| `public/` | GitHub Pages 配信物(公開URLの実体) |
| `marketing/` | LP・チラシ・デッキの本体、ロゴ、素材(`assets/`) |
| `docs/guidelines/` | AI活用ガイドライン・広告ガイドライン(HTML/PDF/骨子) |
| `docs/whitepapers/` | ホワイトペーパー |
| `docs/strategy/` | 事業計画・認証制度設計・ポジショニング・想定問答・商標調査 |
| `docs/proposals/` | 他社向け協業提案(タカラベルモント等) |
| `docs/reports/` | 調査・分析レポート(K-Beauty/SEO/セキュリティ等) |
| `docs/projects/` | プロジェクト単位の実行キット(Beauty 2040 等) |
| `docs/guides/` | 運用・ツールの手順書 |
| `docs/ops/` | エージェント運用設計(ループ設計・MCP設定) |
| `docs/seminar/` `docs/templates/` `docs/press/` | セミナー運営資料・テンプレ・プレスリリース |
| `docs/status/` | 進捗・未完了事項の管理 |
| `scripts/` | 収集・配信・チェック用スクリプト |
| `tools/` | 社内向けHTMLツール(非公開) |
| `blog/` `healthtech/` | コンテンツ |
| `apps/` | Webアプリ(`web` = Next.js / `webapp` = Flask) |

### 法令・コンプライアンス問題集

- 配信: `public/compliance/index.html`(元はNetlify公開のHTMLをそのまま移設。単一HTML・印刷対応)
- 公開URL: https://xenomao.github.io/xenomao/compliance/
- 内容: 特商法・景表法・薬機法・個人情報保護法・SNS・AIガイドラインの10問+解答解説。「AI美容カウンセリング技能資格(ビューティーフェロー3級)」に基づく学習用教材

## ループ設計(エージェント運用)

- 設計全体は `docs/ops/loop_design.md` を参照(4パターンの対応表・使い方)
- LP関連(`marketing/` ⇔ `public/` の同期対象)を編集したら、完了報告前に `scripts/check_lp_sync.sh` が終了コード0であることを確認する(`/lp-sync` スキル)
- 公開URLの死活・デプロイ反映確認は `/site-health` スキル(`scripts/check_site_health.sh`)
- 同期対象HTMLの編集時は PostToolUse フックが自動で同期チェックを行う(`.claude/settings.json`)
- MCP連携(GitHub・Playwright ほか)は `.mcp.json` と `docs/ops/mcp_setup.md` を参照

## ブランド

- **方針転換(2026-07-13・鎌田様指示): パステルラベンダー主体・「淡い」路線は廃止方向。**
  「誠実なサロンを育て、証明する認証機関」という立ち位置に合わせ、白地ベースで、はっきりした・権威性のある配色へ移行する
  (戦略資料はディープネイビー×ゴールド系=検定LPの系統で制作)。新規制作物はパステル・淡い色使いを主体にしないこと。
  **既存LP群(メインLP・診断・鎌田様LP等)の改修は未実施**
- (旧・参考)デザイン: 白基調 × パステルラベンダー(概要資料PDF準拠)。ダークパープルの旧配色は使わない
- ロゴ: `marketing/digilab_beauty_logo.svg`
- ロゴ表記: "Digilab beauty"(Poppins系・ワイドトラッキング)
- 連絡先: digilabbeauty@gmail.com

## 組織情報(LP掲載中・2026年7月時点)

- 理事長: 鎌田麻央 / 副理事長: 井上めぐみ / 監事: 岡島紀子 / 法務顧問: 栗原啓太 / 顧問: 森越道大(一般社団法人デジタルサロン協会事務局長)
- 実務部会: AI教育・セミナー(田中裕美・鈴木啓生) / 広報・メディア(新井智也・SAE) / コミュニティ(樋口奈津子・林田真美)
- 賛助会員の料金はLP上では「年会費¥100,000〜」のみ表示(個別プラン金額は非掲載)

## 規約

- ドキュメントは日本語
- ファイル名は snake_case
