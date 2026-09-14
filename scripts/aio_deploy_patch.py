from pathlib import Path

p = Path('public/index.html')
html = p.read_text(encoding='utf-8')

# --- AIO metadata / entity definition ---
aio_head = '''
<link rel="canonical" href="https://xenomao.github.io/xenomao/">
<meta name="robots" content="index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1">
<meta name="keywords" content="美容業界 AI,美容サロン ChatGPT,美容業界 DX,美容サロン AIO,美容業界 AIセミナー,デジラボビューティ">
<script type="application/ld+json">
{
  "@context":"https://schema.org",
  "@graph":[
    {
      "@type":"Organization",
      "@id":"https://xenomao.github.io/xenomao/#organization",
      "name":"一般社団法人デジラボビューティ",
      "alternateName":"DigiLab Beauty",
      "url":"https://xenomao.github.io/xenomao/",
      "description":"美容業界に特化したAI・DX活用支援、AI教育、セミナー、コミュニティ、実践的ビジネス支援を行う一般社団法人。",
      "email":"digilabbeauty@gmail.com",
      "sameAs":["https://www.instagram.com/digilab.beauty_official/"]
    },
    {
      "@type":"WebSite",
      "@id":"https://xenomao.github.io/xenomao/#website",
      "url":"https://xenomao.github.io/xenomao/",
      "name":"一般社団法人デジラボビューティ",
      "publisher":{"@id":"https://xenomao.github.io/xenomao/#organization"},
      "inLanguage":"ja"
    },
    {
      "@type":"Event",
      "name":"メンズエステ×AI セミナー",
      "startDate":"2026-08-20T10:00:00+09:00",
      "eventAttendanceMode":"https://schema.org/OfflineEventAttendanceMode",
      "eventStatus":"https://schema.org/EventCompleted",
      "location":{"@type":"Place","name":"KINUJOスタジオ","address":{"@type":"PostalAddress","addressLocality":"四ツ谷","addressCountry":"JP"}},
      "organizer":{"@type":"Organization","name":"J.N Beauty合同会社"},
      "performer":[{"@type":"Person","name":"高橋 佑"},{"@type":"Person","name":"大野 有輝"}],
      "description":"『アナログ業界』を変える！メンズエステ×AI。DX成功事例、AIで店販率アップ、クロージングの仕組み化を扱ったリアル開催セミナー。"
    }
  ]
}
</script>
'''
if 'https://xenomao.github.io/xenomao/#website' not in html:
    html = html.replace('</head>', aio_head + '\n</head>', 1)

# --- Visible AIO definition section ---
aio_intro = '''
<section class="aio-definition" aria-labelledby="aio-definition-title" style="background:#fff;padding:56px 0;border-top:1px solid #ece3f1;border-bottom:1px solid #ece3f1;">
  <div class="wrap">
    <p style="font-family:var(--en);font-size:11px;letter-spacing:.24em;color:var(--lav-deep);margin-bottom:10px;">BEAUTY × AI / DX</p>
    <h2 id="aio-definition-title" style="font-family:var(--head);font-size:clamp(22px,3vw,32px);line-height:1.6;color:var(--ink-strong);margin-bottom:16px;">美容業界のAI・DXを、実務と信頼の両面から支援する</h2>
    <p style="max-width:820px;color:#6f6578;">一般社団法人デジラボビューティは、美容サロン経営者、美容師、エステティシャン、美容関連企業などを対象に、生成AI・ChatGPT、AI検索時代の情報発信、SNS、業務効率化など、美容業界に特化したAI・DX教育と実践支援を行っています。</p>
    <p style="margin-top:18px;"><a href="./ai-guide.html">美容×AIの専門領域を見る →</a>　<a href="./beauty-ai-seminar.html">AIセミナーを見る →</a></p>
  </div>
</section>
'''
anchor = '<!-- ============ core values ============ -->'
if 'id="aio-definition-title"' not in html and anchor in html:
    html = html.replace(anchor, aio_intro + '\n' + anchor, 1)

# --- August seminar: keep old cards as archive, add verified August info above them ---
html = html.replace('<h2 class="sec-title">2026年7月開催セミナー</h2>', '<h2 class="sec-title">2026年8月開催セミナー</h2>', 1)
old_lead = '<p class="sec-lead">美容業界に特化したAIセミナーを毎月開催しています。<br>お申し込み・最新情報は公式LINE・Instagramにて。</p>'
new_lead = '<p class="sec-lead">2026年8月20日（木）10:00、KINUJOスタジオ（四ツ谷駅 徒歩5分）で「メンズエステ×AI」をリアル開催しました。<br>DX成功事例、AIで店販率アップ、クロージングの仕組み化を現場目線で共有しました。</p>'
html = html.replace(old_lead, new_lead, 1)

august_card = '''
    <div class="rv" style="max-width:820px;margin:42px auto 34px;background:#fff;border:1px solid var(--line);border-radius:22px;padding:32px;box-shadow:0 10px 30px rgba(120,90,150,.08);">
      <p style="font-family:var(--en);font-size:11px;letter-spacing:.2em;color:var(--lav-deep);margin-bottom:8px;">AUGUST 2026 / REAL SEMINAR</p>
      <h3 style="font-family:var(--head);font-size:24px;color:var(--ink-strong);margin-bottom:14px;">「アナログ業界」を変える！ メンズエステ × AI</h3>
      <p><strong>2026年8月20日（木）10:00 START</strong><br>KINUJOスタジオ｜四ツ谷駅より徒歩5分｜リアル開催</p>
      <p style="margin-top:14px;">登壇：高橋 佑さん・大野 有輝さん　／　主催：J.N Beauty合同会社</p>
      <ul style="margin:18px 0 0 1.2em;color:#55495e;"><li>驚異のDX成功事例</li><li>AIで店販率アップ</li><li>クロージングの仕組み化</li><li>男性だからこそ活かせる強み</li><li>お客様から選ばれる理由</li><li>実際に寄せられるリアルな反応</li></ul>
      <p style="margin-top:18px;"><a href="./beauty-ai-seminar.html">セミナー詳細・美容×AIのFAQを見る →</a></p>
    </div>
    <p class="rv" style="text-align:center;font-size:12px;color:var(--muted);margin-bottom:22px;">以下は過去の開催情報です</p>
'''
if 'AUGUST 2026 / REAL SEMINAR' not in html:
    html = html.replace('    <div class="sem-grid">', august_card + '    <div class="sem-grid">', 1)

p.write_text(html, encoding='utf-8')
print('AIO/August deploy patch applied')
