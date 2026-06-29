#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国税庁 法人番号公表サイトから「実在企業」の会社名・住所を抽出するツール。

このスクリプトは架空データを生成しません。公的に公表されている法人情報
（会社名・所在地・法人番号）のみを扱い、美容業界に関連するキーワードで
絞り込んで営業リストのベースを作ります。

⚠️ 法人番号DBには「電話番号・メールアドレス・担当部署」は含まれません。
   それらは公式サイト・Google Places・許諾済み企業DB等で別途エンリッチ
   してください（prospects/segmentation_plan.md 参照）。

使い方は2通り:

1) 一括ダウンロードCSVを処理（推奨・APIキー不要）
   事前に都道府県別CSVを取得:
     https://www.houjin-bangou.nta.go.jp/download/
   （Shift-JIS / ヘッダ無し / 30列の固定フォーマット）

     python fetch_houjin_bangou.py bulk \
         --input 13_tokyo_all_20240101.csv \
         --output ../output/beauty_tokyo.csv \
         --limit 10000

2) Web-API で名称検索（要 application id）
   申請: https://www.houjin-bangou.nta.go.jp/webapi/
     export NTA_APP_ID=xxxxxxxxxxxxx
     python fetch_houjin_bangou.py api --keyword エステ --pref 13
"""

import argparse
import csv
import os
import sys

# 美容業界の名称キーワード（必要に応じて編集）。
# 会社名にこれらが含まれる法人を候補として抽出する。
DEFAULT_KEYWORDS = [
    "エステ", "ネイル", "美容", "ビューティ", "ビューティー", "beauty",
    "整体", "鍼灸", "アロマ", "セラピ", "リラク", "サロン", "salon",
    "化粧品", "コスメ", "cosme", "スキンケア", "美容機器", "美容外科",
    "クリニック", "皮膚科", "脱毛", "まつげ", "アイラッシュ", "ヘアサロン",
]

# 法人番号 一括ダウンロードCSV（ヘッダ無し）の列インデックス（0始まり）。
# 公式の列定義に基づく。詳細:
#   https://www.houjin-bangou.nta.go.jp/download/zenken/  の「ファイル形式」
COL_HOUJIN_BANGO = 1   # 法人番号
COL_NAME = 6           # 商号又は名称
COL_PREF = 9           # 国内所在地（都道府県）
COL_CITY = 10          # 国内所在地（市区町村）
COL_STREET = 11        # 国内所在地（丁目番地等）
COL_POSTAL = 15        # 郵便番号
MIN_COLUMNS = 16       # これ未満の行は不正としてスキップ

OUTPUT_HEADER = [
    "No.", "会社名", "業種カテゴリ", "郵便番号", "住所",
    "担当部署", "担当者名", "電話番号", "メールアドレス",
    "公式URL", "問い合わせフォームURL", "従業員規模",
    "情報取得元", "取得日", "オプトイン状況", "営業ステータス",
    "法人番号", "備考",
]


def matches(name, keywords):
    return any(k.lower() in name.lower() for k in keywords)


def write_rows(out_path, rows):
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(OUTPUT_HEADER)
        for i, r in enumerate(rows, start=1):
            w.writerow([i] + r)
    print(f"✅ {len(rows)} 件を書き出しました -> {out_path}")
    if rows:
        print("   ※ 電話番号・メール・担当部署は空欄です。エンリッチ工程で補完してください。")


def run_bulk(args):
    keywords = args.keywords.split(",") if args.keywords else DEFAULT_KEYWORDS
    seen = set()
    rows = []
    # 法人番号DBは Shift-JIS。読めない文字はエラーにせず無視。
    with open(args.input, encoding="cp932", errors="ignore", newline="") as f:
        reader = csv.reader(f)
        for cols in reader:
            if len(cols) < MIN_COLUMNS:
                continue
            name = cols[COL_NAME].strip()
            if not name or not matches(name, keywords):
                continue
            bango = cols[COL_HOUJIN_BANGO].strip()
            if bango in seen:
                continue
            seen.add(bango)
            address = f"{cols[COL_PREF]}{cols[COL_CITY]}{cols[COL_STREET]}".strip()
            rows.append([
                name, "", cols[COL_POSTAL].strip(), address,
                "", "", "", "", "", "", "",
                "国税庁法人番号公表サイト", args.date, "未取得", "未着手",
                bango, "会社名・住所のみ実データ／要エンリッチ",
            ])
            if args.limit and len(rows) >= args.limit:
                break
    write_rows(args.output, rows)


def run_api(args):
    try:
        import requests
    except ImportError:
        sys.exit("requests が必要です: pip install -r requirements.txt")

    app_id = os.environ.get("NTA_APP_ID")
    if not app_id:
        sys.exit("環境変数 NTA_APP_ID を設定してください（https://www.houjin-bangou.nta.go.jp/webapi/）")

    # Web-API v4: 名称（あいまい検索 mode=2）でCSV(Shift-JIS)を取得
    url = "https://api.houjin-bangou.nta.go.jp/4/name"
    params = {
        "id": app_id,
        "name": args.keyword,
        "type": "12",          # 12=CSV(Shift-JIS), 02=CSV(Unicode)
        "mode": "2",           # 2=あいまい一致
        "target": "1",         # 1=JIS第一・第二水準
    }
    if args.pref:
        params["address"] = args.pref  # 都道府県コード等で絞り込み
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    resp.encoding = "cp932"
    rows = []
    seen = set()
    reader = csv.reader(resp.text.splitlines())
    for cols in reader:
        # API CSV は列構成が一括版と異なる。先頭付近: [連番, 法人番号, ..., 名称(2), ...]
        if len(cols) < 3:
            continue
        bango = cols[1].strip()
        name = cols[2].strip() if len(cols) > 2 else ""
        if not name or bango in seen:
            continue
        seen.add(bango)
        rows.append([
            name, "", "", "", "", "", "", "", "", "", "",
            "国税庁法人番号Web-API", args.date, "未取得", "未着手",
            bango, "API取得／要エンリッチ",
        ])
    write_rows(args.output, rows)


def main():
    p = argparse.ArgumentParser(description="国税庁 法人番号DB から美容業界の実在企業を抽出")
    p.add_argument("--date", default="2026-06-29", help="取得日（YYYY-MM-DD）")
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("bulk", help="一括ダウンロードCSVを処理（APIキー不要）")
    b.add_argument("--input", required=True, help="都道府県別CSV（Shift-JIS）")
    b.add_argument("--output", default="../output/beauty_prospects.csv")
    b.add_argument("--keywords", help="カンマ区切りの抽出キーワード（省略時は既定セット）")
    b.add_argument("--limit", type=int, default=0, help="最大件数（0=無制限）")
    b.set_defaults(func=run_bulk)

    a = sub.add_parser("api", help="Web-APIで名称検索（要 NTA_APP_ID）")
    a.add_argument("--keyword", required=True, help="検索する名称キーワード")
    a.add_argument("--pref", help="都道府県コード等での絞り込み（任意）")
    a.add_argument("--output", default="../output/beauty_prospects_api.csv")
    a.set_defaults(func=run_api)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
