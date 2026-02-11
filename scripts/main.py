#!/usr/bin/env python3
"""
==========================================================
DigiLab Beauty AI組織システム - Replit統合スクリプト
==========================================================

このスクリプトをReplitにコピーして実行するだけで、
以下が自動的に完了します：

1. データベース作成（SQLite）
2. エステ業界18社のデータインポート
3. 営業パイプライン初期化
4. 初期タスク作成
5. NewsAPIによるニュース収集テスト
6. 統計レポート表示

使い方:
  1. Replitで新しいPython Replを作成
  2. このファイルの内容をmain.pyにコピー
  3. 「Run」ボタンを押す
==========================================================
"""

import sqlite3
import json
import re
import urllib.request
import urllib.parse
from datetime import datetime, timedelta

# ===================================
# 設定
# ===================================
DB_NAME = "digilab_beauty.db"
NEWSAPI_KEY = "d28b5d379b234515b40cd8d2bbb64068"

# ===================================
# 1. データベース作成
# ===================================
def create_database():
    print("=" * 60)
    print("📦 Step 1: データベース作成")
    print("=" * 60)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # テーブル作成
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS companies (
            company_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name VARCHAR(255) NOT NULL,
            category VARCHAR(100),
            operating_company VARCHAR(255),
            established_year VARCHAR(50),
            headquarters TEXT,
            phone VARCHAR(50),
            inquiry_phone VARCHAR(50),
            email VARCHAR(255),
            url VARCHAR(500),
            store_count VARCHAR(50),
            main_services TEXT,
            business_status VARCHAR(50) DEFAULT '営業中',
            priority INTEGER DEFAULT 3,
            tier VARCHAR(5) DEFAULT 'C',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS contacts (
            contact_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            contact_name VARCHAR(100),
            position VARCHAR(100),
            department VARCHAR(100),
            email VARCHAR(255),
            phone VARCHAR(50),
            is_primary BOOLEAN DEFAULT 0,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(company_id)
        );

        CREATE TABLE IF NOT EXISTS contact_history (
            history_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            contact_date DATE NOT NULL,
            contact_type VARCHAR(50),
            contact_person VARCHAR(100),
            subject VARCHAR(255),
            content TEXT,
            result VARCHAR(100),
            next_action TEXT,
            next_action_date DATE,
            ai_agent VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(company_id)
        );

        CREATE TABLE IF NOT EXISTS tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            assigned_to VARCHAR(50) NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            priority INTEGER DEFAULT 3,
            status VARCHAR(50) DEFAULT '未着手',
            due_date DATE,
            completed_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(company_id)
        );

        CREATE TABLE IF NOT EXISTS sales_pipeline (
            pipeline_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            stage VARCHAR(50) NOT NULL,
            stage_date DATE NOT NULL,
            expected_value DECIMAL(10, 2),
            probability INTEGER,
            notes TEXT,
            ai_agent VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(company_id)
        );

        CREATE TABLE IF NOT EXISTS documents (
            document_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            document_type VARCHAR(50),
            title VARCHAR(255) NOT NULL,
            file_path TEXT,
            description TEXT,
            ai_agent VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (company_id) REFERENCES companies(company_id)
        );

        CREATE TABLE IF NOT EXISTS intelligence_log (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER,
            source VARCHAR(100),
            info_type VARCHAR(50),
            title VARCHAR(255),
            content TEXT,
            url TEXT,
            collected_date DATE NOT NULL,
            ai_agent VARCHAR(50) DEFAULT '@AI担当',
            is_important BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS kpi_tracking (
            kpi_id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            ai_agent VARCHAR(50),
            metric_name VARCHAR(100),
            metric_value DECIMAL(10, 2),
            target_value DECIMAL(10, 2),
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_companies_status ON companies(business_status);
        CREATE INDEX IF NOT EXISTS idx_companies_priority ON companies(priority);
        CREATE INDEX IF NOT EXISTS idx_companies_tier ON companies(tier);
        CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON tasks(assigned_to);
        CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
        CREATE INDEX IF NOT EXISTS idx_sales_pipeline_stage ON sales_pipeline(stage);
    """)

    conn.commit()
    conn.close()
    print("✅ データベース作成完了（8テーブル）")


# ===================================
# 2. エステ業界18社インポート
# ===================================
def import_companies():
    print("\n" + "=" * 60)
    print("📥 Step 2: エステ業界18社データインポート")
    print("=" * 60)

    companies = [
        {
            "name": "メナードフェイシャルサロン",
            "category": "エステチェーン",
            "operator": "日本メナード化粧品株式会社",
            "year": "1959年11月",
            "hq": "愛知県名古屋市中区丸の内3-18-15",
            "phone": "052-961-3181",
            "inquiry": "0120-164601",
            "url": "https://www.menard.co.jp/",
            "stores": "約2740店舗",
            "services": "フェイシャル中心",
            "tier": "A",
            "priority": 1,
            "notes": "化粧品メーカー系列・最多店舗数"
        },
        {
            "name": "エステティックTBC",
            "category": "エステチェーン",
            "operator": "TBCグループ株式会社",
            "year": "1976年3月",
            "hq": "東京都新宿区西新宿1-25-1 新宿センタービル43F",
            "phone": "03-3345-1311",
            "inquiry": "0120-707-434",
            "url": "https://www.tbc.co.jp/",
            "stores": "173店舗",
            "services": "脱毛・フェイシャル・ボディ",
            "tier": "A",
            "priority": 2,
            "notes": "全国47都道府県展開"
        },
        {
            "name": "MAQUIA",
            "category": "まつげエクステ",
            "operator": "株式会社MAQUIA",
            "year": "2012年4月",
            "hq": "東京都新宿区西新宿6-15-1",
            "phone": "03-5990-5806",
            "inquiry": "店舗により異なる",
            "url": "https://www.e-maquia.jp/",
            "stores": "170店舗",
            "services": "まつげエクステ専門",
            "tier": "A",
            "priority": 2,
            "notes": "まつエク最大手"
        },
        {
            "name": "ミュゼプラチナム",
            "category": "脱毛エステ",
            "operator": "新生ミュゼプラチナム株式会社",
            "year": "再設立",
            "hq": "東京都千代田区",
            "phone": "記載なし",
            "inquiry": "0120-055-065",
            "url": "https://www.musee-pla.com/",
            "stores": "直営12+FC144=156店舗",
            "services": "美容脱毛",
            "tier": "A",
            "priority": 2,
            "notes": "旧運営会社破産・現在新体制"
        },
        {
            "name": "ミスパリ",
            "category": "エステチェーン",
            "operator": "株式会社シェイプアップハウス",
            "year": "1984年3月",
            "hq": "東京都中央区銀座5-10-2",
            "phone": "03-6757-6502",
            "inquiry": "0120-860-239",
            "url": "https://www.miss-paris.co.jp/",
            "stores": "93店舗",
            "services": "総合エステ",
            "tier": "A",
            "priority": 2,
            "notes": "売上高ランキング1位(2024年)"
        },
        {
            "name": "ジェイエステティック",
            "category": "エステチェーン",
            "operator": "株式会社ザ・フォウルビ",
            "year": "1979年11月",
            "hq": "栃木県宇都宮市江曽島本町12-6",
            "phone": "028-659-0820",
            "inquiry": "0120-169-119",
            "url": "https://www.j-esthe.com/",
            "stores": "89店舗以上",
            "services": "美肌脱毛・フェイシャル",
            "tier": "B",
            "priority": 3,
            "notes": "創業40年以上・全国展開"
        },
        {
            "name": "Beauty Face",
            "category": "シェービングサロン",
            "operator": "株式会社リビアス",
            "year": "2002年2月",
            "hq": "大阪府大阪市淀川区西中島1-11-34",
            "phone": "06-6301-1138",
            "inquiry": "店舗により異なる",
            "url": "https://beauty-face.jp/",
            "stores": "75店舗以上",
            "services": "顔そり・シェービング",
            "tier": "B",
            "priority": 3,
            "notes": "女性専門サロン"
        },
        {
            "name": "たかの友梨ビューティクリニック",
            "category": "エステチェーン",
            "operator": "株式会社不二ビューティ",
            "year": "1979年11月",
            "hq": "東京都渋谷区代々木3-37-5",
            "phone": "03-5304-1107",
            "inquiry": "0120-73-1107",
            "url": "https://www.takanoyuri.com/",
            "stores": "70店舗",
            "services": "エステティック全般",
            "tier": "B",
            "priority": 3,
            "notes": "高級路線・老舗ブランド"
        },
        {
            "name": "スリムビューティハウス",
            "category": "エステチェーン",
            "operator": "株式会社スリムビューティハウス",
            "year": "1987年10月",
            "hq": "東京都港区新橋6-4-9",
            "phone": "03-3486-3636",
            "inquiry": "0120-53-3636",
            "url": "https://slim.co.jp/",
            "stores": "55店舗",
            "services": "ボディ・フェイシャル",
            "tier": "B",
            "priority": 3,
            "notes": "東洋美容理論導入"
        },
        {
            "name": "エルセーヌ",
            "category": "エステチェーン",
            "operator": "株式会社TLC",
            "year": "2017年10月",
            "hq": "東京都台東区小島2-17-12",
            "phone": "記載なし",
            "inquiry": "0120-31-3339",
            "url": "https://www.elleseine.co.jp/",
            "stores": "約50店舗",
            "services": "総合エステ",
            "tier": "B",
            "priority": 3,
            "notes": "2024年4月より株式会社TLCが運営"
        },
        {
            "name": "クイーンズウェイ",
            "category": "リフレクソロジー",
            "operator": "株式会社RAJA",
            "year": "1996年7月",
            "hq": "東京都新宿区市谷仲之町3-5",
            "phone": "各店舗へ直接",
            "inquiry": "問い合わせフォームのみ",
            "url": "https://www.queensway-group.jp/",
            "stores": "約50店舗",
            "services": "英国式リフレクソロジー",
            "tier": "B",
            "priority": 3,
            "notes": "1997年開業・リフレ専門"
        },
        {
            "name": "ポーラ ザ ビューティー",
            "category": "エステ・化粧品",
            "operator": "株式会社ポーラ",
            "year": "1946年7月",
            "hq": "東京都品川区西五反田2-2-3",
            "phone": "03-3494-7111",
            "inquiry": "0120-117111",
            "url": "https://www.pola.co.jp/",
            "stores": "全国展開",
            "services": "化粧品・エステ融合",
            "tier": "B",
            "priority": 3,
            "notes": "ポーラ・オルビスHD傘下"
        },
        {
            "name": "RAYVIS",
            "category": "総合エステ",
            "operator": "株式会社ケンジ",
            "year": "1985年4月",
            "hq": "東京都中央区銀座1-18-2",
            "phone": "03-5524-1305",
            "inquiry": "info@rayvis.jp",
            "url": "https://www.rayvis.jp/",
            "stores": "全国展開",
            "services": "ボディ・フェイシャル・脱毛",
            "tier": "C",
            "priority": 4,
            "notes": "年商35億円"
        },
        {
            "name": "PMK",
            "category": "エステチェーン",
            "operator": "株式会社PMKメディカルラボ",
            "year": "1991年11月",
            "hq": "東京都新宿区新宿1-26-1",
            "phone": "03-5363-4421",
            "inquiry": "店舗により異なる",
            "url": "https://www.pmk-j.com/",
            "stores": "全国展開",
            "services": "痩身・フェイシャル・脱毛",
            "tier": "C",
            "priority": 4,
            "notes": "1992年創業・医療連携"
        },
        {
            "name": "ソシエ",
            "category": "エステチェーン",
            "operator": "株式会社ソシエ・ワールド",
            "year": "1960年5月",
            "hq": "東京都渋谷区代々木4-33-10",
            "phone": "03-5843-5840",
            "inquiry": "0120-413661",
            "url": "https://www.socie.jp/",
            "stores": "全国展開",
            "services": "トータルビューティー",
            "tier": "C",
            "priority": 4,
            "notes": "TBCグループが買収"
        },
        {
            "name": "ヴァン・ベール",
            "category": "エステチェーン",
            "operator": "株式会社ビ・メーク",
            "year": "2002年7月(創業1983年)",
            "hq": "山口県山口市小郡花園町5-3",
            "phone": "083-974-0588",
            "inquiry": "0120-885-042",
            "url": "https://www.van-veal.com/",
            "stores": "全国展開",
            "services": "トータルエステ",
            "tier": "C",
            "priority": 4,
            "notes": "山口本社・全国展開"
        },
        {
            "name": "シーズ・ラボ",
            "category": "メディカルエステ",
            "operator": "株式会社シーズ・ラボ",
            "year": "1995年12月",
            "hq": "東京都渋谷区千駄ヶ谷4-10-8",
            "phone": "店舗により異なる",
            "inquiry": "店舗により異なる",
            "url": "https://www.ci-z.com/",
            "stores": "25店舗",
            "services": "メディカルエステ",
            "tier": "C",
            "priority": 4,
            "notes": "ドクターシーラボ系列"
        },
        {
            "name": "ラ・パルレ",
            "category": "エステチェーン",
            "operator": "株式会社ニューアート・ヘルス＆ビューティー",
            "year": "2014年7月",
            "hq": "東京都中央区銀座1-15-2",
            "phone": "03-5579-9195",
            "inquiry": "0120-860-239",
            "url": "https://www.parler.co.jp/",
            "stores": "22店舗",
            "services": "エステティック全般",
            "tier": "C",
            "priority": 4,
            "notes": "1978年創業の老舗"
        }
    ]

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for i, c in enumerate(companies, 1):
        cursor.execute("""
            INSERT INTO companies (
                company_name, category, operating_company, established_year,
                headquarters, phone, inquiry_phone, url, store_count,
                main_services, business_status, priority, tier, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            c["name"], c["category"], c["operator"], c["year"],
            c["hq"], c["phone"], c["inquiry"], c["url"], c["stores"],
            c["services"], "営業中", c["priority"], c["tier"], c["notes"]
        ))

        company_id = cursor.lastrowid

        # 営業パイプライン初期化
        cursor.execute("""
            INSERT INTO sales_pipeline (company_id, stage, stage_date, probability, ai_agent)
            VALUES (?, 'リード', ?, 10, '@AI営業')
        """, (company_id, datetime.now().strftime('%Y-%m-%d')))

        tier_mark = "🏆" if c["tier"] == "A" else ("🎯" if c["tier"] == "B" else "📌")
        print(f"  {tier_mark} [{c['tier']}] {c['name']} ({c['stores']})")

    conn.commit()
    conn.close()
    print(f"\n✅ {len(companies)}社のインポート完了")


# ===================================
# 3. 初期タスク作成
# ===================================
def create_initial_tasks():
    print("\n" + "=" * 60)
    print("📝 Step 3: 初期タスク作成")
    print("=" * 60)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    tasks = [
        ("@AI営業", "Tier A企業アプローチメール作成", "優先度最高の5社に対するアプローチメールを作成", 1, "2026-02-12"),
        ("@AI営業", "Tier B企業アプローチメール作成", "優先度高の7社に対するアプローチメールを作成", 2, "2026-02-14"),
        ("@AI担当", "業界ニュース日次収集の自動化設定", "NewsAPIを使った自動収集スクリプトのスケジュール設定", 1, "2026-02-11"),
        ("@AIマーケティング", "プレスリリース作成", "DigiLab BeautyのAI組織システムに関するプレスリリース", 2, "2026-02-14"),
        ("@AIマーケティング", "SNSコンテンツ制作（Lovart AI活用）", "Lovart AIでSNS投稿画像を一括生成", 3, "2026-02-14"),
        ("@AI事務局", "一斉メール送信準備", "18社への一斉メール送信リストの最終確認と準備", 2, "2026-02-11"),
        ("@AI事務局", "郵送資料準備", "チラシ印刷・送付状テンプレート・封筒準備", 3, "2026-02-14"),
        ("@AI執行役員", "週次KPIレポート作成", "初回の週次KPIレポートテンプレート作成", 2, "2026-02-14"),
    ]

    for t in tasks:
        cursor.execute("""
            INSERT INTO tasks (assigned_to, title, description, priority, status, due_date)
            VALUES (?, ?, ?, ?, '未着手', ?)
        """, t)
        print(f"  ✅ [{t[0]}] {t[1]}")

    conn.commit()
    conn.close()
    print(f"\n✅ {len(tasks)}件のタスク作成完了")


# ===================================
# 4. NewsAPIテスト
# ===================================
def test_newsapi():
    print("\n" + "=" * 60)
    print("📰 Step 4: NewsAPIニュース収集テスト")
    print("=" * 60)

    keywords = ["beauty salon", "esthetic Japan", "salon M&A"]
    total = 0

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    for keyword in keywords:
        print(f"\n  🔍 キーワード: {keyword}")

        params = urllib.parse.urlencode({
            'q': keyword,
            'pageSize': 3,
            'apiKey': NEWSAPI_KEY
        })
        url = f"https://newsapi.org/v2/everything?{params}"

        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))

            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                print(f"     結果: {data.get('totalResults', 0)}件")

                for article in articles[:3]:
                    title = article.get('title', '不明')[:50]
                    source = article['source'].get('name', '不明')
                    print(f"     📄 {title}...")
                    print(f"        出典: {source}")

                    # DBに保存
                    cursor.execute("""
                        INSERT INTO intelligence_log (source, info_type, title, content, url, collected_date, is_important)
                        VALUES (?, '企業ニュース', ?, ?, ?, ?, 0)
                    """, (
                        f"NewsAPI ({source})",
                        article.get('title', ''),
                        article.get('description', ''),
                        article.get('url', ''),
                        datetime.now().strftime('%Y-%m-%d')
                    ))
                    total += 1

        except Exception as e:
            print(f"     ⚠️ エラー: {e}")

    conn.commit()
    conn.close()
    print(f"\n✅ {total}件のニュース記事をDBに保存")


# ===================================
# 5. 統計レポート
# ===================================
def show_statistics():
    print("\n" + "=" * 60)
    print("📊 Step 5: データベース統計レポート")
    print("=" * 60)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 企業数
    cursor.execute("SELECT COUNT(*) FROM companies")
    total = cursor.fetchone()[0]

    # Tier別
    cursor.execute("SELECT tier, COUNT(*) FROM companies GROUP BY tier ORDER BY tier")
    tiers = cursor.fetchall()

    # カテゴリ別
    cursor.execute("SELECT category, COUNT(*) FROM companies GROUP BY category ORDER BY COUNT(*) DESC")
    categories = cursor.fetchall()

    # タスク
    cursor.execute("SELECT assigned_to, COUNT(*) FROM tasks GROUP BY assigned_to ORDER BY COUNT(*) DESC")
    task_agents = cursor.fetchall()

    # パイプライン
    cursor.execute("SELECT stage, COUNT(*) FROM sales_pipeline GROUP BY stage")
    pipeline = cursor.fetchall()

    # ニュース
    cursor.execute("SELECT COUNT(*) FROM intelligence_log")
    news_count = cursor.fetchone()[0]

    conn.close()

    print(f"\n  🏢 登録企業数: {total}社")
    print(f"\n  📊 Tier別内訳:")
    tier_labels = {"A": "🏆 最優先", "B": "🎯 優先", "C": "📌 通常"}
    for tier, count in tiers:
        print(f"     {tier_labels.get(tier, tier)}: {count}社")

    print(f"\n  📂 カテゴリ別:")
    for cat, count in categories:
        print(f"     {cat}: {count}社")

    print(f"\n  📝 タスク（AIエージェント別）:")
    for agent, count in task_agents:
        print(f"     {agent}: {count}件")

    print(f"\n  📈 営業パイプライン:")
    for stage, count in pipeline:
        print(f"     {stage}: {count}社")

    print(f"\n  📰 収集ニュース: {news_count}件")


# ===================================
# メイン実行
# ===================================
def main():
    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║  DigiLab Beauty AI組織システム - 初期セットアップ       ║")
    print("║  Powered by Replit                                      ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"\n⏰ 実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Step 1: データベース作成
    create_database()

    # Step 2: 企業データインポート
    import_companies()

    # Step 3: 初期タスク作成
    create_initial_tasks()

    # Step 4: NewsAPIテスト
    test_newsapi()

    # Step 5: 統計レポート
    show_statistics()

    print("\n" + "=" * 60)
    print("🎉 セットアップ完了！")
    print("=" * 60)
    print(f"\n📁 データベースファイル: {DB_NAME}")
    print("\n🤖 AI組織メンバー:")
    print("   @AI執行役員 - 全体統括・KPI管理")
    print("   @AI営業     - 18社へのアプローチ開始")
    print("   @AIマーケティング - PR・SNS・Lovart AI活用")
    print("   @AI担当     - NewsAPI情報収集稼働中")
    print("   @AI事務局   - 一斉メール・郵送準備完了")
    print("\n✅ 次のステップ:")
    print("   1. Tier A企業へのアプローチメール送信")
    print("   2. Lovart AIでSNS・チラシ画像生成")
    print("   3. 日次ニュース収集の自動化")
    print("=" * 60)


if __name__ == "__main__":
    main()
