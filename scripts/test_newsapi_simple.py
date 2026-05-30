#!/usr/bin/env python3
"""
NewsAPI 簡易テストスクリプト（標準ライブラリのみ使用）
APIキーが正しく動作するかテストします
"""

import os
import urllib.request
import urllib.parse
import json

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv が無くても環境変数があれば動く
    pass

# APIキーは .env から読み込む（コードに直書きしない）
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")

def test_newsapi_simple():
    """NewsAPI接続テスト（標準ライブラリのみ）"""
    print("=" * 70)
    print("NewsAPI 接続テスト（標準ライブラリ版）")
    print("=" * 70)

    # APIキーの確認
    if not NEWSAPI_KEY:
        print("❌ NEWSAPI_KEY が未設定です。.env に NEWSAPI_KEY を設定してください。")
        print("   （.env.example を参考にしてください）")
        print("=" * 70)
        return False
    print(f"✓ APIキー: {NEWSAPI_KEY[:8]}...{NEWSAPI_KEY[-4:]}")
    
    # テストリクエスト
    base_url = "https://newsapi.org/v2/everything"
    params = {
        'q': 'エステ OR 美容サロン',
        'language': 'ja',
        'pageSize': 5,
        'apiKey': NEWSAPI_KEY
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    print("\n🔍 テスト検索: 'エステ OR 美容サロン'")
    print("送信中...")
    
    try:
        # リクエスト送信
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        if data.get('status') == 'ok':
            print(f"\n✅ API接続成功!")
            print(f"📊 検索結果: {data.get('totalResults', 0)}件")
            
            articles = data.get('articles', [])
            if articles:
                print(f"\n📰 最新ニュース（上位5件）:")
                for i, article in enumerate(articles[:5], 1):
                    print(f"\n{i}. {article['title']}")
                    print(f"   出典: {article['source']['name']}")
                    print(f"   URL: {article['url'][:60]}...")
                    published = article['publishedAt'][:10]
                    print(f"   公開日: {published}")
            
            print("\n" + "=" * 70)
            print("✓ テスト完了 - NewsAPIは正常に動作しています！")
            print("\n次のステップ:")
            print("  1. データベースを初期化（init_database.py）")
            print("  2. daily_news_collection.py でニュース収集開始")
            print("  3. 毎日自動実行するようにスケジュール設定")
            print("=" * 70)
            return True
        else:
            print(f"\n❌ APIエラー: {data.get('message', '不明なエラー')}")
            if data.get('code') == 'apiKeyInvalid':
                print("   → APIキーが無効です。再確認してください。")
            print("=" * 70)
            return False
            
    except urllib.error.HTTPError as e:
        print(f"\n❌ HTTPエラー: {e.code} - {e.reason}")
        if e.code == 401:
            print("   → 認証エラー。APIキーを確認してください。")
        print("=" * 70)
        return False
    except Exception as e:
        print(f"\n❌ エラー: {e}")
        print("=" * 70)
        return False

if __name__ == "__main__":
    test_newsapi_simple()
