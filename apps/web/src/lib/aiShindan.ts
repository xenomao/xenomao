/**
 * AI活用診断（AI Readiness Check）のデータとロジック。
 *
 * 位置づけ（戦略）:
 * - デジラボが策定する「美容業界AI活用ガイドライン（v0.1・策定中）」の6つの視点を
 *   そのまま自己診断の軸にする＝診断＝“ガイドライン（標準）で測る無料の入口”。
 * - 「AIを使えているか（活用度）」と「安全・適法に使えているか（信頼）」の両面で測る
 *   ＝デジラボの差別化（AI×コンプライアンス）と一致。
 *
 * 設計:
 * - 6視点 × 各2問 = 12問。各選択肢は習熟度 0〜3。
 * - スコアは100点換算。最弱視点を自動検出し、次の一歩（連動セミナー）を提示。
 * - 計算はクライアント内で完結・サーバー送信なし（個情法配慮）。
 * - 認証の合否・特定の成果を保証するものではない（景表法配慮）。
 */

export const AI_AXES = [
  "活用度",
  "法令理解",
  "透明性",
  "人の確認",
  "データ保護",
  "体制・教育",
] as const;

export type AiOption = {
  /** 選択肢の文言 */
  t: string;
  /** 習熟度スコア 0〜3 */
  v: number;
};

export type AiQuestion = {
  /** 対応する視点（AI_AXES の index） */
  axis: number;
  q: string;
  opts: AiOption[];
};

/** 6視点 × 各2問 = 12問 */
export const AI_QUESTIONS: AiQuestion[] = [
  // 0: 活用度
  {
    axis: 0,
    q: "予約対応・お問い合わせに、AI（チャットや自動応答など）をどの程度使っていますか？",
    opts: [
      { t: "まったく使っていない", v: 0 },
      { t: "一部、試している", v: 1 },
      { t: "日常的に使う場面がある", v: 2 },
      { t: "仕組みとして定着している", v: 3 },
    ],
  },
  {
    axis: 0,
    q: "SNS投稿やブログ・お礼文などの文章作成に、AIを使っていますか？",
    opts: [
      { t: "使っていない", v: 0 },
      { t: "たまに使う", v: 1 },
      { t: "よく使う", v: 2 },
      { t: "手順化して継続的に使っている", v: 3 },
    ],
  },
  // 1: 法令理解
  {
    axis: 1,
    q: "AIが作った広告・説明文を、薬機法・景品表示法の観点でチェックしていますか？",
    opts: [
      { t: "チェックするという発想がなかった", v: 0 },
      { t: "気にはするが、基準は曖昧", v: 1 },
      { t: "自分なりの基準で確認している", v: 2 },
      { t: "チェック手順が明文化されている", v: 3 },
    ],
  },
  {
    axis: 1,
    q: "「効果・効能」を断定する表現（医療類似など）のリスクを理解していますか？",
    opts: [
      { t: "知らなかった", v: 0 },
      { t: "聞いたことはある", v: 1 },
      { t: "概ね理解している", v: 2 },
      { t: "スタッフにも周知・運用している", v: 3 },
    ],
  },
  // 2: 透明性
  {
    axis: 2,
    q: "AIで作成した文章・画像であることを、必要に応じてお客様に明示していますか？",
    opts: [
      { t: "考えたことがない", v: 0 },
      { t: "ほぼ明示していない", v: 1 },
      { t: "場面によって明示する", v: 2 },
      { t: "方針として明示している", v: 3 },
    ],
  },
  {
    axis: 2,
    q: "カウンセリングで、AIの提案をそのまま伝えず、人の言葉で説明していますか？",
    opts: [
      { t: "AI任せになりがち", v: 0 },
      { t: "場合による", v: 1 },
      { t: "基本は人が説明する", v: 2 },
      { t: "必ず人が確認して説明する", v: 3 },
    ],
  },
  // 3: 人の確認（Human-in-the-loop）
  {
    axis: 3,
    q: "AIの出力を、お客様に出す前に人が確認する運用になっていますか？",
    opts: [
      { t: "確認せず使うことがある", v: 0 },
      { t: "気づいたときだけ確認", v: 1 },
      { t: "基本は確認している", v: 2 },
      { t: "必ず確認する手順がある", v: 3 },
    ],
  },
  {
    axis: 3,
    q: "「AIは間違えることがある」前提で、最終判断は人が持っていますか？",
    opts: [
      { t: "意識していない", v: 0 },
      { t: "なんとなく", v: 1 },
      { t: "概ねそうしている", v: 2 },
      { t: "明確にルール化している", v: 3 },
    ],
  },
  // 4: データ保護
  {
    axis: 4,
    q: "顧客情報をAIツールに入力する際、扱い（外部送信・保存）に配慮していますか？",
    opts: [
      { t: "気にせず入力している", v: 0 },
      { t: "少し気になっている", v: 1 },
      { t: "個人情報は入れないようにしている", v: 2 },
      { t: "取扱いルールが定まっている", v: 3 },
    ],
  },
  {
    axis: 4,
    q: "顧客データの利用について、同意を取得する仕組みがありますか？",
    opts: [
      { t: "特にない", v: 0 },
      { t: "口頭で何となく", v: 1 },
      { t: "一部は書面で取得", v: 2 },
      { t: "明確に取得・管理している", v: 3 },
    ],
  },
  // 5: 体制・教育
  {
    axis: 5,
    q: "スタッフがAIを学ぶ機会（研修・勉強会）はありますか？",
    opts: [
      { t: "ない", v: 0 },
      { t: "個人任せ", v: 1 },
      { t: "ときどき実施している", v: 2 },
      { t: "定期的に実施している", v: 3 },
    ],
  },
  {
    axis: 5,
    q: "ベテランの知識・手順を、共有・標準化できていますか？（属人化の解消）",
    opts: [
      { t: "属人化している", v: 0 },
      { t: "一部だけ共有", v: 1 },
      { t: "概ね共有できている", v: 2 },
      { t: "仕組みとして標準化している", v: 3 },
    ],
  },
];

export type AiLevel = {
  /** この%以上で該当（降順に並べる） */
  min: number;
  tier: string;
  name: string;
  msg: string;
};

export const AI_LEVELS: AiLevel[] = [
  {
    min: 85,
    tier: "LEVEL 4",
    name: "先進 — モデルサロン水準",
    msg: "活用も、安全性も高い水準です。あとはその取り組みを“見える化”すれば、選ばれる理由として発信できます。",
  },
  {
    min: 65,
    tier: "LEVEL 3",
    name: "実践 — 仕組み化が進む",
    msg: "AIが業務に根づきつつあります。弱い視点を1つ補えば、運用の質がもう一段上がります。",
  },
  {
    min: 40,
    tier: "LEVEL 2",
    name: "取り組み中 — 部分活用",
    msg: "良いスタートです。ただ、安全に使う土台にいくつか“穴”が見えました。そこを埋めると安心して広げられます。",
  },
  {
    min: 0,
    tier: "LEVEL 1",
    name: "これから — 基礎づくり",
    msg: "今がはじめどき。正しい順番で土台をつくれば、AIは“人を置き換える”のではなく“負担を減らす”味方になります。",
  },
];

export type AiReco = {
  /** 視点名（AI_AXES と一致） */
  axis: string;
  head: string;
  step: string;
  seminar: string;
};

/** AI_RECO は AI_AXES と同じ並び順 */
export const AI_RECO: AiReco[] = [
  {
    axis: "活用度",
    head: "まだAIの“使いどころ”が、見えていないかも",
    step: "予約・発信・事務など、まず1つの業務から小さく試すと、効果を実感しやすくなります",
    seminar: "はじめてのAI活用 — まず1業務から始めるサロンの第一歩",
  },
  {
    axis: "法令理解",
    head: "AIの文章が、知らないうちに“危ない表現”になっているかも",
    step: "薬機法・景表法を踏まえてAIの出力をチェックする型を持つと、安心して発信できます",
    seminar: "薬機法・景表法に強くなる — AI表現チェックの作法",
  },
  {
    axis: "透明性",
    head: "「AIで作った」ことを、正しく伝えられているか不安かも",
    step: "AI生成物の明示と、人の言葉での説明をルール化すると、お客様の信頼が積み上がります",
    seminar: "“AIだと正しく伝える” — 誠実な情報開示の作法",
  },
  {
    axis: "人の確認",
    head: "AI任せになり、最終チェックが抜けているかも",
    step: "お客様に出す前に人が確認する手順（Human-in-the-loop）を決めると、事故を防げます",
    seminar: "AI任せにしない運用設計 — 人が最終判断を持つ仕組み",
  },
  {
    axis: "データ保護",
    head: "顧客情報の扱いに、ヒヤリとする場面があるかも",
    step: "AIに入れてよい情報の線引きと、同意取得の仕組みを整えると、守りが固まります",
    seminar: "顧客データを守るAIの使い方 — 個人情報の基本",
  },
  {
    axis: "体制・教育",
    head: "属人化したまま、スタッフ間に差が出ているかも",
    step: "ベテランの知識をAIで共有・標準化し、学ぶ機会を定例化すると、店全体の底上げになります",
    seminar: "属人化を解く — AIマニュアル化とスタッフ教育",
  },
];

/** 各視点の満点（その視点の問題数 × 3） */
export function maxPerAiAxis(): number[] {
  const max = AI_AXES.map(() => 0);
  AI_QUESTIONS.forEach((q) => {
    max[q.axis] += 3;
  });
  return max;
}

/** 選択履歴（picks）から視点別スコアを算出 */
export function aiAxisScores(picks: number[]): number[] {
  const scores = AI_AXES.map(() => 0);
  picks.forEach((pick, qi) => {
    const question = AI_QUESTIONS[qi];
    const opt = question?.opts[pick];
    if (!opt) return;
    scores[question.axis] += opt.v;
  });
  return scores;
}

export type AiResult = {
  axisScores: number[];
  max: number[];
  score100: number;
  level: AiLevel;
  weakAxis: number;
  reco: AiReco;
};

/** スコアから結果（100点換算・レベル・最弱視点・次の一歩）を算出 */
export function computeAiResult(picks: number[]): AiResult {
  const axisScores = aiAxisScores(picks);
  const max = maxPerAiAxis();
  const raw = axisScores.reduce((a, b) => a + b, 0);
  const total = max.reduce((a, b) => a + b, 0);
  const score100 = total > 0 ? Math.round((raw / total) * 100) : 0;
  const level = AI_LEVELS.find((l) => score100 >= l.min) ?? AI_LEVELS[AI_LEVELS.length - 1];

  let weakAxis = 0;
  let weakRatio = 2;
  axisScores.forEach((s, ax) => {
    const r = s / (max[ax] || 1);
    if (r < weakRatio) {
      weakRatio = r;
      weakAxis = ax;
    }
  });

  return { axisScores, max, score100, level, weakAxis, reco: AI_RECO[weakAxis] };
}
