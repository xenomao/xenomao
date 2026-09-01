# -*- coding: utf-8 -*-
"""認証マーク(AIセーフサロン / ビューティAIトラスト)を生成する。

使い方: リポジトリのルートで `python3 scripts/generate_certification_marks.py`
  → marketing/assets/certification/ に3配色のSVGを出力する。
パレット: navy(正) / spectrum(ダーク) / light(白地)
中央アイコン: node(ノードグラフ・現行) / iris(同心円のアイリス) / mono(AIモノグラム)
PNGは出力したSVGをブラウザで1000pxで開いて書き出す(背景透過)。
"""

def icon_svg(kind, grad, cy, pal):
    """中央アイコン: node(ノードグラフ) / iris(同心円のアイリス) / mono(AIモノグラム)"""
    if kind == 'node':
        if grad.startswith('sg'):
            lines = 'M100 113 L79 100 M100 113 L121 100 M100 113 L85 132 M100 113 L115 132 M79 100 L121 100 M85 132 L115 132'
            dots = '<circle cx="79" cy="100" r="3.6"/><circle cx="121" cy="100" r="3.6"/><circle cx="85" cy="132" r="3.6"/><circle cx="115" cy="132" r="3.6"/>'
        else:
            lines = 'M100 114 L100 93 M100 114 L77 127 M100 114 L123 127 M100 93 L77 127 M100 93 L123 127 M77 127 L123 127'
            dots = '<circle cx="100" cy="93" r="4"/><circle cx="77" cy="127" r="4"/><circle cx="123" cy="127" r="4"/>'
        return (f'<g stroke="url(#{grad})" stroke-width="1.5" opacity=".85" fill="none"><path d="{lines}"/></g>'
                f'<g fill="url(#{grad})">{dots}</g>'
                f'<circle cx="100" cy="{cy}" r="13" fill="none" stroke="url(#{grad})" stroke-width="0.9" opacity=".45"/>'
                f'<circle cx="100" cy="{cy}" r="7" fill="url(#{grad})"/>')
    if kind == 'iris':
        r_out, r_mid, r_in, r_core = (27, 21, 13.5, 6.4) if grad.startswith('sg') else (24, 19, 12, 5.8)
        fibers = ''.join(
            f'<line x1="{100+r_in*__import__("math").cos(__import__("math").radians(a)):.2f}" '
            f'y1="{cy+r_in*__import__("math").sin(__import__("math").radians(a)):.2f}" '
            f'x2="{100+r_mid*__import__("math").cos(__import__("math").radians(a)):.2f}" '
            f'y2="{cy+r_mid*__import__("math").sin(__import__("math").radians(a)):.2f}"/>'
            for a in range(0, 360, 30))
        return (f'<circle cx="100" cy="{cy}" r="{r_out}" fill="none" stroke="url(#{grad})" stroke-width="1" opacity=".38"/>'
                f'<circle cx="100" cy="{cy}" r="{r_mid}" fill="none" stroke="url(#{grad})" stroke-width="1.6" opacity=".62"/>'
                f'<g stroke="url(#{grad})" stroke-width="1" opacity=".45">{fibers}</g>'
                f'<circle cx="100" cy="{cy}" r="{r_in}" fill="none" stroke="url(#{grad})" stroke-width="2.6"/>'
                f'<circle cx="100" cy="{cy}" r="{r_core}" fill="url(#{grad})"/>')
    if kind == 'mono':
        return (f'<circle cx="100" cy="{cy}" r="25" fill="none" stroke="url(#{grad})" stroke-width="1" opacity=".45"/>'
                f'<text x="100.8" y="{cy+10.5}" font-family="Poppins,sans-serif" font-size="31" font-weight="600" '
                f'letter-spacing="1.5" fill="url(#{grad})" text-anchor="middle">AI</text>')
    raise ValueError(kind)

def salon(pal, sid, icon="node"):
    icon_markup_s = icon_svg(icon, f'sg{sid}', 113, pal)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200" role="img" aria-label="AIセーフサロン認証マーク">
<title>AIセーフサロン認証マーク({pal["label"]})</title>
<desc>一般社団法人デジラボビュティ ビューティAI認証制度 / 事業所認証</desc>
<defs>
  <linearGradient id="sg{sid}" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{pal['a']}"/><stop offset=".5" stop-color="{pal['b']}"/><stop offset="1" stop-color="{pal['c']}"/>
  </linearGradient>
  <radialGradient id="sd{sid}" cx=".5" cy=".36" r=".78">
    <stop offset="0" stop-color="{pal['bg1']}"/><stop offset="1" stop-color="{pal['bg2']}"/>
  </radialGradient>
  <path id="stop{sid}" d="M 22 100 A 78 78 0 0 1 178 100" fill="none"/>
  <path id="sbot{sid}" d="M 26.5 100 A 73.5 73.5 0 0 0 173.5 100" fill="none"/>
</defs>
<circle cx="100" cy="100" r="96" fill="url(#sd{sid})"/>
<circle cx="100" cy="100" r="96" fill="none" stroke="url(#sg{sid})" stroke-width="2.6"/>
<circle cx="100" cy="100" r="87" fill="none" stroke="url(#sg{sid})" stroke-width="0.9" opacity=".65"/>
<text font-family="Poppins,'Noto Sans JP',sans-serif" font-size="12.4" font-weight="600" letter-spacing="2.6" fill="{pal['ring1']}">
  <textPath href="#stop{sid}" startOffset="50%" text-anchor="middle">AI SAFE SALON CERTIFIED</textPath>
</text>
<text font-family="Poppins,'Noto Sans JP',sans-serif" font-size="8.4" font-weight="500" letter-spacing="3.1" fill="{pal['ring2']}">
  <textPath href="#sbot{sid}" startOffset="50%" text-anchor="middle">DIGILAB BEAUTY</textPath>
</text>
<circle cx="12.5" cy="100" r="2.6" fill="{pal['b']}"/>
<circle cx="187.5" cy="100" r="2.6" fill="{pal['b']}"/>
<circle cx="100" cy="100" r="68" fill="none" stroke="{pal['b']}" stroke-width="0.8" opacity=".3"/>
<path d="M100 44 L138 60 V96 C138 124 121 142 100 152 C79 142 62 124 62 96 V60 Z" fill="{pal['shield']}" stroke="url(#sg{sid})" stroke-width="2"/>
<text x="100" y="84" font-family="Poppins,sans-serif" font-size="12.5" font-weight="600" letter-spacing="3.6" fill="{pal['t1']}" text-anchor="middle">SAFE</text>
{icon_markup_s}
</svg>
'''

def trust(pal, sid, icon="node"):
    icon_markup_t = icon_svg(icon, f'tg{sid}', 108, pal)
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200" role="img" aria-label="ビューティAIトラストマーク">
<title>ビューティAIトラストマーク({pal["label"]})</title>
<desc>一般社団法人デジラボビュティ ビューティAI認証制度 / 美容向けAIツールの第三者認証</desc>
<defs>
  <linearGradient id="tg{sid}" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{pal['a']}"/><stop offset=".5" stop-color="{pal['b']}"/><stop offset="1" stop-color="{pal['c']}"/>
  </linearGradient>
  <radialGradient id="td{sid}" cx=".5" cy=".36" r=".78">
    <stop offset="0" stop-color="{pal['bg1']}"/><stop offset="1" stop-color="{pal['bg2']}"/>
  </radialGradient>
  <path id="ttop{sid}" d="M 22 100 A 78 78 0 0 1 178 100" fill="none"/>
  <path id="tbot{sid}" d="M 26.5 100 A 73.5 73.5 0 0 0 173.5 100" fill="none"/>
</defs>
<circle cx="100" cy="100" r="96" fill="url(#td{sid})"/>
<circle cx="100" cy="100" r="96" fill="none" stroke="url(#tg{sid})" stroke-width="2.6"/>
<circle cx="100" cy="100" r="87" fill="none" stroke="url(#tg{sid})" stroke-width="1" opacity=".55"/>
<text font-family="Poppins,'Noto Sans JP',sans-serif" font-size="12.4" font-weight="600" letter-spacing="2.5" fill="{pal['ring1']}">
  <textPath href="#ttop{sid}" startOffset="50%" text-anchor="middle">BEAUTY AI TRUST MARK</textPath>
</text>
<text font-family="Poppins,'Noto Sans JP',sans-serif" font-size="8.4" font-weight="500" letter-spacing="3.1" fill="{pal['ring2']}">
  <textPath href="#tbot{sid}" startOffset="50%" text-anchor="middle">DIGILAB BEAUTY</textPath>
</text>
<circle cx="12.5" cy="100" r="2.6" fill="{pal['b']}"/>
<circle cx="187.5" cy="100" r="2.6" fill="{pal['b']}"/>
<path d="M100 44 L141 68 V116 L100 140 L59 116 V68 Z" fill="{pal['shield']}" stroke="url(#tg{sid})" stroke-width="2"/>
<path d="M100 55 L131 73 V111 L100 129 L69 111 V73 Z" fill="none" stroke="{pal['b']}" stroke-width="0.9" opacity=".5"/>
<text x="100" y="84" font-family="Poppins,sans-serif" font-size="11.5" font-weight="600" letter-spacing="3.4" fill="{pal['t1']}" text-anchor="middle">TRUST</text>
{icon_markup_t}
</svg>
'''

PALETTES={
 # AIらしいスペクトラム(ダーク): インクブラック × アクア→シアン→バイオレット
 'spectrum':dict(label='スペクトラム', a='#5eead4', b='#38bdf8', c='#a78bfa',
   bg1='#1a1436', bg2='#080a14', ring1='#a5f3ec', ring2='#7dd3fc',
   shield='rgba(94,234,212,.09)', t1='#f2fbff'),
 # ライト(白背景・印刷/店頭用)
 'light':dict(label='ライト', a='#0ea5a4', b='#2f7df6', c='#8b5cf6',
   bg1='#ffffff', bg2='#eef3fb', ring1='#16305f', ring2='#2a5687',
   shield='rgba(47,125,246,.08)', t1='#111a33'),
}

NAVY=dict(label='ネイビー', a='#f0dca0', b='#c9a24e', c='#9a7526',
          bg1='#2a3363', bg2='#141834', ring1='#e6cd8f', ring2='#c9a24e',
          shield='rgba(230,205,143,.07)', t1='#f2ead4')
PALETTES={'navy':NAVY, **PALETTES}

if __name__=='__main__':
    import sys
    icon = sys.argv[1] if len(sys.argv)>1 else 'node'
    base='marketing/assets/certification/'
    for key,pal in PALETTES.items():
        sid=key[:2]
        suffix='' if key=='navy' else f'_{key}'
        open(f'{base}mark_ai_safe_salon{suffix}.svg','w',encoding='utf-8').write(salon(pal,sid,icon))
        open(f'{base}mark_beauty_ai_trust{suffix}.svg','w',encoding='utf-8').write(trust(pal,sid,icon))
        print('wrote', key, icon)
