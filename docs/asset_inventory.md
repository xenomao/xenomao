# DigiLab Beauty 成果物・URL一覧(アセットインベントリ)

最終更新: 2026-07-30(未マージ39ブランチ・gh-pages・オープンPRの全棚卸しに基づく再編)

> **完成済み成果物の所在**は本ファイル。**未完了事項と次アクション**は
> `docs/status/incomplete_items_and_next_actions.md` を参照。

## A. 公開ページ(GitHub Pages)

| 名前 | URL | ソース | 本番反映 |
|---|---|---|---|
| メインLP(団体公式) | https://xenomao.github.io/xenomao/ | `public/index.html` | △ 旧版が配信中 |
| 美容AIセキュリティ基礎検定3級 LP | https://xenomao.github.io/xenomao/kentei/ | `public/kentei/index.html` | ○ |
| 法令・コンプライアンス問題集 | https://xenomao.github.io/xenomao/compliance/ | `public/compliance/index.html` | ○ |
| サロンAI活用度診断(全10問) | https://xenomao.github.io/xenomao/shindan/ | `public/shindan/index.html` | ○ |
| 鎌田麻央 個人ビジネスLP | https://xenomao.github.io/xenomao/kamata/ | `public/kamata/index.html` | ○ |
| プライバシーポリシー | https://xenomao.github.io/xenomao/privacy.html | `public/privacy.html` | ○ |
| 検定LP用OGPシェア画像 | https://xenomao.github.io/xenomao/kentei/ogp.png | `public/kentei/ogp.png` | ○ |
| ピュアライン様LP(問い合わせ特化) | https://xenomao.github.io/xenomao/pureline/ | `public/pureline/index.html` | ○ |
| 賛助会員向けプレゼンデッキ | https://xenomao.github.io/xenomao/sponsor/ | `public/sponsor/index.html` | **× 404(未デプロイ)** |
| Beauty 2040(未来共創プロジェクト) | https://xenomao.github.io/xenomao/beauty2040/ | `public/beauty2040/index.html` | **× 未デプロイ** |
| Beauty TIMES LP | https://xenomao.github.io/xenomao/beauty_times/ | PR #13(未マージ) | **× 未デプロイ** |

※ 配信の実体は `gh-pages` ブランチ。`public/` 更新後は `gh-pages` への同期が必要(CLAUDE.md参照)。
配信方式の一本化が未決のため反映漏れが発生している(未完了事項の 2. を参照)。
死活確認は `bash scripts/check_site_health.sh`、本体⇔配信コピーの同期確認は `bash scripts/check_lp_sync.sh`。

## B. 外部サービス

| 名前 | URL | 状態 |
|---|---|---|
| 問題集(旧・Netlify版) | https://sunny-queijadas-b66611.netlify.app/ | `/compliance/` に移設済み。**停止手続き未実施** |

## C. ガイドライン(docs/guidelines/)

| 名前 | ファイル |
|---|---|
| 美容業界AI活用ガイドライン 2026(検定版) | `beauty_ai_guideline_kentei_2026.html` / `.pdf` |
| 美容業界AI活用ガイドライン 2026(パートナー版) | `beauty_ai_guideline_partner_2026.html` / `.pdf` |
| 美容業界AIガイドライン v0.1(骨子) | `beauty_ai_guideline_v0.1.md` |
| エステティック広告ガイドライン 改定追補(消費者契約法・割賦販売法・特定電子メール法) | `esthetic_ad_guideline_amendment.pdf` / `.html` |

## D. ホワイトペーパー(docs/whitepapers/)

| 名前 | ファイル |
|---|---|
| AI時代のエステティシャン | `whitepaper_aesthetician_ai_era.md` |
| AI時代だからこそ輝く人 vol.1(フォーマル版) | `whitepaper_ai_era_vol1.html` / `.pdf` |

## E. 戦略・制度設計(docs/strategy/)

| 名前 | ファイル |
|---|---|
| 事業計画書 | `business_plan_digilab_beauty.md` |
| ビジネスモデル | `business_model.md` |
| 戦略ポジショニング1枚 | `positioning_one_pager.html` |
| デジラボ認証(仮称)審査基準 第1次草案 | `certification_criteria_draft.html` |
| 理事会向け説明メモ(制度全体図・審議事項) | `board_briefing_memo.html` |
| 化粧品×薬機法講座 企画書 | `course_cosmetics_yakkiho_plan.html` |
| 宣言用セルフチェックシート | `self_check_declaration_sheet.html` |
| 想定問答集(独自性・スケーラビリティ・社会インパクト・実現可能性) | `pitch_qa_answers.md` |
| 商標予備調査メモ(デジラボ/Digilab/ビューティーフェロー) | `trademark_preliminary_search_memo.md` |
| 5/19セミナー 会員獲得デイリータスク(実施済み・記録) | `seminar_membership_daily_tasks_may19.md` |

## F. 協業提案(docs/proposals/)

| 名前 | ファイル |
|---|---|
| タカラベルモント エステ事業部 協業プラン提案書 | `takarabelmont_esthe_synergy_proposal.html` / `.pdf` / `.md` |
| 同 提案A/B/C A4片面一枚もの | `takarabelmont_onepager_abc.html` / `.pdf` |
| タカラベルモント向け AI活用ガイドライン Do/Don't詳細版 | `beauty_ai_guideline_takarabelmont_dodont.md` |

## G. 調査・分析レポート(docs/reports/)

| 名前 | ファイル |
|---|---|
| K-Beauty国家戦略 徹底分析 | `kbeauty_national_strategy_analysis.md` |
| J-Beauty世界展開戦略 政府向け提言書 | `jbeauty_global_strategy_proposal.md` |
| 成長戦略 2026-2030 | `growth_strategy_2026_2030.md` |
| デジタルビューティー戦略白書 2 | `digital_beauty_strategy_whitepaper2.md` |
| フェーズ1 実行計画 / 完了レポート | `phase1_execution_plan.md` / `phase1_completion_report.md` |
| ピュアライン サイト批評・再設計 | `pureline_site_critique_and_relaunch.md` |
| SEO診断(digilab beauty) | `seo_diagnosis_digilab_beauty.md` |
| 指標データ整合性レポート | `metrics_data_integrity_report.md` |
| シークレット是正レポート | `security_remediation_secrets.md` |
| NewsAPI検証レポート | `newsapi_verification_report.md` |

## H. プロジェクト実行キット(docs/projects/)

| 名前 | ファイル |
|---|---|
| Beauty 2040 立ち上げTODO(全16タスク・未着手) | `beauty_2040/todo_launch.md` |
| Beauty 2040 リリース記事 | `beauty_2040/press_release.md` |
| Beauty 2040 100人集客プラン | `beauty_2040/recruit_100_plan.md` |

## I. 運用・手順(docs/guides/ · docs/ops/ · docs/seminar/ · docs/templates/ · docs/press/)

| 名前 | ファイル |
|---|---|
| 運用ガイド(AIエージェント口座 / 一斉メール / Codex CLI / Lovart / News API / note / Kimi K3 / LINEステップ配信 / Claude 4.8ワークフロー / Search Console) | `docs/guides/*.md` |
| エージェント ループ設計 / MCP設定 | `docs/ops/loop_design.md` / `docs/ops/mcp_setup.md` |
| 5/19セミナー運営一式(マスター戦略・進行台本・チェックリスト・登壇構成・フォローメール) | `docs/seminar/0519_*.md` / `0519_member_flyer.html` |
| テンプレ(セミナークロージング / フォローメール / 入会フォーム / 営業1枚 / Jエステ アプローチ) | `docs/templates/*.md` |
| 設立プレスリリース(**ドラフト・未配信**) | `docs/press/press_release_establishment_2026.md` |

## J. ツール(tools/)

| 名前 | ファイル | 備考 |
|---|---|---|
| 事業KPIダッシュボード(管理画面) | `tools/kpi_dashboard.html` | データはブラウザlocalStorage保存。社内用・未公開 |
| KPIダッシュボード使い方マニュアル | `tools/kpi_dashboard_manual.html` | 入力担当者向け |

## K. 販促・営業資料(marketing/)

| 名前 | ファイル |
|---|---|
| メインLP本体 | `digilab_beauty_lp.html` |
| 検定LP本体 | `kentei_lp.html` |
| 鎌田麻央LP本体 | `kamata_mao_lp.html` |
| サロンAI活用度診断 本体 | `salon_ai_shindan.html` |
| 賛助会員向けプレゼンデッキ本体 | `digilab_beauty_sponsor_deck.html` / `.pdf` |
| Beauty 2040 LP本体 | `beauty_2040_lp.html` |
| ピュアライン様LP本体 | `pureline_lp.html` |
| エクソソーム測定 クリニック配布用1枚もの(薬機法配慮版) | `exosome_measurement_clinic_flyer.html` |
| チラシ(A4フライヤー) | `digilab_beauty_flyer.html` |
| ピッチデッキ v3(最新)/ v2 / AX版 | `pitch_deck_v3.html` ほか |
| ロゴ(SVG)/ ロゴプレビュー集 | `digilab_beauty_logo.svg` / `logo_preview.html` |
| セルフチェックシート | `digilab_beauty_self_check.html` |
| 診断リリースキット | `shindan_release_kit.md` |
| LPパステル配色案(比較用アーカイブ) | `digilab_beauty_lp_pastel.html` |
| 会員特典: AIスターターガイド / 会員証カード / ニュースレターvol.1 | `member_benefits/*.html` |
| SEO用 robots.txt / sitemap.xml | `web/` |
| 素材(写真・QR・鎌田様写真) | `assets/` |

## L. スクリプト(scripts/)

| 名前 | ファイル | 用途 |
|---|---|---|
| LP同期チェッカー | `check_lp_sync.sh` | `marketing/` ⇔ `public/` の全7ペアを機械判定(終了コード=不一致数) |
| サイト死活チェッカー | `check_site_health.sh` | 公開URLのHTTPステータスとデプロイ反映確認 |
| LP同期ガードフック | `hook_lp_sync_guard.sh` | 編集時にPostToolUseで自動チェック |
| 日次ニュース収集 | `daily_news_collection.py` | ヘルステック日次更新用(**現在停止中**) |
| LINEステップ配信 | `line_harness.py` / `line_webhook.py` / `step_line.py` | 公式LINE配信 |
| AI活用度アセスメント | `ai_assessment.py` | 診断ロジック |
| DB初期化 / 統合スクリプト / NewsAPIテスト | `init_database.py` / `main.py` / `test_newsapi_simple.py` | ※APIキーは環境変数から読む |

## M. アプリ(apps/)

| 名前 | ディレクトリ | 備考 |
|---|---|---|
| AI活用診断 Webアプリ(Next.js) | `apps/web/` | AI Readiness Check・レーダーチャート。LP基盤含む |
| 会員ポータルWebアプリ(Flask) | `apps/webapp/` | 会員証・コンテンツ管理・収益画面など14テンプレート |

## N. コンテンツ

| 名前 | 場所 |
|---|---|
| ブログ記事 50本(AIマーケ/グローバル/成分/スタッフ教育 ほか) | `blog/**/*.md` |
| ヘルステック・リサーチ(ニュース・起業リサーチ) | `healthtech/` ※日次更新は2026-07-08で停止中 |

## O. Google Drive(リポジトリ外)

| 名前 | 形式 |
|---|---|
| 美容サロン法規コンプライアンスハンドブック v2.0(同名2件) | Word |
| 美肌検定案 | PDF |
| 美容業界向けAI・DX活用セミナー開催履歴 | スプレッドシート |

## 機密データ(公開リポジトリに置かないもの)

- **移動済み**: 営業管理DB・DD対象19社リスト・営業リスト最終報告 → `xenomao/digilab-beauty-data`(非公開)
- **未移動**: 営業見込みリスト約1万件(ブランチ `claude/beauty-prospect-list-uoqu3j` に残置)、
  定款 docx(ブランチ `claude/happy-keller-LuUeR` に残置)。いずれも非公開リポジトリへ移すこと
- `.env` はコミット禁止。雛形は `.env.example`
