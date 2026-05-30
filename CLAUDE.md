# CLAUDE.md — DigiLab Beauty AI 組織システム

このファイルは Claude Code がセッション開始時に自動で読み込みます。
（Codex 用の `codex.md` とは別ファイル。重複箇所は本ファイルを優先）

## プロジェクト概要
DigiLab Beauty AI 組織システム。エステ業界19社への B2B 営業・マーケティングを
管理する、コンテンツ＋軽量スクリプト中心のプロジェクト（約70ファイル規模）。

## AI 組織（役割）
- @AI Executive Officer — 戦略・KPI 管理
- @AI Sales — 19社（Tier A/B/C）への営業アウトリーチ
- @AI Marketing — PR・SNS・コンテンツ制作（Lovart AI 連携）
- @AI Intelligence — NewsAPI によるニュース収集・業界モニタリング
- @AI Secretary — メール手順・文書管理

## 主要ファイル
- `scripts/main.py` — セットアップ（DB 初期化、企業インポート、ニュース収集）
- `scripts/daily_news_collection.py` — NewsAPI 日次ニュース収集
- `db/digilab_beauty.db` — SQLite（8テーブル）
- `db/esthetic_industry_dd_19companies.csv` — 19社のソースデータ
- `marketing/digilab_beauty_flyer.html` — A4 印刷用チラシ
- `blog/` — ブログ記事（約50本、Markdown）／`blog/cta_template.md` は CTA 雛形
- `docs/guides/claude_4.8_workflow_guide.md` — 4.8 運用ガイド（Effort / ダイナミック WF）

## 技術スタック
- Python 3.12 / SQLite / NewsAPI / Lovart AI

## 規約
- ドキュメントは日本語
- ブランドカラー: 紫 `#8b2fc9` / ピンク `#d946a8` / ゴールド `#ffd700`
- ファイル命名: snake_case

---

## Claude Code 運用ポリシー（4.8）
- プラン: **Pro**。**既定モデルは Sonnet 4.6**。Opus 4.8（および `xhigh`・ダイナミック WF の
  本領）を使うには `/model opus` で切替える。Opus は Pro では消費が速く、上限超過時は
  自動的に Sonnet へフォールバックすることがある。
- ダイナミックワークフローは `/config` の「Dynamic workflows」で手動有効化が必要。

### Effort（努力度）— 都度選択（固定しない）
既定値は意図的に固定していない（`settings.json` の `effortLevel` 未設定）。`/effort` で
タスクごとに選ぶ。目安:
- `low` / `medium` … 誤字修正・リンク差し替え・体裁調整など軽微／低コスト作業
- `high` … 通常のブログ執筆・記事編集・スクリプト小修正（Sonnet 4.6 / Opus 4.8 の既定）
- `xhigh` … 複数ファイルのリファクタ／監査／一括変更（**Opus 4.7/4.8 のみ**。Sonnet では high に縮退）
- `max` … 最難関の単発のみ（過剰思考に陥りやすく逓減あり。そのセッション限定）
- 単発で深く考えさせたい時はプロンプトに `ultrathink` を入れる（Effort 設定は変えずその回だけ深掘り）

### ダイナミックワークフロー — 明示的に呼ぶ時だけ
- **既定では使わない。`ultracode`（auto）にしない。Claude 側から自動起動しないこと。**
- 本プロジェクトは約70ファイル規模のため、大半の作業は通常セッションで十分。
- ユーザーが明示依頼した大規模バッチ（例: 全ブログ記事の一括リライト、19社分の
  営業文一括生成、多言語ローカライズ、全記事の横断監査）に限り、起動を提案・実行する。
- 起動は**実行前のプレビュー確認**を経ること。通常より消費（usage）が大幅に増える点を
  必ず事前に伝える。Pro の利用上限に当たりやすいので小範囲で試運転 → 拡大。
- 上限: 同時 16 ／ 合計 1,000 サブエージェント。進捗は自動保存され中断後に再開可能。
