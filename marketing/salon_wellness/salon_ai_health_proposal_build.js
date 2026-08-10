const pptxgen = require("pptxgenjs");

// ---- Palette: Deep Ink Navy (dominant) x Vital Teal x Gold accent ----
const INK = "0B1220";
const SURFACE_D = "16233A";
const SURFACE_D2 = "1E2E49";
const TEAL = "00A896";
const TEAL_DEEP = "028090";
const GOLD = "D4A94A";
const LIGHT_BG = "F2F5F7";
const CARD_W = "FFFFFF";
const BORDER = "DCE3E9";
const TEXT_D = "0F1A2B";
const MUTED = "5A6A7D";
const ON_DARK = "FFFFFF";
const ON_DARK_MUTED = "9FB2C4";

const F = "Yu Gothic";
const FL = "Arial";

const P = new pptxgen();
P.layout = "LAYOUT_WIDE"; // 13.33 x 7.5

function logo(s, dark) {
  s.addText(
    [
      { text: "Digilab", options: { bold: true, charSpacing: 2 } },
      { text: " beauty", options: { bold: false, charSpacing: 2 } },
    ],
    { x: 0.5, y: 0.35, w: 4, h: 0.4, fontFace: FL, fontSize: 13, color: dark ? ON_DARK : TEXT_D, margin: 0 }
  );
}
function pnum(s, n, dark) {
  s.addText(String(n).padStart(2, "0"), {
    x: 12.5, y: 7.0, w: 0.6, h: 0.3, fontFace: F, fontSize: 10,
    color: dark ? "5D7186" : "9AA8B5", align: "right", margin: 0,
  });
}
function title(s, t, dark, size) {
  s.addText(t, {
    x: 0.7, y: 1.02, w: 11.9, h: 0.85, fontFace: F, fontSize: size || 28,
    bold: true, color: dark ? ON_DARK : TEXT_D, margin: 0,
  });
}
function sub(s, t, dark) {
  s.addText(t, {
    x: 0.7, y: 1.82, w: 11.6, h: 0.5, fontFace: F, fontSize: 14,
    color: dark ? ON_DARK_MUTED : MUTED, margin: 0,
  });
}
// small solid square marker + text
function item(s, x, y, w, t, opts = {}) {
  const c = opts.color || MUTED;
  const mk = opts.marker || TEAL;
  s.addShape("rect", { x, y: y + 0.11, w: 0.11, h: 0.11, fill: { color: mk }, line: { type: "none" } });
  s.addText(t, {
    x: x + 0.28, y, w: w - 0.28, h: opts.h || 0.45, fontFace: F,
    fontSize: opts.size || 13, color: c, lineSpacingMultiple: 1.25, margin: 0,
  });
}

/* ============ 1. TITLE ============ */
{
  const s = P.addSlide();
  s.background = { color: INK };
  s.addShape("ellipse", { x: 9.9, y: -2.1, w: 6.4, h: 6.4, fill: { color: TEAL_DEEP, transparency: 80 }, line: { type: "none" } });
  s.addShape("ellipse", { x: 11.5, y: 4.5, w: 3.4, h: 3.4, fill: { color: TEAL, transparency: 86 }, line: { type: "none" } });
  s.addShape("ellipse", { x: 11.15, y: 2.62, w: 0.26, h: 0.26, fill: { color: GOLD }, line: { type: "none" } });
  logo(s, true);

  s.addText("BEAUTY SALON x AI  /  PREVENTIVE HEALTH", {
    x: 0.7, y: 2.45, w: 10, h: 0.4, fontFace: FL, fontSize: 12.5, color: TEAL, bold: true, charSpacing: 3, margin: 0,
  });
  s.addText("美容サロンを、\n予防ヘルスケアの入口に。", {
    x: 0.65, y: 2.9, w: 10.5, h: 2.1, fontFace: F, fontSize: 42, bold: true,
    color: ON_DARK, lineSpacingMultiple: 1.15, margin: 0,
  });
  s.addText("カウンセリング型 美容サロン × AI ハイブリッドモデルによる新規事業のご提案", {
    x: 0.7, y: 5.05, w: 10.5, h: 0.5, fontFace: F, fontSize: 17, color: "C4D3DE", margin: 0,
  });
  s.addText("一般社団法人デジラボビューティー　|　ご提案資料　|　2026", {
    x: 0.7, y: 6.65, w: 8, h: 0.4, fontFace: F, fontSize: 11.5, color: "6E8296", margin: 0,
  });
}

/* ============ 2. 出発点：髪だけでは見えない ============ */
{
  const s = P.addSlide();
  s.background = { color: LIGHT_BG };
  logo(s, false); pnum(s, 2, false);
  title(s, "出発点 ― 髪を切るだけでは、変化は見えない");
  sub(s, "こころの変化に気づくには、髪だけでは情報が足りない。軸に置くのは「カウンセリングを行う美容サロン」。");

  // left: hair-only
  s.addShape("roundRect", { x: 0.7, y: 2.65, w: 5.8, h: 2.9, rectRadius: 0.1, fill: { color: CARD_W }, line: { color: BORDER, width: 1 } });
  s.addText("ヘアサロン中心の接点", { x: 1.05, y: 2.95, w: 5.1, h: 0.5, fontFace: F, fontSize: 17, bold: true, color: TEXT_D, margin: 0 });
  [
    "接点は主に髪と、その場かぎりの会話",
    "体調や生活習慣に踏み込む必然性が薄い",
    "記録が残らず、変化を追いかけられない",
  ].forEach((t, i) => item(s, 1.05, 3.62 + i * 0.6, 5.1, t, { color: MUTED, marker: "B9C4CE" }));

  // right: counseling salon
  s.addShape("roundRect", { x: 6.8, y: 2.65, w: 5.8, h: 2.9, rectRadius: 0.1, fill: { color: INK }, line: { type: "none" } });
  s.addText("カウンセリング型 美容サロン", { x: 7.15, y: 2.95, w: 5.1, h: 0.5, fontFace: F, fontSize: 17, bold: true, color: TEAL, margin: 0 });
  [
    "施術前カウンセリングが業務に組み込まれている",
    "肌・体調・睡眠・食事・ストレスに正面から触れる",
    "記録が残り、来店ごとに変化を追える",
  ].forEach((t, i) => item(s, 7.15, 3.62 + i * 0.6, 5.1, t, { color: "D3DEE6", marker: TEAL }));

  s.addShape("rect", { x: 0.7, y: 6.02, w: 0.14, h: 0.14, fill: { color: GOLD }, line: { type: "none" } });
  s.addText("だから軸は、カウンセリングを行う美容サロン。髪だけでは、こころの変化は見えない。", {
    x: 1.02, y: 5.88, w: 11.5, h: 0.5, fontFace: F, fontSize: 16, bold: true, color: TEXT_D, margin: 0,
  });
}

/* ============ 3. 兆し：OpenAIの動き ============ */
{
  const s = P.addSlide();
  s.background = { color: INK };
  logo(s, true); pnum(s, 3, true);
  title(s, "兆し ― AIの次の主戦場は、ヘルスになった", true);
  sub(s, "2026年、OpenAIは「ChatGPT Health」を発表。サム・アルトマン自ら医師・病院へ売り込んでいる。", true);

  s.addText("週 3億件", {
    x: 0.7, y: 2.75, w: 6, h: 1.4, fontFace: F, fontSize: 62, bold: true, color: TEAL, margin: 0,
  });
  s.addText("2026年7月時点、ChatGPTに寄せられる健康関連の質問数\n(2026年1月時点では週2.3億件)", {
    x: 0.7, y: 4.15, w: 6, h: 0.9, fontFace: F, fontSize: 13, color: ON_DARK_MUTED, lineSpacingMultiple: 1.35, margin: 0,
  });

  s.addShape("line", { x: 7.3, y: 2.75, w: 0, h: 3.5, line: { color: "36486150".slice(0, 6), width: 1 } });
  [
    "1月7日　一般ユーザー向け「ChatGPT Health」発表\n患者ポータル・Apple Health・健康アプリと連携",
    "1月8日　医療機関向け「OpenAI for Healthcare」発表\nCedars-Sinai、HCA Healthcare など大手が導入",
    "7月23日　米国の全ユーザーへ提供開始",
  ].forEach((t, i) => {
    const y = 2.75 + i * 1.2;
    s.addShape("ellipse", { x: 7.24, y: y + 0.1, w: 0.13, h: 0.13, fill: { color: TEAL }, line: { type: "none" } });
    s.addText(t, { x: 7.6, y, w: 5.0, h: 1.0, fontFace: F, fontSize: 12.5, color: ON_DARK, lineSpacingMultiple: 1.35, margin: 0 });
  });

  s.addText("出典: OpenAI 公表資料 / TechCrunch / Forbes (2026)", {
    x: 0.7, y: 6.45, w: 8, h: 0.35, fontFace: F, fontSize: 10, color: "5D7186", margin: 0,
  });
}

/* ============ 4. AIが手に入れられない3つ ============ */
{
  const s = P.addSlide();
  s.background = { color: LIGHT_BG };
  logo(s, false); pnum(s, 4, false);
  title(s, "それでもAIが、構造的に手に入れられない3つのもの");
  sub(s, "ChatGPTがどれだけ賢くなっても、この3つは自力では埋まらない。");

  [
    ["実世界の観察データ", "本人が入力しない限り、AIはその人の状態を何も知らない"],
    ["継続的な関係と信頼", "「言いにくいこと」は、関係性のある相手にしか出てこない"],
    ["行動変容を伴走する人", "正しい提案をしても、実行を支える人がいなければ続かない"],
  ].forEach(([t, d], i) => {
    const y = 2.6 + i * 1.15;
    s.addText(String(i + 1).padStart(2, "0"), {
      x: 0.7, y, w: 0.95, h: 0.6, fontFace: FL, fontSize: 24, bold: true, color: GOLD, margin: 0,
    });
    s.addText(t, { x: 1.75, y: y + 0.02, w: 4.0, h: 0.55, fontFace: F, fontSize: 17, bold: true, color: TEXT_D, margin: 0 });
    s.addText(d, { x: 5.9, y: y + 0.02, w: 6.7, h: 0.55, fontFace: F, fontSize: 13, color: MUTED, valign: "middle", margin: 0 });
  });

  s.addShape("roundRect", { x: 0.7, y: 6.15, w: 11.9, h: 0.8, rectRadius: 0.1, fill: { color: INK }, line: { type: "none" } });
  s.addText("この3つを、カウンセリング型の美容サロンはすでに持っている。", {
    x: 1.1, y: 6.15, w: 11.1, h: 0.8, fontFace: F, fontSize: 16, bold: true, color: ON_DARK, valign: "middle", margin: 0,
  });
}

/* ============ 5. 提案 + フロー ============ */
{
  const s = P.addSlide();
  s.background = { color: INK };
  logo(s, true); pnum(s, 5, true);

  s.addText("PROPOSAL", { x: 0.7, y: 1.0, w: 6, h: 0.35, fontFace: FL, fontSize: 12, bold: true, color: TEAL, charSpacing: 3, margin: 0 });
  s.addText("サロン起点の、予防ヘルスケアモデル", {
    x: 0.7, y: 1.42, w: 11.9, h: 0.9, fontFace: F, fontSize: 32, bold: true, color: ON_DARK, margin: 0,
  });
  s.addText("すでに行われているカウンセリングを、そのまま予防の入口にする。\nAIは黒子として記録を束ね、判断と声かけは常に人が行う。", {
    x: 0.7, y: 2.35, w: 11.0, h: 1.0, fontFace: F, fontSize: 15, color: "C4D3DE", lineSpacingMultiple: 1.4, margin: 0,
  });

  const boxes = [
    ["カウンセリング", "施術前の問診"],
    ["記録", "来店ごとに残す"],
    ["AI 縦断分析", "変化を検出"],
    ["示唆", "施術者へ提示"],
    ["人が伝える", "声かけ・橋渡し"],
  ];
  const bw = 2.1, gap = 0.32, sx = 0.7, by = 3.75, bh = 1.65;
  boxes.forEach((b, i) => {
    const x = sx + i * (bw + gap);
    const hot = i === 2;
    s.addShape("roundRect", { x, y: by, w: bw, h: bh, rectRadius: 0.1, fill: { color: hot ? TEAL : SURFACE_D }, line: { type: "none" } });
    s.addText(b[0], { x: x + 0.1, y: by + 0.42, w: bw - 0.2, h: 0.5, fontFace: F, fontSize: 15, bold: true, color: hot ? INK : ON_DARK, align: "center", margin: 0 });
    s.addText(b[1], { x: x + 0.1, y: by + 0.95, w: bw - 0.2, h: 0.4, fontFace: F, fontSize: 10.5, color: hot ? "05463E" : ON_DARK_MUTED, align: "center", margin: 0 });
    if (i < boxes.length - 1) {
      s.addText("→", { x: x + bw, y: by + 0.55, w: gap, h: 0.5, fontFace: F, fontSize: 18, bold: true, color: TEAL, align: "center", margin: 0 });
    }
  });

  s.addShape("rect", { x: 0.7, y: 5.85, w: 0.13, h: 0.13, fill: { color: GOLD }, line: { type: "none" } });
  s.addText("AIは記録を束ね、変化を示すだけ。診断も判断もしない。", {
    x: 1.0, y: 5.72, w: 11.5, h: 0.45, fontFace: F, fontSize: 14, color: ON_DARK, bold: true, margin: 0,
  });
}

/* ============ 6. 対象業態 ============ */
{
  const s = P.addSlide();
  s.background = { color: LIGHT_BG };
  logo(s, false); pnum(s, 6, false);
  title(s, "対象 ― カウンセリングが前提の美容サロン");
  sub(s, "ヘアサロンに限定しない。身体と生活に踏み込む業態こそ、予防の入口になる。");

  const chips = [
    "エステ・フェイシャル",
    "痩身・ボディケア",
    "脱毛",
    "ネイル",
    "アイラッシュ",
    "リラクゼーション・整体系",
  ];
  chips.forEach((c, i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.7 + col * 3.25, y = 2.65 + row * 1.15;
    s.addShape("roundRect", { x, y, w: 2.95, h: 0.88, rectRadius: 0.08, fill: { color: CARD_W }, line: { color: BORDER, width: 1 } });
    s.addShape("rect", { x: x + 0.28, y: y + 0.38, w: 0.11, h: 0.11, fill: { color: TEAL }, line: { type: "none" } });
    s.addText(c, { x: x + 0.52, y, w: 2.38, h: 0.88, fontFace: F, fontSize: 12.5, color: TEXT_D, valign: "middle", margin: 0 });
  });

  s.addShape("roundRect", { x: 7.4, y: 2.65, w: 5.2, h: 3.15, rectRadius: 0.1, fill: { color: INK }, line: { type: "none" } });
  s.addText("3つの共通点", { x: 7.75, y: 2.95, w: 4.5, h: 0.45, fontFace: F, fontSize: 16, bold: true, color: TEAL, margin: 0 });
  [
    "施術前カウンセリングが必須",
    "継続来店が前提(月1〜数ヶ月ごと)",
    "身体に直接触れている",
  ].forEach((t, i) => item(s, 7.75, 3.6 + i * 0.62, 4.5, t, { color: "D3DEE6", marker: GOLD, size: 13.5 }));

  s.addShape("rect", { x: 0.7, y: 6.18, w: 0.14, h: 0.14, fill: { color: GOLD }, line: { type: "none" } });
  s.addText("「カウンセリングシートを書く」という既存の習慣の上に載せられるため、現場の追加負担が小さい。", {
    x: 1.02, y: 6.04, w: 11.5, h: 0.5, fontFace: F, fontSize: 15, bold: true, color: TEXT_D, margin: 0,
  });
}

/* ============ 7. サロンが触れている情報 = ヘルス ============ */
{
  const s = P.addSlide();
  s.background = { color: INK };
  logo(s, true); pnum(s, 7, true);
  title(s, "サロンが日常的に触れている情報は、すでに「ヘルス」", true);
  sub(s, "こころの不調は、まず身体と生活に出る。サロンはその表面を毎回見ている。", true);

  const chips = ["肌の状態", "体調・むくみ", "睡眠", "食事・水分", "体重・体型の変化", "ストレスの自覚", "生活リズム", "表情・声のトーン"];
  chips.forEach((c, i) => {
    const col = i % 4, row = Math.floor(i / 4);
    const x = 0.7 + col * 3.03, y = 2.95 + row * 1.35;
    s.addShape("roundRect", { x, y, w: 2.8, h: 1.15, rectRadius: 0.1, fill: { color: SURFACE_D }, line: { type: "none" } });
    s.addShape("rect", { x: x + 0.3, y: y + 0.34, w: 0.11, h: 0.11, fill: { color: TEAL }, line: { type: "none" } });
    s.addText(c, { x: x + 0.3, y: y + 0.55, w: 2.2, h: 0.45, fontFace: F, fontSize: 13.5, bold: true, color: ON_DARK, margin: 0 });
  });

  s.addShape("roundRect", { x: 0.7, y: 5.85, w: 11.9, h: 0.95, rectRadius: 0.1, fill: { color: SURFACE_D2 }, line: { type: "none" } });
  s.addText("前提", { x: 1.1, y: 6.0, w: 0.9, h: 0.35, fontFace: F, fontSize: 12, bold: true, color: GOLD, margin: 0 });
  s.addText("医療行為ではなく「気づきの記録」。要配慮個人情報として、本人の同意取得と適切な管理を前提に設計する。", {
    x: 1.1, y: 6.35, w: 11.1, h: 0.4, fontFace: F, fontSize: 12.5, color: "D3DEE6", margin: 0,
  });
}

/* ============ 8. 仕組み 3層 ============ */
{
  const s = P.addSlide();
  s.background = { color: LIGHT_BG };
  logo(s, false); pnum(s, 8, false);
  title(s, "仕組み ― 3層構造");
  sub(s, "現場のオペレーションを変えずに、記録と示唆の層だけを足す。");

  const layers = [
    ["① カウンセリング支援", "施術者 向け", "ガイドライン準拠の問診項目と、会話に自然に織り込めるトークスクリプト", false],
    ["② 縦断分析エンジン", "AI", "来店ごとの記録を時系列で束ね「前回からの変化」を提示。判断と声かけは常に人が行う", true],
    ["③ つなぎのケア", "利用者 向け", "セルフケアの提示と、必要時に専門機関・産業保健へつなぐブリッジ(任意提供)", false],
  ];
  layers.forEach((l, i) => {
    const y = 2.55 + i * 1.5;
    s.addShape("roundRect", { x: 0.7, y, w: 11.9, h: 1.3, rectRadius: 0.1, fill: { color: l[3] ? INK : CARD_W }, line: l[3] ? { type: "none" } : { color: BORDER, width: 1 } });
    s.addText(l[0], { x: 1.1, y: y + 0.2, w: 3.6, h: 0.45, fontFace: F, fontSize: 16.5, bold: true, color: l[3] ? ON_DARK : TEXT_D, margin: 0 });
    s.addText(l[1], { x: 1.1, y: y + 0.68, w: 3.6, h: 0.4, fontFace: F, fontSize: 12, bold: true, color: l[3] ? TEAL : TEAL_DEEP, margin: 0 });
    s.addText(l[2], { x: 5.0, y, w: 7.3, h: 1.3, fontFace: F, fontSize: 13, color: l[3] ? "D3DEE6" : MUTED, valign: "middle", lineSpacingMultiple: 1.3, margin: 0 });
  });
}

/* ============ 9. 戦略資産（Altmanが欲しがるもの） ============ */
{
  const s = P.addSlide();
  s.background = { color: INK };
  logo(s, true); pnum(s, 9, true);
  s.addText("WHY THIS MATTERS", { x: 0.7, y: 1.0, w: 6, h: 0.35, fontFace: FL, fontSize: 12, bold: true, color: TEAL, charSpacing: 3, margin: 0 });
  s.addText("ヘルス領域の最後のピースは、「実世界」と「人」", {
    x: 0.7, y: 1.4, w: 11.9, h: 0.85, fontFace: F, fontSize: 30, bold: true, color: ON_DARK, margin: 0,
  });

  s.addShape("roundRect", { x: 0.7, y: 2.55, w: 5.8, h: 3.15, rectRadius: 0.1, fill: { color: SURFACE_D }, line: { type: "none" } });
  s.addText("OpenAIがすでに押さえたもの", { x: 1.05, y: 2.85, w: 5.1, h: 0.45, fontFace: F, fontSize: 15.5, bold: true, color: ON_DARK_MUTED, margin: 0 });
  ["電子カルテ・患者ポータルとの連携", "ウェアラブル・健康アプリのデータ", "保険・受診に関する情報", "週3億件の健康相談"].forEach((t, i) =>
    item(s, 1.05, 3.5 + i * 0.55, 5.1, t, { color: "C4D3DE", marker: "5D7186", size: 12.5 })
  );

  s.addShape("roundRect", { x: 6.8, y: 2.55, w: 5.8, h: 3.15, rectRadius: 0.1, fill: { color: TEAL }, line: { type: "none" } });
  s.addText("まだ誰も押さえていないもの", { x: 7.15, y: 2.85, w: 5.1, h: 0.45, fontFace: F, fontSize: 15.5, bold: true, color: INK, margin: 0 });
  ["対面で継続的に得られる観察データ", "同意にもとづく縦断ウェルネス記録", "行動変容を伴走する人", "世界中にすでにある物理拠点"].forEach((t, i) =>
    item(s, 7.15, 3.5 + i * 0.55, 5.1, t, { color: INK, marker: "04352F", size: 12.5 })
  );

  s.addShape("rect", { x: 0.7, y: 6.12, w: 0.14, h: 0.14, fill: { color: GOLD }, line: { type: "none" } });
  s.addText("AIが読める形の「実世界データ」と、それを実行に移す人。ここを持つ側が、次のヘルスケアの主導権を持つ。", {
    x: 1.02, y: 5.98, w: 11.5, h: 0.5, fontFace: F, fontSize: 15, bold: true, color: GOLD, margin: 0,
  });
}

/* ============ 10. エビデンス基盤 ============ */
{
  const s = P.addSlide();
  s.background = { color: LIGHT_BG };
  logo(s, false); pnum(s, 10, false);
  title(s, "エビデンス基盤 ― 自己流にしない");
  sub(s, "Minds(公益財団法人 日本医療機能評価機構)型のプロセスを踏み、社会的な信頼性を担保する。");

  const steps = [
    ["エビデンスレビュー", "既存研究やDeLiGHTプロジェクト等の知見を、系統的に収集する"],
    ["確実性の評価", "集めた知見の強さと限界を、客観的な基準で評価する"],
    ["多者による合意形成", "サロン事業者・施術者・専門家を含む協働体制で検討する"],
    ["推奨の明示・更新", "「型」として明文化し、継続的に見直す"],
  ];
  steps.forEach((st, i) => {
    const x = 0.7 + i * 3.03;
    s.addShape("roundRect", { x, y: 2.75, w: 2.8, h: 2.65, rectRadius: 0.1, fill: { color: CARD_W }, line: { color: BORDER, width: 1 } });
    s.addText(String(i + 1).padStart(2, "0"), { x: x + 0.3, y: 3.0, w: 2.2, h: 0.5, fontFace: FL, fontSize: 21, bold: true, color: GOLD, margin: 0 });
    s.addText(st[0], { x: x + 0.3, y: 3.6, w: 2.2, h: 0.6, fontFace: F, fontSize: 14, bold: true, color: TEXT_D, lineSpacingMultiple: 1.15, margin: 0 });
    s.addText(st[1], { x: x + 0.3, y: 4.3, w: 2.2, h: 1.0, fontFace: F, fontSize: 11, color: MUTED, lineSpacingMultiple: 1.3, margin: 0 });
    if (i < steps.length - 1) {
      s.addText("→", { x: x + 2.8, y: 3.9, w: 0.23, h: 0.4, fontFace: F, fontSize: 15, color: TEAL, align: "center", bold: true, margin: 0 });
    }
  });

  s.addText("Mindsは、システマティックレビューによるエビデンス総体の評価と、多職種・患者市民を含む合議で推奨を定める国内標準の方法論。\n参照: DeLiGHTプロジェクト(AMED事業/日本産業衛生学会ほか関連7学会連携)による、産業保健分野のMinds参照型ガイドライン策定モデル。", {
    x: 0.7, y: 5.75, w: 11.9, h: 0.9, fontFace: F, fontSize: 10.5, color: "7F8D9B", lineSpacingMultiple: 1.35, margin: 0,
  });
}

/* ============ 11. サロンのメリット ============ */
{
  const s = P.addSlide();
  s.background = { color: LIGHT_BG };
  logo(s, false); pnum(s, 11, false);
  title(s, "サロンにとってのメリット");

  const merits = [
    ["カウンセリングの質が上がる", "毎回の記録が蓄積され、経験や勘に頼らず変化を捉えられる"],
    ["顧客ロイヤルティの向上", "「気にかけてもらえる場所」として、通い続ける理由が増える"],
    ["対応の迷いがなくなる", "気になるお客様への声かけに、明確な指針と線引きができる"],
    ["新しい収益の入り口", "認定制度・研修を通じ、施術以外の価値提供につながる"],
  ];
  merits.forEach(([t, d], i) => {
    const col = i % 2, row = Math.floor(i / 2);
    const x = 0.7 + col * 6.1, y = 2.3 + row * 1.95;
    s.addShape("roundRect", { x, y, w: 5.8, h: 1.7, rectRadius: 0.1, fill: { color: CARD_W }, line: { color: BORDER, width: 1 } });
    s.addText(String(i + 1).padStart(2, "0"), { x: x + 0.35, y: y + 0.25, w: 0.8, h: 0.4, fontFace: FL, fontSize: 16, bold: true, color: GOLD, margin: 0 });
    s.addText(t, { x: x + 1.15, y: y + 0.22, w: 4.3, h: 0.45, fontFace: F, fontSize: 15.5, bold: true, color: TEXT_D, margin: 0 });
    s.addText(d, { x: x + 1.15, y: y + 0.78, w: 4.4, h: 0.75, fontFace: F, fontSize: 12.5, color: MUTED, lineSpacingMultiple: 1.3, margin: 0 });
  });

  s.addText("いずれも、いま行っているカウンセリングの延長線上で実現できる。", {
    x: 0.7, y: 6.35, w: 11.5, h: 0.45, fontFace: F, fontSize: 13.5, color: MUTED, margin: 0,
  });
}

/* ============ 12. ロードマップ + Ask ============ */
{
  const s = P.addSlide();
  s.background = { color: INK };
  logo(s, true); pnum(s, 12, true);
  title(s, "ロードマップと、今回のお願い", true);

  const phases = [
    ["Phase 1", "国内実証", "カウンセリング型サロン数店舗でMVPを試験導入し、効果を測定する"],
    ["Phase 2", "認定制度化", "ガイドライン準拠サロンの認定と研修プログラムを商品化する"],
    ["Phase 3", "海外展開", "各国の規制に合わせてローカライズし、業界団体との提携で型を輸出する"],
  ];
  phases.forEach((ph, i) => {
    const x = 0.7 + i * 4.05;
    const hot = i === 0;
    s.addShape("roundRect", { x, y: 2.3, w: 3.8, h: 2.0, rectRadius: 0.1, fill: { color: hot ? TEAL : SURFACE_D }, line: { type: "none" } });
    s.addText(ph[0], { x: x + 0.3, y: 2.5, w: 3.2, h: 0.35, fontFace: FL, fontSize: 12, bold: true, color: hot ? "04352F" : TEAL, charSpacing: 1, margin: 0 });
    s.addText(ph[1], { x: x + 0.3, y: 2.88, w: 3.2, h: 0.45, fontFace: F, fontSize: 17, bold: true, color: hot ? INK : ON_DARK, margin: 0 });
    s.addText(ph[2], { x: x + 0.3, y: 3.4, w: 3.2, h: 0.8, fontFace: F, fontSize: 11, color: hot ? "04352F" : ON_DARK_MUTED, lineSpacingMultiple: 1.3, margin: 0 });
  });

  s.addShape("roundRect", { x: 0.7, y: 4.7, w: 11.9, h: 2.0, rectRadius: 0.12, fill: { color: SURFACE_D2 }, line: { type: "none" } });
  s.addText("今回のお願い", { x: 1.15, y: 4.95, w: 6, h: 0.35, fontFace: F, fontSize: 12.5, bold: true, color: GOLD, margin: 0 });
  s.addText("Phase 1トライアルにご参加いただけるサロンを募集しています。", {
    x: 1.15, y: 5.32, w: 10.9, h: 0.5, fontFace: F, fontSize: 18, bold: true, color: ON_DARK, margin: 0,
  });
  s.addText("ご協力いただくこと: 施術前カウンセリング内での数分のヒアリングと、その記録\n費用: トライアル期間中は無償　/　個人情報: 本人同意にもとづき、匿名化して取り扱います", {
    x: 1.15, y: 5.85, w: 10.9, h: 0.75, fontFace: F, fontSize: 12.5, color: "C4D3DE", lineSpacingMultiple: 1.35, margin: 0,
  });
}

/* ============ 13. クロージング ============ */
{
  const s = P.addSlide();
  s.background = { color: INK };
  s.addShape("ellipse", { x: -1.8, y: 3.9, w: 6.2, h: 6.2, fill: { color: TEAL_DEEP, transparency: 82 }, line: { type: "none" } });
  s.addShape("ellipse", { x: 12.0, y: -0.9, w: 2.6, h: 2.6, fill: { color: TEAL, transparency: 86 }, line: { type: "none" } });

  s.addText("Digilab beauty", {
    x: 0.7, y: 2.5, w: 8, h: 0.7, fontFace: FL, fontSize: 26, bold: true, color: ON_DARK, charSpacing: 2, margin: 0,
  });
  s.addText("カウンセリングの現場から、予防ヘルスケアをつくる。", {
    x: 0.7, y: 3.28, w: 10.5, h: 0.6, fontFace: F, fontSize: 18, color: TEAL, margin: 0,
  });
  s.addShape("rect", { x: 0.7, y: 4.35, w: 0.14, h: 0.14, fill: { color: GOLD }, line: { type: "none" } });
  s.addText("digilabbeauty@gmail.com", {
    x: 1.02, y: 4.2, w: 8, h: 0.45, fontFace: F, fontSize: 16, bold: true, color: ON_DARK, margin: 0,
  });
  s.addText("一般社団法人デジラボビューティー", {
    x: 1.02, y: 4.72, w: 8, h: 0.4, fontFace: F, fontSize: 12, color: "8DA0B2", margin: 0,
  });
}

const path = require("path");
P.writeFile({ fileName: path.join(__dirname, "salon_ai_health_proposal.pptx") })
  .then(() => console.log("done"));
