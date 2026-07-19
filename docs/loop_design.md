# AIエージェント ループ設計(DigiLab Beauty リポジトリ適用版)

「4つのループ特性(ターン型・ゴール型・タイム型・プロアクティブ型)」の考え方を、
本リポジトリの実際の運用課題に当てはめて実装したもの。2026-07-19 導入。

設計の核心は次の2点。

1. **停止条件は機械判定**: 「良い感じ」ではなく、スクリプトの終了コードで判定する。
2. **実行役と検証役の分離(Actor-Verifier)**: 直すのはエージェント、合否を出すのはスクリプト。エージェントの自己採点で完了扱いにしない。

## 本リポジトリでの4パターン対応表

| パターン | 本リポジトリでの実装 | トリガー | 停止条件 |
|---|---|---|---|
| ターン型 | 通常の対話タスク(従来どおり) | 人間の指示 | エージェントの完了判断 |
| ゴール型 | `/lp-sync` スキル | 人間の指示 or LP編集後 | `scripts/check_lp_sync.sh` が終了コード0 / 最大5回試行 |
| タイム型 | `/site-health` スキル + `/loop` or Routine | スケジュール | 各回はチェック完了で待機。異常時のみ報告 |
| プロアクティブ型 | PostToolUse フック(LP同期ガード) | LP対象ファイルの Edit/Write イベント | 同期一致(不一致時のみ警告発火) |

## 各実装の詳細

### 1. ゴール型: LP同期ループ(`/lp-sync`)

本リポジトリ最大の定型リスクは「marketing/ の本体と public/ の配信用コピーの同期漏れ」。
これを定量的停止条件つきのループにした。

- Verifier: `scripts/check_lp_sync.sh` — 同期3ペアを diff し、終了コード=不一致ペア数
- Actor: `.claude/skills/lp-sync/SKILL.md` — 不一致を解消し、Verifierが0を返すまで繰り返す(最大5回)
- 使い方: Claude Code で `/lp-sync` と入力

対象ペア(増やす場合はスクリプトの PAIRS に追記):

- `marketing/digilab_beauty_lp.html` ↔ `public/index.html`
- `marketing/kentei_lp.html` ↔ `public/kentei/index.html`
- `marketing/salon_ai_shindan.html` ↔ `public/shindan/index.html`

### 2. タイム型: 公開サイト死活監視(`/site-health`)

- Verifier: `scripts/check_site_health.sh` — 公開5URLの HTTP 200 判定 + 本番内容とローカル `public/` のハッシュ比較(gh-pages 未反映検知)
- スキル: `.claude/skills/site-health/SKILL.md`
- 単発実行: `/site-health`
- ローカル定期実行(PC稼働中のみ): `/loop 30m /site-health`
- クラウド定期実行(PCを閉じても稼働): Claude Code のリモートセッションで
  「毎朝9時に /site-health を実行する Routine を作って」と依頼する
  (cron `0 9 * * *`・新規セッション起動型。停止は「その Routine を削除して」でよい)

### 3. プロアクティブ型: LP同期ガード(フック)

人間もエージェントも同期を「忘れる」前提で、編集イベント自体をトリガーにした。

- 設定: `.claude/settings.json` の PostToolUse フック
- 実体: `scripts/hook_lp_sync_guard.sh` — 同期対象HTMLが Edit/Write された直後に同期チェックを実行し、不一致ならエージェントに警告を返す(exit 2)
- 対象外ファイルの編集では何もしない

### 4. ターン型

通常の対話はこれまでどおり。ただし LP関連の編集タスクでは、完了報告の前に
`/lp-sync` の Verifier を通すことを標準とする(CLAUDE.md にも記載)。

## 情報の配置ルール(このリポジトリでの適用)

- **CLAUDE.md(憲法)**: 常時読み込まれる共通ルールのみ。現在68行、200行以内を維持する
- **skills(手順書)**: 30行を超える手順は `.claude/skills/` に切り出す(`lp-sync` / `site-health`)
- **scripts(検証役)**: 機械判定ロジックは `scripts/*.sh` に置き、スキルからは呼ぶだけにする
- **hooks(割り込み)**: `.claude/settings.json` に定義。ロジック本体は scripts に置く

## 今後の候補(未実装)

- コンプラ問題集・検定LPのリンク切れチェック(ゴール型)
- `blog/` 更新の定期ルーティン(タイム型)
- gh-pages への反映自動化(現状は手動反映。自動化するなら deploy-lp.yml の拡張として設計する)
