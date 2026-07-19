# MCP連携設定(自律運用のための外部ツール接続)

`docs/loop_design.md` のループを自律的に回すためのMCP(Model Context Protocol)連携の整理。2026-07-19 導入。

## ループ運用で使うMCPと役割

| MCP | 接続状態 | 自律運用での役割 |
|---|---|---|
| GitHub | クラウド環境: 組み込み / ローカル: `.mcp.json` で定義 | デプロイ確認(`deploy-lp.yml` の実行結果)、gh-pages反映、PR作成・監視(`subscribe_pr_activity`) |
| Claude Code Remote | クラウド環境: 組み込み | タイム型ループの実体。Routine(定期実行)・`send_later`(自己リマインド)の管理 |
| Playwright | ローカル: `.mcp.json` で定義 | LPの実ブラウザ検証(表示崩れ・リンク切れ・QRコード表示の観測)。「AIに実行結果を直接観測させる」検証手法の実装 |
| Vercel | 接続済み | Vercelデプロイのログ・エラー確認 |
| Gmail | 接続済み | digilabbeauty@gmail.com の問い合わせ確認・返信ドラフト作成 |
| Google Calendar | 接続済み | セミナー・理事会などの日程確認、Routineと組み合わせた前日リマインド |
| Google Drive | 接続済み | 概要資料・セミナー資料の参照 |
| Figma | 接続済み | LP・OGP・エンブレム等のデザイン素材の作成/取り込み |

## リポジトリの `.mcp.json`(ローカルセッション用)

ローカルPCのClaude Codeでこのリポジトリを開くと、次の2つが自動で提供される
(初回にClaude Codeが承認を求めるので許可すること)。

- `github`: GitHub公式リモートMCP(https://api.githubcopilot.com/mcp/)。初回にGitHubのOAuth認証が走る
- `playwright`: `npx @playwright/mcp@latest` で起動するブラウザ操作MCP(Node.js が必要)

クラウド(リモート)セッションでは GitHub MCP と Claude Code Remote が環境組み込みのため、`.mcp.json` の設定は不要。

## インストール済みだが未有効のコネクタ(必要になったら有効化)

Canva / SlidesGPT / Stripe / Manufact はorgにインストール済みだが、チャットでは無効。
有効化はエージェントからはできないため、claude.ai のコネクタ設定から手動で行う。

- Stripe: 賛助会員の年会費(¥100,000〜)の決済管理を自動化する場合に有効化を検討
- Canva / SlidesGPT: 販促資料・セミナー資料の生成を自動化する場合に有効化を検討

## 未接続(将来候補)

- Google Data Cloud(BigQuery): `antigravity_setup_guide.md` 記載のとおり要設定のまま。営業管理DB(非公開リポジトリ `digilab-beauty-data`)の分析を本格化する際に、Service Account Key を用意して接続する
