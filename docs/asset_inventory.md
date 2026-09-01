# DigiLab Beauty 成果物・URL一覧(アセットインベントリ)

最終更新: 2026-09-01(認証事業ドキュメント `docs/strategy/` を追加 / ビューティAI認証制度へ名称統一)

## A. 公開中ページ(GitHub Pages)

| 名前 | URL | ソース |
|---|---|---|
| メインLP(団体公式) | https://xenomao.github.io/xenomao/ | `public/index.html` |
| ビューティAI検定 3級 LP(制度全体ページ) | https://xenomao.github.io/xenomao/kentei/ | `public/kentei/index.html` |
| ビューティAI検定 3級 公式練習問題(法令・コンプライアンス) | https://xenomao.github.io/xenomao/compliance/ | `public/compliance/index.html` |
| サロンAI活用度診断(全10問) | https://xenomao.github.io/xenomao/shindan/ | `public/shindan/index.html` |
| 賛助会員向けプレゼンデッキ | https://xenomao.github.io/xenomao/sponsor/ | `public/sponsor/index.html`(本体: `marketing/digilab_beauty_sponsor_deck.html`) |
| 鎌田麻央 個人ビジネスLP | https://xenomao.github.io/xenomao/kamata/ | `public/kamata/index.html` |
| プライバシーポリシー | https://xenomao.github.io/xenomao/privacy.html | `public/privacy.html` |
| 検定LP用OGPシェア画像 | https://xenomao.github.io/xenomao/kentei/ogp.png | `public/kentei/ogp.png`(新名称で再生成済) |
| 認定番号の照会(レジストリ) | https://xenomao.github.io/xenomao/kentei/verify/ | `public/kentei/verify/index.html` + `registry.json` |

※ 配信の実体は `gh-pages` ブランチ。`public/` 更新後は `gh-pages` への同期が必要(CLAUDE.md参照)。

## B. 外部サービス

| 名前 | URL | 状態 |
|---|---|---|
| 問題集(旧・Netlify版) | https://sunny-queijadas-b66611.netlify.app/ | `/compliance/` に移設済み。停止推奨 |

## C. ガイドライン・教材(docs/)

| 名前 | ファイル |
|---|---|
| 美容業界AI活用ガイドライン 2026(検定版) | `docs/beauty_ai_guideline_kentei_2026.html` / `.pdf` |
| 美容業界AI活用ガイドライン 2026(パートナー版) | `docs/beauty_ai_guideline_partner_2026.html` / `.pdf` |
| 美容業界AIガイドライン v0.1(骨子) | `docs/beauty_ai_guideline_v0.1.md` |
| ホワイトペーパー「AI時代のエステティシャン」 | `docs/whitepaper_aesthetician_ai_era.md` |
| 5/19セミナー会員募集チラシ | `docs/seminar/0519_member_flyer.html` |
| 名称規程 v1.0(ビューティAI認証制度の正式名称・表記ルール・商標対象) | `docs/strategy/certification_naming_standard.md` |
| 検定事業ティアダウン(日本化粧品検定の構造解体) | `docs/strategy/cosme_kentei_business_teardown.md` |
| 認証事業 事業設計書 v1.0(資格体系・価格・収益モデル・ロードマップ) | `docs/strategy/digilab_ai_certification_business_design.md` |
| 出題・審査ブループリント v1.0(級別出題比率・サロン認証35項目・ベンダー審査) | `docs/strategy/digilab_certification_curriculum_blueprint.md` |
| 運用ガイド(AIエージェント口座/一斉メール/Codex CLI/Lovart/News API/note) | `docs/guides/*.md` |
| レポート(NewsAPI検証/フェーズ1完了) | `docs/reports/*.md` |
| 営業メールテンプレ(Jエステ) | `docs/templates/email_j-esthe_approach.md` |

## D. ツール(tools/)

| 名前 | ファイル | 備考 |
|---|---|---|
| 事業KPIダッシュボード(管理画面) | `tools/kpi_dashboard.html` | データはブラウザlocalStorage保存。社内用・未公開 |
| KPIダッシュボード使い方マニュアル | `tools/kpi_dashboard_manual.html` | 入力担当者向け |

## E. 販促・営業資料(marketing/)

| 名前 | ファイル |
|---|---|
| メインLP本体 | `marketing/digilab_beauty_lp.html` |
| 検定LP本体 | `marketing/kentei_lp.html` |
| 鎌田麻央LP本体 | `marketing/kamata_mao_lp.html` |
| サロンAI活用度診断 本体 | `marketing/salon_ai_shindan.html` |
| チラシ(A4フライヤー) | `marketing/digilab_beauty_flyer.html` |
| ピッチデッキ v3(最新)/ v2 / AX版 | `marketing/pitch_deck_v3.html` ほか |
| ロゴプレビュー集 | `marketing/logo_preview.html` |
| セルフチェックシート | `marketing/digilab_beauty_self_check.html` |
| LPパステル配色案(比較用アーカイブ) | `marketing/digilab_beauty_lp_pastel.html` |
| 会員特典: AIスターターガイド / 会員証カード / ニュースレターvol.1 | `marketing/member_benefits/*.html` |
| 素材(写真・QR・鎌田様写真) | `marketing/assets/` |
| 認証制度ブランド素材(エンブレム3種・認証マーク2種・OGPソース・認定証/認証証書テンプレ) | `marketing/assets/certification/`(+ `README.md`) |

## F. アプリ(apps/)

| 名前 | ディレクトリ | 備考 |
|---|---|---|
| AI活用診断 Webアプリ(Next.js) | `apps/web/` | AI Readiness Check・レーダーチャート。LP基盤含む |
| 会員ポータルWebアプリ | `apps/webapp/` | 会員証・コンテンツ管理・収益画面など14テンプレート |

## G. コンテンツ

| 名前 | 場所 |
|---|---|
| ブログ記事 50本(AIマーケ/グローバル/成分/スタッフ教育 ほか) | `blog/**/*.md` |

## H. Google Drive(リポジトリ外)

| 名前 | 形式 |
|---|---|
| 美容サロン法規コンプライアンスハンドブック v2.0(同名2件) | Word |
| 美肌検定案 | PDF |
| 美容業界向けAI・DX活用セミナー開催履歴 | スプレッドシート |

## 機密データ(非公開リポジトリ)

営業管理DB・DD対象19社リスト・営業リスト最終報告は `xenomao/digilab-beauty-data`(非公開)に移動済み。本リポジトリには置かないこと(詳細: CLAUDE.md)。
