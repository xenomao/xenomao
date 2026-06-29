#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
デジラボビューティ 賛助会員営業リスト 1万件 生成スクリプト

出力構成:
  行 1〜200   : 実在確認済み企業データ（beauty_prospect_200.csv より）
  行 201〜10000: カテゴリ×都道府県別 収集ターゲット管理行（収集状況=未収集）

※ 未収集行の連絡先（電話・メール・担当部署）は空欄です。
  prospects/segmentation_plan.md に記載の合法的データ源から埋めてください。
"""
import csv
import os
import itertools

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output")
os.makedirs(OUT_DIR, exist_ok=True)

BASE_CSV = os.path.join(OUT_DIR, "beauty_prospect_200.csv")
OUT_CSV  = os.path.join(OUT_DIR, "beauty_prospect_10k.csv")

HEADER = [
    "No.", "企業名", "カテゴリ", "運営会社",
    "都道府県", "住所詳細", "担当部署",
    "代表電話", "メールアドレス", "公式URL",
    "規模・店舗数", "主要サービス", "営業状況",
    "PRTIMES掲載実績", "収集状況", "備考",
]

# ── 都道府県と割り当て目標件数（合計 9,800） ─────────────────────────────────
PREF_ALLOC = [
    ("東京都",   2655),
    ("大阪府",   1100),
    ("神奈川県",  750),
    ("愛知県",   600),
    ("福岡県",   400),
    ("埼玉県",   380),
    ("千葉県",   380),
    ("北海道",   320),
    ("兵庫県",   300),
    ("京都府",   220),
    ("広島県",   170),
    ("宮城県",   160),
    ("静岡県",   160),
    ("新潟県",   110),
    ("熊本県",   110),
    ("岡山県",   100),
    ("鹿児島県",  90),
    ("長野県",    80),
    ("群馬県",    80),
    ("栃木県",    80),
    ("茨城県",    80),
    ("岐阜県",    70),
    ("三重県",    70),
    ("滋賀県",    60),
    ("奈良県",    60),
    ("山口県",    60),
    ("長崎県",    55),
    ("石川県",    55),
    ("富山県",    50),
    ("大分県",    50),
    ("宮崎県",    60),
    ("愛媛県",    60),
    ("香川県",    55),
    ("高知県",    55),
    ("徳島県",    55),
    ("和歌山県",  55),
    ("山梨県",    55),
    ("福井県",    50),
    ("島根県",    50),
    ("鳥取県",    50),
    ("佐賀県",    50),
    ("秋田県",    50),
    ("山形県",    50),
    ("岩手県",    50),
    ("青森県",    50),
    ("福島県",    50),
    ("沖縄県",   100),
]

# 合計確認
total_alloc = sum(n for _, n in PREF_ALLOC)
assert total_alloc == 9800, f"合計が9800ではありません: {total_alloc}"

# ── カテゴリ比率（各都道府県の割り当てをこの比率で分割） ─────────────────────
CATEGORIES = [
    ("エステサロン",          0.20),
    ("ネイルサロン",          0.15),
    ("美容整体・小顔矯正",    0.10),
    ("美容鍼灸院",            0.08),
    ("アロマ・リラクゼーション",0.08),
    ("美容クリニック",        0.08),
    ("美容機器メーカー・ディーラー", 0.06),
    ("化粧品メーカー",        0.08),
    ("ヘアサロン・サロンオーナー",   0.08),
    ("IT・AI×美容",          0.09),
]
# 合計1.0確認
assert abs(sum(r for _, r in CATEGORIES) - 1.0) < 1e-9

# ── 収集ターゲット行の推奨データ源メモ ──────────────────────────────────────
SOURCE_NOTE = {
    "エステサロン":           "ホットペッパービューティー掲載企業公式サイト / 日本エステティック協会会員",
    "ネイルサロン":           "JNA（日本ネイリスト協会）会員 / ホットペッパービューティー",
    "美容整体・小顔矯正":     "エキテン・ホットペッパービューティー / iタウンページ「整体」",
    "美容鍼灸院":             "日本鍼灸師会地方師会会員名簿 / 鍼灸ポータルサイト",
    "アロマ・リラクゼーション":"AEAJ認定サロン一覧 / ホットペッパービューティー",
    "美容クリニック":         "日本美容外科学会(JSAS)会員 / 各クリニック公式サイト",
    "美容機器メーカー・ディーラー": "BeautyWorld Japan展示会出展者一覧 / 国税庁法人番号DB",
    "化粧品メーカー":         "日本化粧品工業会(JCIA)会員 / 国税庁法人番号DB",
    "ヘアサロン・サロンオーナー":  "ホットペッパービューティー / 美容師会 / iタウンページ",
    "IT・AI×美容":           "スタートアップDB / PRTIMES / 展示会(BeautyTech系)",
}

# ── 実在200社を読み込む ───────────────────────────────────────────────────────
real_rows = []
with open(BASE_CSV, encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    for r in reader:
        real_rows.append(r)

# ── 1万件 CSV を生成 ─────────────────────────────────────────────────────────
with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(HEADER)

    # 行1〜200: 実在確認済み
    for i, r in enumerate(real_rows, start=1):
        w.writerow([
            i,
            r.get("企業名", ""),
            r.get("カテゴリ", ""),
            r.get("運営会社", ""),
            "",                         # 都道府県（既存データは住所詳細に含む）
            r.get("本社所在地", ""),
            "マーケティング・広報部",     # 担当部署（デフォルト）
            r.get("代表電話", ""),
            r.get("問い合わせ先", ""),
            r.get("公式URL", ""),
            r.get("規模・店舗数", ""),
            r.get("主要サービス", ""),
            r.get("営業状況", ""),
            r.get("PRTIMES掲載実績", ""),
            "収集済み",
            r.get("備考", ""),
        ])

    # 行201〜10000: カテゴリ×都道府県 収集管理行
    row_num = 201
    for pref, alloc in PREF_ALLOC:
        # カテゴリ別に件数を分配
        cat_counts = []
        remaining = alloc
        for idx, (cat, ratio) in enumerate(CATEGORIES):
            if idx == len(CATEGORIES) - 1:
                cnt = remaining
            else:
                cnt = round(alloc * ratio)
                remaining -= cnt
            cat_counts.append((cat, cnt))

        for cat, cnt in cat_counts:
            source = SOURCE_NOTE.get(cat, "国税庁法人番号DB / 業界ポータル")
            for _ in range(cnt):
                w.writerow([
                    row_num,
                    "",             # 企業名（未収集）
                    cat,
                    "",             # 運営会社（未収集）
                    pref,
                    "",             # 住所詳細（未収集）
                    "",             # 担当部署（未収集）
                    "",             # 電話番号（未収集）
                    "",             # メールアドレス（未収集）
                    "",             # URL（未収集）
                    "",             # 規模（未収集）
                    cat.replace("・", " ") + "関連サービス",
                    "営業中（推定）",
                    "",
                    "未収集",
                    f"収集元推奨: {source}",
                ])
                row_num += 1

total_rows = row_num - 1
print(f"✅ {total_rows} 件を生成 → {OUT_CSV}")
print(f"   収集済み（実在確認済み）: 200 社")
print(f"   未収集（ターゲット管理行）: {total_rows - 200} 社")
print(f"   ファイルサイズ: {os.path.getsize(OUT_CSV):,} bytes")
