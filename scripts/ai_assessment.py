#!/usr/bin/env python3
"""
@AI営業 - AI活用診断ツール（フック商品 v1）
==========================================================
サロンの現状を入力すると「DX成熟度スコア + 優先改善3点 + 想定効果レンジ」を
自動レポート化する。無料診断としてリード獲得に用い、診断→商談→受注へつなぐ。

設計方針:
  - APIキー不要で完全動作する「ルールベース診断」が土台（誰でもすぐ動く）。
  - ANTHROPIC_API_KEY があれば Claude API で講評文を肉付け（任意・高度化）。
  - 診断結果は Markdown レポート出力 + documents テーブルへ記録。
  - kpi_tracking に診断実施数を加算（ファネル計測の起点）。

必要なパッケージ:
  pip install python-dotenv
  pip install anthropic   # 任意（Claude講評を使う場合のみ）

環境変数(.env):
  DB_PATH=path/to/digilab_beauty.db   # 未設定なら db/digilab_beauty.db
  ANTHROPIC_API_KEY=sk-...            # 任意。無ければルールベースのみで動作

使い方:
  対話モード:   python scripts/ai_assessment.py
  サンプル実行: python scripts/ai_assessment.py --demo
  JSON入力:     python scripts/ai_assessment.py --input salon.json
==========================================================
"""

import os
import sys
import json
import argparse
import sqlite3
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv が無くても環境変数があれば動く
    pass

from assessment_engine import run_diagnosis, REPORT_DIR
from assessment_engine import build_markdown_report, claude_review_optional


# デフォルトDBパス（既存スクリプト同様 .env を優先）
DEFAULT_DB = os.path.join(os.path.dirname(__file__), "..", "db", "digilab_beauty.db")
DB_PATH = os.getenv("DB_PATH", DEFAULT_DB)


# 診断の質問項目（対話モード用）。choices は assessment_engine の選択肢キーと一致させる。
QUESTIONS = [
    ("salon_name", "サロン名", str, None),
    ("category", "業態（エステ/ネイル/まつエク/脱毛/その他）", str, None),
    ("staff_count", "スタッフ人数（人）", int, None),
    ("monthly_customers", "月間来店客数（おおよそ・人）", int, None),
    ("avg_ticket", "平均客単価（円）", int, None),
    ("booking_method", "予約方法 [1]電話のみ [2]電話+一部web [3]web/LINE中心 [4]AI/自動化", int, None),
    ("repeat_tracking", "リピート顧客の管理 [1]していない [2]紙台帳 [3]Excel [4]システム/CRM", int, None),
    ("sns_marketing", "SNS集客 [1]していない [2]不定期 [3]定期運用 [4]AI活用で最適化", int, None),
    ("staff_training", "スタッフ研修 [1]OJTのみ [2]社内マニュアル [3]体系的研修 [4]AI/オンライン研修", int, None),
    ("data_usage", "顧客データ活用 [1]していない [2]集計のみ [3]分析している [4]AI予測活用", int, None),
]


def ask_interactive():
    """対話形式で診断入力を集める。"""
    print("=" * 70)
    print("🔮 DigiLab Beauty - AI活用診断 v1")
    print("   各項目にお答えください（数字選択は [ ] 内の番号を入力）")
    print("=" * 70)
    answers = {}
    for key, label, caster, _ in QUESTIONS:
        while True:
            raw = input(f"  {label}: ").strip()
            if caster is int:
                try:
                    val = int(raw)
                except ValueError:
                    print("    ⚠ 数字で入力してください")
                    continue
            else:
                val = raw or "（未入力）"
            answers[key] = val
            break
    return answers


def save_to_database(answers, result, report_path):
    """診断結果を documents に記録し、kpi_tracking に実施数を加算する。"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        today = datetime.now().strftime("%Y-%m-%d")

        # documents へ診断レポートを登録
        cur.execute(
            """
            INSERT INTO documents (company_id, document_type, title, file_path, description, ai_agent)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                None,
                "AI診断",
                f"AI活用診断レポート - {answers.get('salon_name', '無名サロン')}",
                report_path,
                f"DX成熟度スコア {result['score']}/100（{result['grade']}）",
                "@AI営業",
            ),
        )

        # kpi_tracking に「AI診断実施数」を1件として記録
        cur.execute(
            """
            INSERT INTO kpi_tracking (date, ai_agent, metric_name, metric_value, target_value, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (today, "@AI営業", "AI診断実施数", 1, None,
             f"{answers.get('salon_name', '無名サロン')} / スコア{result['score']}"),
        )

        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"  ⚠ データベースエラー: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="DigiLab Beauty AI活用診断ツール")
    parser.add_argument("--demo", action="store_true", help="サンプルデータで実行")
    parser.add_argument("--input", metavar="FILE", help="JSONファイルから入力")
    parser.add_argument("--no-db", action="store_true", help="DBへ保存しない")
    args = parser.parse_args()

    # 入力の取得
    if args.demo:
        answers = {
            "salon_name": "サンプル美容サロン",
            "category": "エステ",
            "staff_count": 5,
            "monthly_customers": 180,
            "avg_ticket": 12000,
            "booking_method": 2,
            "repeat_tracking": 3,
            "sns_marketing": 2,
            "staff_training": 1,
            "data_usage": 2,
        }
        print("ℹ️  --demo: サンプルデータで診断します")
    elif args.input:
        with open(args.input, encoding="utf-8") as f:
            answers = json.load(f)
    else:
        answers = ask_interactive()

    # 診断実行（ルールベース・APIキー不要）
    result = run_diagnosis(answers)

    # 任意: Claude API で講評を肉付け（ANTHROPIC_API_KEY があれば）
    review = claude_review_optional(answers, result)

    # Markdown レポート生成
    report_md = build_markdown_report(answers, result, review)
    os.makedirs(REPORT_DIR, exist_ok=True)
    safe_name = "".join(c for c in answers.get("salon_name", "salon") if c.isalnum() or c in "-_")[:30] or "salon"
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(REPORT_DIR, f"diagnosis_{safe_name}_{stamp}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)

    # コンソール表示
    print("\n" + "=" * 70)
    print(f"📊 診断完了: {answers.get('salon_name', '無名サロン')}")
    print(f"   DX成熟度スコア: {result['score']}/100（{result['grade']}）")
    print(f"   優先改善: " + " / ".join(p['title'] for p in result['priorities']))
    print(f"   レポート: {report_path}")
    if review:
        print("   ✨ Claude講評: 付与済み")
    else:
        print("   ℹ️ Claude講評: スキップ（ANTHROPIC_API_KEY未設定）")
    print("=" * 70)

    # DB保存
    if not args.no_db:
        if save_to_database(answers, result, report_path):
            print("✓ documents / kpi_tracking に記録しました")

    return report_path


if __name__ == "__main__":
    main()
