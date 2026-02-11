#!/usr/bin/env python3
"""
@AI担当 - 日次情報収集スクリプト
エステ業界のニュースを自動収集し、データベースに保存

必要なパッケージ:
pip install requests python-dotenv

環境変数(.env):
NEWSAPI_KEY=your_key_here
DB_PATH=path/to/database.db
"""

import os
import requests
import sqlite3
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# 設定
NEWSAPI_KEY = os.getenv('NEWSAPI_KEY', 'YOUR_NEWSAPI_KEY_HERE')
DB_PATH = os.getenv('DB_PATH', r'C:\Users\pline\.gemini\antigravity\scratch\digilab_beauty.db')

# 検索キーワード
KEYWORDS = [
    "エステ",
    "美容サロン",
    "脱毛サロン",
    "エステティックTBC",
    "ジェイエステティック",
    "たかの友梨",
    "スリムビューティハウス",
    "ミスパリ",
    "エステ AND 倒産",
    "エステ AND M&A",
    "エステ AND 新規出店"
]

# 企業名マッピング（タイトルから企業IDを判定）
COMPANY_MAPPING = {
    'TBC': 1,
    'ジェイエステ': 2,
    'たかの友梨': 3,
    'スリムビューティハウス': 4,
    'ミスパリ': 5
}


def collect_news_from_newsapi(keyword, days_back=3):
    """
    NewsAPIからニュースを収集
    
    Args:
        keyword: 検索キーワード
        days_back: 何日前までのニュースを取得するか
        
    Returns:
        list: 記事データのリスト
    """
    url = "https://newsapi.org/v2/everything"
    
    # 検索期間
    from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    params = {
        'q': keyword,
        'language': 'ja',
        'from': from_date,
        'sortBy': 'publishedAt',
        'pageSize': 20,
        'apiKey': NEWSAPI_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        articles = []
        if data.get('status') == 'ok':
            for article in data.get('articles', []):
                articles.append({
                    'source': f"NewsAPI ({article['source']['name']})",
                    'title': article['title'],
                    'content': article.get('description', ''),
                    'url': article['url'],
                    'published_at': article['publishedAt']
                })
        
        return articles
    
    except requests.exceptions.RequestException as e:
        print(f"  ⚠ APIエラー: {e}")
        return []


def identify_company(title):
    """
    タイトルから企業IDを判定
    
    Args:
        title: 記事タイトル
        
    Returns:
        int or None: 企業ID
    """
    for keyword, company_id in COMPANY_MAPPING.items():
        if keyword in title:
            return company_id
    return None


def classify_info_type(title, content):
    """
    情報種別を分類
    
    Args:
        title: 記事タイトル
        content: 記事内容
        
    Returns:
        tuple: (情報種別, 重要度フラグ)
    """
    text = f"{title} {content}"
    
    if '倒産' in text or '破産' in text or '廃業' in text:
        return '倒産情報', True
    elif 'M&A' in text or '買収' in text or '子会社化' in text:
        return 'M&A情報', True
    elif '出店' in text or '開店' in text or 'オープン' in text:
        return '出店情報', False
    elif '閉店' in text or '撤退' in text:
        return '閉店情報', True
    elif '人事異動' in text or '社長交代' in text:
        return '人事異動', False
    elif '決算' in text or '業績' in text:
        return '財務情報', False
    else:
        return '企業ニュース', False


def save_to_database(company_id, article, info_type, is_important):
    """
    データベースに保存
    
    Args:
        company_id: 企業ID（None可）
        article: 記事データ
        info_type: 情報種別
        is_important: 重要度フラグ
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 重複チェック
        cursor.execute("""
            SELECT COUNT(*) FROM intelligence_log
            WHERE url = ? AND collected_date = ?
        """, (article['url'], datetime.now().strftime('%Y-%m-%d')))
        
        if cursor.fetchone()[0] == 0:
            # 新規登録
            cursor.execute("""
                INSERT INTO intelligence_log (
                    company_id, source, info_type, title, content, url,
                    collected_date, ai_agent, is_important
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                company_id,
                article['source'],
                info_type,
                article['title'],
                article['content'],
                article['url'],
                datetime.now().strftime('%Y-%m-%d'),
                '@AI担当',
                1 if is_important else 0
            ))
            conn.commit()
            return True
        
        conn.close()
        return False
        
    except sqlite3.Error as e:
        print(f"  ⚠ データベースエラー: {e}")
        return False


def main():
    """メイン処理"""
    print("=" * 70)
    print("@AI担当 - 日次エステ業界ニュース収集")
    print(f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    total_collected = 0
    total_saved = 0
    important_news = []
    
    for i, keyword in enumerate(KEYWORDS, 1):
        print(f"\n[{i}/{len(KEYWORDS)}] キーワード: {keyword}")
        
        articles = collect_news_from_newsapi(keyword)
        print(f"  収集: {len(articles)}件")
        
        saved_count = 0
        for article in articles:
            company_id = identify_company(article['title'])
            info_type, is_important = classify_info_type(article['title'], article['content'])
            
            if save_to_database(company_id, article, info_type, is_important):
                saved_count += 1
                total_saved += 1
                
                if is_important:
                    important_news.append({
                        'title': article['title'],
                        'info_type': info_type,
                        'url': article['url']
                    })
        
        print(f"  保存: {saved_count}件（重複除外済み）")
        total_collected += len(articles)
    
    print("\n" + "=" * 70)
    print(f"📊 収集サマリー")
    print(f"  総収集件数: {total_collected}件")
    print(f"  新規保存件数: {total_saved}件")
    print(f"  重要ニュース: {len(important_news)}件")
    
    if important_news:
        print("\n⚠️  重要ニュース:")
        for news in important_news[:5]:  # 最大5件表示
            print(f"  - [{news['info_type']}] {news['title']}")
            print(f"    {news['url']}")
    
    print("=" * 70)
    print("✓ @AI担当 - 日次情報収集完了")
    print("=" * 70)


if __name__ == "__main__":
    main()
