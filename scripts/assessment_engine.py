#!/usr/bin/env python3
"""
AI活用診断 - スコアリングエンジン
==========================================================
ai_assessment.py から利用される診断ロジック本体。
APIキー不要のルールベースで「DX成熟度スコア・グレード・優先改善・想定効果」を算出する。

数値の根拠について（重要）:
  想定効果レンジは「業界一般の改善幅・当社想定」であり自社実測ではない。
  レポートにも明記し、断定的な実績数値としては提示しない（景表法配慮）。
==========================================================
"""

import os

# レポート出力先（リポジトリ直下 docs/reports/diagnoses/）
REPORT_DIR = os.path.join(os.path.dirname(__file__), "..", "docs", "reports", "diagnoses")


# 5つの評価軸。各軸 1〜4 のレベルを 0〜20 点に換算（合計100点満点）。
AXES = [
    {
        "key": "booking_method",
        "name": "予約・問い合わせ",
        "levels": {
            1: "電話のみ（取りこぼし・機会損失が大きい）",
            2: "電話＋一部web（24時間対応に課題）",
            3: "web/LINE中心（自動化の余地あり）",
            4: "AI/自動化（24時間受付が確立）",
        },
        "improve": {
            "title": "予約のAI自動化（24時間受付）",
            "detail": "AIチャットボット/LINE予約で深夜・営業時間外の問い合わせを取りこぼさない。",
            "effect": "予約取りこぼし削減・問い合わせ対応工数の削減",
        },
    },
    {
        "key": "repeat_tracking",
        "name": "顧客・リピート管理",
        "levels": {
            1: "管理していない（リピート施策が打てない）",
            2: "紙台帳（分析・自動化が困難）",
            3: "Excel（手作業に依存）",
            4: "システム/CRM（データ活用の土台あり）",
        },
        "improve": {
            "title": "顧客データのCRM化とリピート予測",
            "detail": "来店履歴をデータ化し、離反予兆の検知とフォロー自動化につなげる。",
            "effect": "リピート率向上・離反防止",
        },
    },
    {
        "key": "sns_marketing",
        "name": "集客・SNS",
        "levels": {
            1: "していない（新規流入が口コミ頼み）",
            2: "不定期（効果が安定しない）",
            3: "定期運用（最適化の余地あり）",
            4: "AI活用で最適化（投稿・広告を効率化）",
        },
        "improve": {
            "title": "SNS/MEO集客のAI最適化",
            "detail": "投稿生成・広告配信・口コミ返信をAIで効率化し、新規獲得単価を下げる。",
            "effect": "新規客数の増加・広告費の効率化",
        },
    },
    {
        "key": "staff_training",
        "name": "スタッフ研修・標準化",
        "levels": {
            1: "OJTのみ（属人化・ばらつき大）",
            2: "社内マニュアル（更新・浸透に課題）",
            3: "体系的研修（コスト・期間が課題）",
            4: "AI/オンライン研修（全店同時展開）",
        },
        "improve": {
            "title": "AIスタッフ研修による早期戦力化",
            "detail": "スキル別のAI研修で新人を早期戦力化し、店舗間のサービス品質を標準化する。",
            "effect": "教育期間の短縮・品質の均一化",
        },
    },
    {
        "key": "data_usage",
        "name": "データ活用・カウンセリング",
        "levels": {
            1: "していない（勘と経験に依存）",
            2: "集計のみ（示唆に至らない）",
            3: "分析している（提案への接続が課題）",
            4: "AI予測活用（提案の質が高い）",
        },
        "improve": {
            "title": "AIカウンセリングで客単価向上",
            "detail": "顧客データをAIが分析し、最適メニュー・ホームケアを科学的に提案する。",
            "effect": "客単価・物販売上の向上",
        },
    },
]

GRADES = [
    (85, "A: AI先進サロン"),
    (70, "B: DX推進中"),
    (50, "C: 部分的にデジタル化"),
    (30, "D: アナログ中心・伸びしろ大"),
    (0, "E: ほぼ未着手・最優先で改善余地"),
]


def _level_to_points(level):
    """レベル1〜4を0,7,14,20点に換算（4段階を0-20へ）。"""
    table = {1: 0, 2: 7, 3: 14, 4: 20}
    return table.get(level, 0)


def run_diagnosis(answers):
    """診断のコア。スコア・グレード・軸別評価・優先改善3点・想定効果を返す。"""
    axis_results = []
    total = 0
    for axis in AXES:
        level = answers.get(axis["key"], 1)
        try:
            level = int(level)
        except (TypeError, ValueError):
            level = 1
        level = max(1, min(4, level))
        pts = _level_to_points(level)
        total += pts
        axis_results.append({
            "name": axis["name"],
            "level": level,
            "level_label": axis["levels"][level],
            "points": pts,
            "improve": axis["improve"],
        })

    score = total  # 0〜100
    grade = next(label for threshold, label in GRADES if score >= threshold)

    # 優先改善 = 点数が低い軸の上位3つ（伸びしろが大きい順）
    priorities = sorted(axis_results, key=lambda a: a["points"])[:3]
    priority_items = [
        {
            "axis": p["name"],
            "title": p["improve"]["title"],
            "detail": p["improve"]["detail"],
            "effect": p["improve"]["effect"],
            "current": p["level_label"],
        }
        for p in priorities
    ]

    # 想定効果レンジ（※業界一般・当社想定。自社実測ではない）
    expected = estimate_effects(answers, score)

    return {
        "score": score,
        "grade": grade,
        "axes": axis_results,
        "priorities": priority_items,
        "expected": expected,
    }


def estimate_effects(answers, score):
    """想定効果レンジを概算する。低スコアほど伸びしろを大きめに見積もる（あくまで目標値）。"""
    # 伸びしろ係数: スコアが低いほど改善余地が大きい
    headroom = (100 - score) / 100  # 0〜1
    avg_ticket = _safe_int(answers.get("avg_ticket"), 10000)
    monthly_customers = _safe_int(answers.get("monthly_customers"), 100)

    # レンジは控えめ〜やや強気の幅で提示（目標値であることを明記）
    repeat_low, repeat_high = round(5 * headroom, 1), round(20 * headroom, 1)
    ticket_low, ticket_high = round(3 * headroom, 1), round(12 * headroom, 1)

    # 客単価向上による月間売上インパクトの目安（あくまで試算）
    uplift_low = int(monthly_customers * avg_ticket * (ticket_low / 100))
    uplift_high = int(monthly_customers * avg_ticket * (ticket_high / 100))

    return {
        "repeat_rate": (repeat_low, repeat_high),       # %ポイント（目標）
        "avg_ticket_up": (ticket_low, ticket_high),     # %（目標）
        "monthly_uplift_yen": (uplift_low, uplift_high) # 円/月（試算）
    }


def _safe_int(v, default):
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def build_markdown_report(answers, result, review=None):
    """診断結果をMarkdownレポート化する。"""
    exp = result["expected"]
    lines = []
    lines.append(f"# AI活用診断レポート — {answers.get('salon_name', '無名サロン')}")
    lines.append("")
    lines.append(f"- 業態: {answers.get('category', '—')}")
    lines.append(f"- 規模: スタッフ{answers.get('staff_count', '—')}名 / 月間来店{answers.get('monthly_customers', '—')}名 / 平均客単価{answers.get('avg_ticket', '—')}円")
    lines.append("")
    lines.append(f"## 総合: DX成熟度スコア **{result['score']}/100**（{result['grade']}）")
    lines.append("")

    # 軸別スコア（簡易バー）
    lines.append("### 評価軸ごとの現状")
    lines.append("")
    lines.append("| 評価軸 | レベル | 現状 | 点数 |")
    lines.append("|---|---|---|---|")
    for a in result["axes"]:
        bar = "■" * a["level"] + "□" * (4 - a["level"])
        lines.append(f"| {a['name']} | {bar} | {a['level_label']} | {a['points']}/20 |")
    lines.append("")

    # 優先改善3点
    lines.append("### 🎯 優先的に取り組むべき3点（伸びしろの大きい順）")
    lines.append("")
    for i, p in enumerate(result["priorities"], 1):
        lines.append(f"**{i}. {p['title']}**（{p['axis']}）")
        lines.append(f"- 現状: {p['current']}")
        lines.append(f"- 打ち手: {p['detail']}")
        lines.append(f"- 期待: {p['effect']}")
        lines.append("")

    # 想定効果（目標値であることを明記）
    lines.append("### 📈 想定効果レンジ（※自社実測ではなく目標値）")
    lines.append("")
    lines.append("> 以下は業界一般の改善幅と当社想定に基づく目標レンジです。実際の効果は導入状況により異なります。")
    lines.append("")
    lines.append(f"- リピート率: +{exp['repeat_rate'][0]}〜{exp['repeat_rate'][1]} ポイント（目標）")
    lines.append(f"- 客単価: +{exp['avg_ticket_up'][0]}〜{exp['avg_ticket_up'][1]}%（目標）")
    lines.append(f"- 月間売上インパクト試算: 約 {exp['monthly_uplift_yen'][0]:,}〜{exp['monthly_uplift_yen'][1]:,} 円/月（客単価向上ベースの目安）")
    lines.append("")

    # Claude講評（任意）
    if review:
        lines.append("### ✨ 専門コメント")
        lines.append("")
        lines.append(review.strip())
        lines.append("")

    # CTA
    lines.append("---")
    lines.append("")
    lines.append("## 次のステップ")
    lines.append("")
    lines.append("この診断は無料の現状把握です。優先改善の具体化（ツール選定〜定着）は、")
    lines.append("**30分の無料オンライン相談**で、貴サロンに合わせてご提案します。")
    lines.append("")
    lines.append("**▶ 無料相談:** https://digilab-beauty.com/")
    lines.append("")
    lines.append("---")
    lines.append("*DigiLab Beauty — 美容業界のAI・DXを、ここから始める。*")
    lines.append("")
    return "\n".join(lines)


def claude_review_optional(answers, result):
    """ANTHROPIC_API_KEY があれば Claude API で講評文を生成。無ければ None。

    依存(anthropic)やキーが無い環境でも本体が動くよう、失敗は握りつぶして None を返す。
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    try:
        import anthropic
    except ImportError:
        print("  ℹ️ anthropic 未インストールのため Claude講評をスキップ（pip install anthropic）")
        return None

    try:
        client = anthropic.Anthropic(api_key=api_key)
        priorities = "、".join(p["title"] for p in result["priorities"])
        prompt = (
            "あなたは美容業界専門のAI・DXコンサルタントです。"
            "以下のサロン診断結果をもとに、3〜4文の前向きで具体的な講評を日本語で書いてください。"
            "売り込み調を避け、現状の良い点と次の一歩を簡潔に示してください。\n\n"
            f"サロン名: {answers.get('salon_name')}\n"
            f"業態: {answers.get('category')}\n"
            f"DX成熟度スコア: {result['score']}/100（{result['grade']}）\n"
            f"優先改善: {priorities}\n"
        )
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        # テキストブロックを連結
        parts = [b.text for b in msg.content if getattr(b, "type", "") == "text"]
        return "".join(parts).strip() or None
    except Exception as e:
        print(f"  ℹ️ Claude講評の生成をスキップ（{type(e).__name__}）")
        return None
