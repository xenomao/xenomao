# Project Learnings

このファイルは、セッションをまたいだ「学び」の記憶装置。
運用ルールは3本のプロンプトだけ:

- **開始時**: `CLAUDE.md` の指示に従い、このファイルを読んで要約する
- **終了時**: `/update-learnings` を実行し、このセッションの学びを該当セクションに追記する
- **週1回**: `/consolidate-learnings` を実行し、古い項目の削除・重複マージ・原則の統合を行う

設計の肝: 「生の観察」(Patterns / Mistakes / Domain Knowledge / Open Questions)と「合成した原則」(Consolidated Principles)は別セクションに分ける。混ぜると、どちらも腐って読まれなくなる。
1項目1洞察、日付(YYYY-MM-DD)を必ず入れる。

## Patterns That Work

効いたやり方・型。

## Mistakes to Avoid

失敗と再発防止策。

## Domain Knowledge

業務・仕様に関する事実(プロジェクト固有の前提知識)。

## Open Questions

要調査・未解決の疑問。

## Consolidated Principles

週1回の統合パスで、上記セクションから抽出・統合した原則。
