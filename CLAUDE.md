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

### 検定LP(美容AIセキュリティ基礎検定 3級)

- 本体: `marketing/kentei_lp.html` / 配信用コピー: `public/kentei/index.html`(内容は同一。更新時は両方を同期すること)
- 公開URL: https://xenomao.github.io/xenomao/kentei/
- LP本体(`digilab_beauty_lp.html` / `public/index.html`)のグローバルナビ「検定」からリンク
- デザインは「検定・認定証」らしい権威性を出すため、**ディープネイビー×ゴールド**の専用スタイル(明朝: Shippori Mincho / Noto Serif JP)。パステルラベンダーはサブアクセント。認定エンブレム(シール)はSVGで生成
- OGP画像: `public/kentei/ogp.png`(1200×630・ネイビー×ゴールド・認定シール入り)。`og:image`は絶対URL(https://xenomao.github.io/xenomao/kentei/ogp.png)で指定
- 配信の実体: Pages は **GitHub Actions**(`deploy-lp.yml` / `actions/deploy-pages`)から配信されている。`main` の `public/` を更新すれば本番に出る。`gh-pages` ブランチは存在しない(2026-08-28 時点で origin は `main` のみ・直近のデプロイは全て成功)

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
- 内容: 特商法・景表法・薬機法・個人情報保護法・SNS・AIガイドラインの10問+解答解説。「AI美容カウンセリング技能資格(ビューティーフェロー3級)」に基づく学習用教材

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

## 自律開発ハーネス(planner / generator / evaluator)

アプリ・ツールを新規に作る依頼を受けたときは、以下の3役サブエージェントによる
自律ループで進行する。定義は `.claude/agents/` 配下。

### 体制

- **オーケストレーター(メインのあなた)**: 進行管理のみ。仕様も実装も評価もしない
- **planner**(企画): `SPEC.md` / `TASKS.md` を作る。最初に1回だけ起動
- **generator**(実装): 1タスクずつ実装し自己評価。タスクの数だけ繰り返し起動
- **evaluator**(評価): headless Chromeの実機で見て pass/fail を判定

サブエージェント間でメモリは共有されないため、連携は**ファイルベース**で行う。
やり取りの接点は `SPEC.md` / `TASKS.md` / `.claude/reports/` 配下のレポート・
スクリーンショットの3つだけ。

**3役は対等。主役を1つ作らない。** planner の仕様を generator が勝手に握り潰さない、
generator の実装を evaluator が勝手に直さない、evaluator の判定を generator が
上書きしない。各役が自分の禁止事項を守ることでのみ、この体制は機能する。

### タスクの状態

`pending` → `in_progress` → `self_reviewed` → `evaluated(pass)` / `evaluated(fail)`

状態は `TASKS.md` の表で管理する。状態を書き換えてよいのは、その時点で
そのタスクを担当しているエージェントのみ。

### 動き方は7手

1. **依頼** — ユーザーから短い一言を受け取る
2. **計画** — planner が `SPEC.md` / `TASKS.md` を作る
3. **1つ作る** — generator が未着手タスクを1つだけ実装する
4. **検査** — evaluator が実機で見て pass / fail を判定する
5. **不合格なら直して再検査** — fail は同じタスクを generator に差し戻す
6. **合格したら次の1つへ** — pass になって初めて次のタスクに移る
7. **人間が確認する** — 全タスク pass の後、ユーザーが最終確認する

**合格するまで、次の1つには進まない。** 依存関係が無いタスクであっても、
`evaluated(pass)` 以外のタスクが残っている間は次のタスクに着手しない。
同時に2つのタスクが `in_progress` / `self_reviewed` / `evaluated(fail)` に
なっている状態を作らないこと。

### ループの回り方(オーケストレーターの手順)

1. 短い依頼を受け取る
2. `planner` を起動 → `SPEC.md` / `TASKS.md` 作成(1回だけ)
3. **harness.html を出力して `open` で開く**(後述。実装に入る前に必ず)
4. 以下をタスクの数だけ繰り返す
   1. `generator` を起動 → 1タスク実装＋自己評価 → `self_reviewed`
   2. `evaluator` を起動 → 実機確認 → `evaluated(pass)` / `evaluated(fail)`
   3. `fail` なら同じタスクで `generator` に差し戻す(fail回数 +1)
   4. `pass` なら次の `pending` へ
5. `pending` が無くなったらユーザーへ完了報告

ユーザーに話しかけるのは**完了報告のとき**と、**同一タスクが3連続 fail した
とき**の2回だけ。3連続 fail 時は、evaluator の指摘と generator の自己評価の
乖離(何を pass と主張し、何が fail だったか)を並べて相談する。勝手に
受け入れ基準を緩めて先に進めない。

### オーケストレーターの禁止事項

- 自分でコードを書く・直すこと(実装は generator の担当)
- 自分で pass/fail を判定すること(判定は evaluator の担当)
- `SPEC.md` / `TASKS.md` を自分で書き換えること
- 3連続 fail 以外でループを止めてユーザーに質問すること
- サブエージェントの報告を要約せずそのまま長文で貼ること(進捗は1行で伝える)

### harness.html(実装前に必ず出す)

3役の定義と本 CLAUDE.md が揃った時点、かつアプリの実装に入る前に、
「こういうハーネスを作りました」という説明HTMLを **`harness.html`** として
リポジトリ直下に1枚出力し、`open harness.html` で開く。

- 中身は **体制図 / 3役の担当と禁止事項 / ループの回り方 / 人がやること** の4つ
- 文章を並べず**図で見せる**(SVG・カード・フローチャート)
- 配色: 背景グレー `#e9edf3`、カード白、基調 紺 `#0f1f3a`
- LPのパステルラベンダー配色は適用しない(このHTMLは社内向けの説明資料)
- `public/` 配下には置かない(GitHub Pagesへは公開しない)

### このリポジトリでの当てはめ

このリポジトリの課題は3種類ある。**ハーネスをそのまま適用できるのはAだけ**で、
BとCは読み替えが必要。

| | 課題の種類 | ハーネスの適用 |
|---|---|---|
| **A** | アプリ開発(`apps/web` Next.js / `apps/webapp` Flask) | 7手をそのまま適用 |
| **B** | 単一HTML成果物(LP・診断・教材・デッキ) | 適用するが下記の読み替えが必須 |
| **C** | 文言・法令表現・ブランド・名称の判断 | **適用しない。人間が決める** |

#### B(単一HTML成果物)での読み替え

1. **タスクの単位は「機能」ではなく「セクション/ページ」**。
   1ファイルで完結するため、planner は画面のセクション単位で分割する。
2. **起動コマンドは不要**。evaluator は `file://` で直接開く。
   サーバ起動が要るのはAのときだけ。
3. **同期ペアの一致は受け入れ基準に必ず入れる**（最重要）。
   `marketing/` の本体と `public/` の配信コピーは同一内容を保つ規約だが、
   **片方だけ見ても絶対に気づけない**ため、目視ではなく `diff -q` で機械的に
   検証する。現在の同期ペア:

   | 本体 | 配信コピー |
   |---|---|
   | `marketing/digilab_beauty_lp.html` | `public/index.html` |
   | `marketing/kentei_lp.html` | `public/kentei/index.html` |
   | `marketing/salon_ai_shindan.html` | `public/shindan/index.html` |
   | `marketing/digilab_beauty_sponsor_deck.html` | `public/sponsor/index.html` |
   | `marketing/kamata_mao_lp.html` | `public/kamata/index.html` |

4. **単一HTMLが巨大**(最大1.2MB・画像はbase64埋め込み)。
   generator は**全文を `Read` しない**。`Grep` で該当箇所を特定し、
   `Edit` で部分置換する。`Write` による全文書き直しは禁止。
5. **公開ページはデプロイ時に書き換わる**。`scripts/aio_deploy_patch.py` が
   `public/index.html` にJSON-LD等を注入するため、**ローカル確認の結果は
   本番と一致しない**。evaluator が判定できるのはリポジトリ内のHTMLまで。
   デプロイ後の実ページ確認は人間の担当。
6. **ブランド規約は「好み」ではなく合否条件**。planner は SPEC の受け入れ基準に
   明記する(通常のLP/教材=白基調×パステルラベンダー、検定LP=ネイビー×ゴールド)。
   evaluator はこれを根拠に fail を出してよい。
7. **QRコードは目視で pass にしない**。読み取り検証を行うか、できなければ
   人間確認へ回す。

#### C(人間が決める領域)— evaluator は pass を出してはならない

以下は画面を見ても正しさを判定できない。planner は SPEC の
「人間が確認する事項」に切り出し、evaluator は判定を保留して
オーケストレーター経由で人間に上げる。

- 薬機法・景表法・特商法に関わる表現の可否
- 団体・個人の**正式名称、役職、実績**の表記
- 料金・会費の掲載可否と金額
- 個人情報の取り扱い・プライバシーポリシーの記載内容

#### 全課題共通の禁止事項(generator)

- 機密データ(DB・営業リスト・個人情報)をこの公開リポジトリに置くこと
- `tools/kpi_dashboard.html`(社内用)を `public/` 配下に移すこと

### 人がやること

- 最初の一言(何を作りたいか)を渡す
- 3連続 fail の相談に答える
- 完了報告を受けて最終確認する

それ以外は介入しない。
