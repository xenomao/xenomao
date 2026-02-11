#!/usr/bin/env python3
"""
DigiLab Beauty AI組織システム - データベース初期化スクリプト
エステ業界19社のリストをデータベースにインポートします。
"""

import sqlite3
import csv
from datetime import datetime
from pathlib import Path

# データベースファイルのパス
DB_PATH = Path(__file__).parent / "digilab_beauty.db"
SCHEMA_PATH = Path(__file__).parent / "digilab_beauty_db_schema.sql"
CSV_PATH = Path(__file__).parent / "esthetic_industry_dd_19companies.csv"


def create_database():
    """データベースを作成し、スキーマを適用"""
    print(f"データベースを作成中: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # スキーマファイルを読み込んで実行
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
        cursor.executescript(schema_sql)
    
    conn.commit()
    conn.close()
    print("✓ データベース作成完了")


def import_companies_from_csv():
    """CSVファイルから企業データをインポート"""
    print(f"CSVファイルを読み込み中: {CSV_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    imported_count = 0
    skipped_count = 0
    
    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # 破産企業はスキップ
            if '破産' in row.get('営業状況', ''):
                print(f"⚠ スキップ: {row['企業名']} (破産企業)")
                skipped_count += 1
                continue
            
            # 優先度を設定（店舗数や規模に基づく）
            priority = calculate_priority(row)
            
            try:
                cursor.execute("""
                    INSERT INTO companies (
                        company_name, category, operating_company, established_year,
                        headquarters, phone, inquiry_phone, url, store_count,
                        main_services, business_status, priority, notes, created_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row['企業名'],
                    row['カテゴリ'],
                    row['運営会社'],
                    row['設立年'],
                    row['本社所在地'],
                    row['代表電話'],
                    row['問い合わせ先'],
                    row['公式URL'],
                    row['店舗数'],
                    row['主要サービス'],
                    row['営業状況'],
                    priority,
                    row.get('備考', ''),
                    '@AI担当'
                ))
                
                company_id = cursor.lastrowid
                
                # 営業パイプラインの初期ステージを設定
                cursor.execute("""
                    INSERT INTO sales_pipeline (
                        company_id, stage, stage_date, probability, ai_agent
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    company_id,
                    'リード',
                    datetime.now().strftime('%Y-%m-%d'),
                    10,  # 初期確度10%
                    '@AI営業'
                ))
                
                print(f"✓ インポート完了: {row['企業名']} (優先度: {priority})")
                imported_count += 1
                
            except Exception as e:
                print(f"✗ エラー: {row['企業名']} - {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n=== インポート結果 ===")
    print(f"成功: {imported_count}社")
    print(f"スキップ: {skipped_count}社")
    print(f"合計: {imported_count + skipped_count}社")


def calculate_priority(row):
    """企業の優先度を計算（1:最優先 5:低優先）"""
    store_count_str = row.get('店舗数', '0')
    
    # 店舗数から数値を抽出
    import re
    numbers = re.findall(r'\d+', store_count_str)
    if numbers:
        store_count = int(numbers[0])
    else:
        store_count = 0
    
    # 優先度判定ロジック
    if store_count >= 150:
        return 2  # 高優先（大手チェーン）
    elif 50 <= store_count < 150:
        return 3  # 中優先（中堅チェーン）
    elif store_count < 50 and '全国展開' in store_count_str:
        return 3  # 中優先（規模不明だが全国展開）
    elif store_count < 50 and store_count > 0:
        return 4  # 低優先（小規模チェーン）
    else:
        return 5  # 最低優先（情報不足）


def create_initial_tasks():
    """初期タスクを作成"""
    print("\n初期タスクを作成中...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # @AI営業向けタスク
    cursor.execute("""
        INSERT INTO tasks (assigned_to, title, description, priority, status, due_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        '@AI営業',
        '優先度2-3企業へのアプローチメール作成',
        '優先度2-3の企業（約15社）に対するアプローチメールを作成し、送信準備を行う',
        2,
        '未着手',
        (datetime.now().date()).isoformat()
    ))
    
    # @AI担当向けタスク
    cursor.execute("""
        INSERT INTO tasks (assigned_to, title, description, priority, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        '@AI担当',
        'Opal連携システム構築',
        'エステ業界ニュースの自動収集とDD情報の定期更新システムを構築する',
        1,
        '未着手'
    ))
    
    # @AIマーケティング向けタスク
    cursor.execute("""
        INSERT INTO tasks (assigned_to, title, description, priority, status)
        VALUES (?, ?, ?, ?, ?)
    """, (
        '@AIマーケティング',
        'PR TIMES用プレスリリース作成',
        'DigiLab BeautyのAI組織システムに関するプレスリリースを作成する',
        3,
        '未着手'
    ))
    
    conn.commit()
    conn.close()
    print("✓ 初期タスク作成完了")


def display_statistics():
    """データベースの統計情報を表示"""
    print("\n=== データベース統計 ===")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 企業数
    cursor.execute("SELECT COUNT(*) FROM companies")
    company_count = cursor.fetchone()[0]
    print(f"登録企業数: {company_count}社")
    
    # 優先度別集計
    cursor.execute("""
        SELECT priority, COUNT(*) 
        FROM companies 
        GROUP BY priority 
        ORDER BY priority
    """)
    print("\n優先度別:")
    priority_labels = {1: '最優先', 2: '高', 3: '中', 4: '低', 5: '最低'}
    for priority, count in cursor.fetchall():
        print(f"  優先度{priority} ({priority_labels.get(priority, '不明')}): {count}社")
    
    # カテゴリ別集計
    cursor.execute("""
        SELECT category, COUNT(*) 
        FROM companies 
        GROUP BY category 
        ORDER BY COUNT(*) DESC
    """)
    print("\nカテゴリ別:")
    for category, count in cursor.fetchall():
        print(f"  {category}: {count}社")
    
    # タスク数
    cursor.execute("SELECT COUNT(*) FROM tasks")
    task_count = cursor.fetchone()[0]
    print(f"\n登録タスク数: {task_count}件")
    
    conn.close()


def main():
    """メイン処理"""
    print("=" * 60)
    print("DigiLab Beauty AI組織システム - データベース初期化")
    print("=" * 60)
    print()
    
    # データベース作成
    create_database()
    
    # 企業データインポート
    import_companies_from_csv()
    
    # 初期タスク作成
    create_initial_tasks()
    
    # 統計表示
    display_statistics()
    
    print("\n" + "=" * 60)
    print("✓ 初期化完了")
    print(f"データベースファイル: {DB_PATH}")
    print("=" * 60)


if __name__ == "__main__":
    main()
