# 未完了事項と次アクション(優先順位付き)

最終更新: 2026-07-30
作成根拠: main / gh-pages / 未マージ39ブランチ / オープンPR の全棚卸し

> このファイルは「**何が終わっていないか**」と「**次に何をやるか**」の一次ソース。
> 完成済み成果物の一覧は `docs/asset_inventory.md` を参照。

---

## 0. サマリー

| 区分 | 件数 | 状態 |
|---|---|---|
| 完成済みだが未集約だった成果物 | 約40ファイル | **本コミットでmainへ集約完了** |
| 本番サイトに未反映の公開物 | 3件(賛助デッキ/Beauty 2040/メインLP更新) | **未対応・要デプロイ** |
| 露出した秘密情報 | APIキー1件 | **コード側は対処済み・キー無効化は未実施** |
| 停止している自動運用 | ヘルステック日次更新 | **22日間停止中** |
| 意思決定待ち(理事長判断) | 5件 | 未決 |
| 未マージのオープンPR | 2件(#13, #1) | 未処理 |

---

## 1. 【最優先・即日】セキュリティ:公開リポジトリにAPIキーが露出

**事象**: 公開リポジトリ `xenomao/xenomao` に NewsAPI のキーが3か所で平文コミットされていた。

| 箇所 | 状態 |
|---|---|
| `.env`(初回コミットから追跡されていた) | 本コミットで追跡解除 + `.env.example` を追加 |
| `scripts/main.py` | `os.getenv("NEWSAPI_KEY", "")` に変更済み |
| `scripts/test_newsapi_simple.py` | `os.getenv("NEWSAPI_KEY", "")` に変更済み |

**残作業(コードでは解決できない)**:

1. **NewsAPI管理画面で当該キーを無効化(revoke)し、新しいキーを再発行する** ← 最優先
   - 過去コミット履歴にキーが残るため、ファイルを消しただけでは漏えい状態は解消しない
2. 新キーはローカルの `.env`(コミットされない)と、GitHub Actions を使う場合は Repository secrets に設定
3. 併せて `SMTP` / `EMAIL_PASSWORD` / `SERPAPI_KEY` も履歴に残っていないか確認(現状は空欄)
4. 中期: `git filter-repo` 等での履歴書き換えを検討(機密DB移動時から積み残し。CLAUDE.md参照)

---

## 2. 【最優先・即日】本番サイトに反映されていない公開物

**根本原因**: GitHub Pages の配信元が **`gh-pages` ブランチ**(Settings→Pages が "Deploy from a branch")なのに、
リポジトリには `main` の `public/` を配信する前提のワークフロー(`.github/workflows/deploy-lp.yml`、
`actions/deploy-pages` 使用=Source が "GitHub Actions" でないと効かない)が同居している。
このため **`main` にマージしても本番に出ない**という状態が続いている。

`gh-pages` と `main:public/` の差分(2026-07-30時点):

| ページ | main | gh-pages(本番) | 影響 |
|---|---|---|---|
| `/sponsor/`(賛助会員デッキ) | あり | **無し** | 賛助会員向けに配る公開URLが **404**。営業活動に直接影響 |
| `/`(メインLP) | 最新 | 旧版 | 年会費表記の修正・ヘルステック導線が本番未反映 |
| `/pureline/` | (本コミットで追加) | あり | 逆にmainに無かった。整合済み |
| `/beauty2040/` | (本コミットで追加) | 無し | 未公開 |

**次アクション(順に)**:

1. **配信方式をどちらかに一本化する**(推奨: Pages の Source を **GitHub Actions** に変更し、`gh-pages` ブランチは廃止)
   - こうすると `main` の `public/` を更新するだけで本番反映され、二重管理と反映漏れが構造的に無くなる
   - 移行できない事情がある場合は、逆に `deploy-lp.yml` を削除し `gh-pages` への同期を必須手順として明文化する
2. 一本化後に `/sponsor/` `/beauty2040/` を含む全ページを再デプロイし、`bash scripts/check_site_health.sh` で全URLの200を確認
3. 資料に載せている公開URL(賛助会員デッキ等)を配布前に再点検

> ※ 本コミットでは `gh-pages` への push は行っていない(本番公開は外向きの操作のため、判断を仰ぐ)。
> 指示があれば同期を実行する。

---

## 3. 【高】停止している自動運用:ヘルステック日次更新

- `healthtech/README.md` には「毎朝7:00 JST に Routine が起動し、日次ニュースをPRで提出」と記載
- しかし `healthtech/news/` の最新は **2026-07-08**。**22日間、生成物が1件も無い**
- Routine が停止/失敗しているか、生成PRが誰にも見られず放置されている可能性

**次アクション**: Routine の稼働状況を確認 → 停止していれば再作成、不要なら README の運用記述を実態に合わせて削除する
(「動いていることになっている止まった仕組み」を残さない)

---

## 4. 【高】ブランド方針転換にともなう既存制作物の改修(未着手)

2026-07-13の指示で「パステルラベンダー主体・淡い路線は廃止、権威性のある配色へ」と方針転換したが、
**既存LP群の改修は未実施**(`docs/strategy/` の資料のみ新方針=ネイビー×ゴールドで制作済み)。

| 対象 | 現状の配色 | 対応 |
|---|---|---|
| メインLP(`marketing/digilab_beauty_lp.html` / `public/index.html`) | パステルラベンダー | 未改修 |
| サロンAI活用度診断 | パステルラベンダー | 未改修 |
| 鎌田麻央LP | パステル系 | 未改修 |
| 会員特典3点(`marketing/member_benefits/`) | パステル系 | 未改修 |
| 検定LP・戦略資料 | ネイビー×ゴールド | **新方針に適合済み** |

**次アクション**: 改修の範囲と順序を決める。メインLPは全導線の起点なので最初に着手すべきだが、
作り直しコストが大きい。**「メインLPのみ改修 / 全面改修 / 現状維持」の三択を理事長判断で確定させる**のが先。

---

## 5. 【高】オープンPRの処理

| PR | 内容 | 状態 | 次アクション |
|---|---|---|---|
| [#13](https://github.com/xenomao/xenomao/pull/13) | Beauty TIMES LP(30分Zoom相談予約・年額プラン) | 2026-07-29から未マージ。成果物としては完成 | レビューしてマージ。マージ後 `gh-pages` にも反映(2.参照)。**OGP画像が未作成**なのでSNS拡散前に1200×630を用意 |
| [#1](https://github.com/xenomao/xenomao/pull/1) | 5/19セミナー会員獲得戦略・デイリータスク | 2026-05-08から放置。**イベントは終了済み** | 中身(`docs/strategy/seminar_membership_daily_tasks_may19.md`)は本コミットでmainへ取り込み済み。**PRはクローズしてよい** |

---

## 6. 【中】Beauty 2040 プロジェクトの立ち上げ(キットは完成・実行は未着手)

`docs/projects/beauty_2040/` に立ち上げキット一式(TODO・リリース文・100人集客プラン)とLPが揃っているが、
**実行タスクは16項目すべて未着手**。フェーズ0(今日〜3日、費用ゼロ)から着手できる。

直近で着手できるもの:

1. コンセプト文の確定(30分・理事長確認)
2. 参加申込Googleフォームの作成(1時間)
3. 公式LINE / Instagram での第一報(1時間)
4. 理事・部会メンバーへ「最初の10人」声かけ依頼

**理事長判断が必要な未決事項**(`docs/projects/beauty_2040/todo_launch.md` 末尾):
参加費 / 参加資格 / 白書の権利 / 「100人」の定義

---

## 7. 【中】営業案件のフォロー(資料は完成・アクションが止まっている)

| 案件 | 完成物 | 未完了 |
|---|---|---|
| タカラベルモント エステ事業部 協業提案 | 提案書(HTML/PDF/MD)、A/B/C一枚もの、Do/Don't詳細版 — `docs/proposals/` | **先方への提出・アポイントが未記録**。2026-07-12以降の進捗が追えない |
| Jエステ アプローチ | メールテンプレ `docs/templates/email_j-esthe_approach.md` | 送付有無が不明 |
| 賛助会員(法人)募集 | デッキ・プレスリリース・公開ページ | 公開URLが404(2.参照)。**プレスリリースも未配信** |

**次アクション**: 営業の進捗管理を非公開リポジトリ側のDBに寄せる(公開リポジトリには置かない)。
最低限、誰にいつ何を送ったかを記録する場所を決める。

---

## 8. 【中】設立プレスリリースが未配信(ドラフトのまま)

`docs/press/press_release_establishment_2026.md` は**配信日が「2026年7月〇日」のまま**。
法人設立は2026-07-24で既に経過している。

**次アクション**: 配信日・代表コメント・配信媒体(PR TIMES等)を確定 → 配信。
設立から時間が経つほどニュース価値が落ちるため、**やるなら早い方がよい / やらないなら文書をアーカイブ扱いにする**の判断を。

---

## 9. 【中】機密データの残置(未移動)

ブランチ `claude/beauty-prospect-list-uoqu3j` に営業見込みリストが残っている:

- `prospects/output/beauty_prospect_10k.csv`(約3.5MB・約1万件)
- `prospects/output/beauty_prospect_200.csv`
- 生成スクリプト・セグメンテーション計画

CLAUDE.mdの規約により**公開リポジトリのmainには取り込まない**(本コミットでも意図的に除外)。

**次アクション**: 非公開リポジトリ `xenomao/digilab-beauty-data` へ移設し、当該ブランチを削除する。
生成スクリプト(`prospects/scripts/*.py`)だけは公開しても問題ないため、必要なら分離して公開側に残す。

---

## 10. 【低】整理・保守

- **未マージブランチ39本**: 本コミットで成果物の吸い上げは完了。中身がmainに入ったブランチは削除してよい
  (削除候補: `claude/*` のうち下表「集約済み」のもの)
- **定款 `デジラボビューティー定款_v2.0.docx`** がブランチ `claude/happy-keller-LuUeR` に残置。
  役員の個人情報を含む可能性があるため、**公開リポジトリに入れず**非公開リポジトリへ移すべき(未対応)
- **`docs/reports/phase1_completion_report.md`** の参照リンクが `file:///C:/Users/pline/...` のローカル絶対パスのまま。リンク切れ
- **`install.ps1`**(`claude/add-powershell-install-script-fD9Hl`)は用途不明。要否を判断して削除か取り込みか決める
- **旧Netlify版の問題集** (https://sunny-queijadas-b66611.netlify.app/) は `/compliance/` に移設済み。**停止手続きが未実施**

---

## 付録: 本コミットでmainへ集約した成果物(2026-07-30)

いずれも**完成済み**でありながら、ブランチに取り残されていたもの。

| 集約先 | 成果物 | 取得元ブランチ |
|---|---|---|
| `docs/strategy/` | 認証制度3段階設計・審査基準草案・理事会説明メモ・ポジショニング1枚・想定問答集・商標予備調査・化粧品×薬機法講座企画・宣言用セルフチェック | `diglab-beauty-positioning-i85trw` |
| `docs/strategy/` | 事業計画書 / ビジネスモデル | `digilab-beauty-business-plan-g8xzyh` / `determined-shannon-kwBTQ` |
| `docs/proposals/` | タカラベルモント協業提案(HTML/PDF/MD)・A/B/C一枚もの・Do/Don'tガイドライン | `takarabelmonte-digilab-synergy-l99sv8` |
| `docs/reports/` | K-Beauty国家戦略分析 / J-Beauty世界展開提言 | `kbeauty-strategy-analysis-dg4yfg` |
| `docs/reports/` | ピュアライン サイト批評・再設計 | `pureline-design-critique-ikwfyp` |
| `docs/reports/` | 成長戦略2026-2030 / デジタルビューティー戦略白書2 / フェーズ1実行計画 | `digital-beauty-strategy-aOBDA` |
| `docs/reports/` | SEO診断 / 指標データ整合性 / シークレット是正 | `digilab-beauty-lp-search-foovgx` / `determined-shannon-kwBTQ` |
| `docs/projects/beauty_2040/` | 立ち上げTODO・リリース記事・100人集客プラン | `beauty-2040-launch-rpnrvq` |
| `docs/whitepapers/` | 白書「AI時代だからこそ輝く人」vol.1(HTML/PDF) | `content-refinement-pdf-4ulogg` |
| `docs/guidelines/` | エステティック広告ガイドライン改定追補(PDF/HTML・snake_caseへ改名) | `relaxed-knuth-6q020` |
| `docs/guides/` | Kimi K3 / LINEステップ配信 / Claude 4.8ワークフロー / Search Console設定 | 各ブランチ |
| `docs/seminar/` `docs/templates/` | 5/19セミナー運営資料5点・フォローアップメール等テンプレ4点 | `setup-operating-system-az0ig` / `clarify-task-CZp9V` |
| `docs/ops/` | ループ設計 / MCP設定 | `ai-agent-loop-design-qvftjx` |
| `marketing/` | Beauty 2040 LP / ピュラインLP / エクソソーム測定チラシ / ロゴSVG / 診断リリースキット / robots・sitemap | 各ブランチ |
| `public/` | `beauty2040/` `pureline/` | 同上 |
| `scripts/` `.claude/` `.mcp.json` | LP同期チェッカー・サイト死活チェッカー・同期ガードフック・スキル2種・LINE配信スクリプト・AI診断スクリプト | `ai-agent-loop-design-qvftjx` / `line-harness-step-line-9bi6sz` / `determined-shannon-kwBTQ` |

**意図的に集約しなかったもの**: 営業見込みリスト(機密・9.参照)、定款docx(個人情報の可能性・10.参照)、
`apps/` と重複する旧 `web/` `webapp/` ディレクトリ、削除済みの `public/CNAME`。
