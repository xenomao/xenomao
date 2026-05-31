/**
 * 自己診断（DQSミニ診断）のデータとロジック。
 * digilab-beauty-lp-demo.html の <script> を移植したもの。
 *
 * 設計メモ（HANDOFF準拠）:
 * - 悩み起点の6軸でスコアリング: [集客, リピート, 単価・指名, 時間・運営, 発信・口コミ, 数字・経営]
 * - 「AI」という言葉は表に出さない（経営ベネフィット言語で表現）
 * - スコアは112点換算。最弱軸を自動検出し、連動セミナーを提示。
 * - 計算はすべてクライアント内・サーバー送信なし（個情法配慮）。
 * - 状態は「選択した回答（picks）」の配列のみで保持し、スコアは純粋関数で都度算出する。
 */

export const AXES = [
  "集客",
  "リピート",
  "単価・指名",
  "時間・運営",
  "発信・口コミ",
  "数字・経営",
] as const;

export type QuizMode = "salon" | "pro";

export type QuizOption = {
  /** 選択肢の文言 */
  t: string;
  /** 6軸への加点（0〜4） */
  s: number[];
};

export type QuizQuestion = {
  q: string;
  opts: QuizOption[];
};

export type QuizSet = {
  label: string;
  lead: string;
  questions: QuizQuestion[];
};

export const QUIZ: Record<QuizMode, QuizSet> = {
  salon: {
    label: "サロン経営者",
    lead: "サロン経営の「いまの悩み」から、現在地を診断します。",
    questions: [
      {
        q: "新規のお客様は、安定して来ていますか？",
        opts: [
          { t: "毎月、安定して新規が来ている", s: [4, 1, 1, 0, 1, 1] },
          { t: "月によって、波が大きい", s: [2, 0, 0, 0, 1, 0] },
          { t: "正直、新規集客に悩んでいる", s: [0, 0, 0, 0, 0, 0] },
        ],
      },
      {
        q: "一度来たお客様は、また来てくれますか？",
        opts: [
          { t: "多くの方がリピートしてくれる", s: [1, 4, 2, 0, 1, 1] },
          { t: "半分くらいは続くが、離脱も多い", s: [0, 2, 1, 0, 0, 0] },
          { t: "1回きりで終わることが多い", s: [0, 0, 0, 0, 0, 0] },
        ],
      },
      {
        q: "指名や単価は、思うように伸びていますか？",
        opts: [
          { t: "指名も単価も、しっかり取れている", s: [1, 2, 4, 0, 1, 1] },
          { t: "なんとなく、価格競争になりがち", s: [0, 1, 2, 0, 0, 0] },
          { t: "安売りから抜け出せていない", s: [0, 0, 0, 0, 0, 0] },
        ],
      },
      {
        q: "日々の事務作業に、追われていませんか？",
        opts: [
          { t: "仕組み化できていて、施術に集中できる", s: [1, 1, 0, 4, 1, 2] },
          { t: "なんとか回しているが、手一杯", s: [0, 0, 0, 2, 0, 1] },
          { t: "予約・連絡・事務に振り回されている", s: [0, 0, 0, 0, 0, 0] },
        ],
      },
      {
        q: "SNSや口コミでの発信は、続いていますか？",
        opts: [
          { t: "継続でき、集客にもつながっている", s: [2, 1, 1, 0, 4, 1] },
          { t: "やってはいるが、反応が薄い", s: [1, 0, 0, 0, 2, 0] },
          { t: "何を出せばいいか分からず止まりがち", s: [0, 0, 0, 0, 0, 0] },
        ],
      },
      {
        q: "サロンの数字（売上・客数・単価）を、把握できていますか？",
        opts: [
          { t: "毎月、数字を見て手を打てている", s: [1, 1, 2, 1, 1, 4] },
          { t: "なんとなくは分かるが、感覚頼り", s: [0, 0, 1, 0, 0, 2] },
          { t: "どんぶり勘定になっている", s: [0, 0, 0, 0, 0, 0] },
        ],
      },
    ],
  },
  pro: {
    label: "個人セラピスト",
    lead: "これからの働き方の「いまの悩み」から、現在地を診断します。",
    questions: [
      {
        q: "あなたを“指名”してくれるお客様は、増えていますか？",
        opts: [
          { t: "指名のお客様が安定している", s: [4, 2, 2, 0, 1, 1] },
          { t: "少しずつだが、増えてきた", s: [2, 1, 1, 0, 1, 0] },
          { t: "なかなか指名につながらない", s: [0, 0, 0, 0, 0, 0] },
        ],
      },
      {
        q: "お客様との関係は、長く続いていますか？",
        opts: [
          { t: "長く通ってくれる方が多い", s: [1, 4, 2, 0, 1, 1] },
          { t: "続く方もいれば、離れる方も", s: [0, 2, 1, 0, 0, 0] },
          { t: "続かないことが多い", s: [0, 0, 0, 0, 0, 0] },
        ],
      },
      {
        q: "自分の施術やサービスに、自信を持って価格を付けられますか？",
        opts: [
          { t: "価値を伝え、納得して選ばれている", s: [1, 2, 4, 0, 1, 1] },
          { t: "値付けにいつも迷う", s: [0, 1, 2, 0, 0, 0] },
          { t: "安くしないと選ばれない気がする", s: [0, 0, 0, 0, 0, 0] },
        ],
      },
      {
        q: "事務・連絡・準備に、時間を取られすぎていませんか？",
        opts: [
          { t: "段取りができ、施術に集中できる", s: [1, 1, 0, 4, 1, 2] },
          { t: "なんとか回しているが大変", s: [0, 0, 0, 2, 0, 1] },
          { t: "雑務に追われて余裕がない", s: [0, 0, 0, 0, 0, 0] },
        ],
      },
      {
        q: "自分の魅力を、SNSなどで発信できていますか？",
        opts: [
          { t: "発信が、ファンや集客につながっている", s: [2, 1, 1, 0, 4, 1] },
          { t: "やってはいるが手応えがない", s: [1, 0, 0, 0, 2, 0] },
          { t: "何を出せばいいか分からない", s: [0, 0, 0, 0, 0, 0] },
        ],
      },
      {
        q: "自分の売上や顧客の状況を、数字で把握できていますか？",
        opts: [
          { t: "数字を見て、次の一手を考えられる", s: [1, 1, 2, 1, 1, 4] },
          { t: "だいたいの感覚で動いている", s: [0, 0, 1, 0, 0, 2] },
          { t: "数字はあまり見ていない", s: [0, 0, 0, 0, 0, 0] },
        ],
      },
    ],
  },
};

export type Rank = { min: number; name: string; msg: string };

export const RANKS: Rank[] = [
  {
    min: 80,
    name: "順調に回せています",
    msg: "経営の土台がしっかりしています。あとは“伸びている理由”を言葉にできれば、さらに強くなれます。",
  },
  {
    min: 55,
    name: "あと一歩で、変わります",
    msg: "悪くありません。ただ、いくつかの“もったいない穴”が見えました。そこを埋めれば景色が変わります。",
  },
  {
    min: 30,
    name: "伸びしろが、はっきり見えました",
    msg: "今が踏ん張りどき。弱点がはっきりした今こそ、正しい順番で手を打てば、流れは変えられます。",
  },
  {
    min: 0,
    name: "いまが、変えるチャンス",
    msg: "課題が多く見えるかもしれません。でも逆に、一つ学ぶだけで大きく変わる余地があるということです。",
  },
];

export type Weak = {
  /** 軸名（AXES と一致） */
  axis: string;
  /** 悩みの見出し */
  head: string;
  /** 経営ベネフィット言語 */
  ben: string;
  /** 連動セミナー名 */
  sem: string;
};

/** WEAK は AXES と同じ並び順（0:集客 … 5:数字・経営） */
export const WEAK: Weak[] = [
  {
    axis: "集客",
    head: "新しいお客様の“入口”が、足りていないかも",
    ben: "広告に頼りすぎず、自然に予約が入る集客の流れをつくるヒント",
    sem: "予約の“入口”を増やす — 安定集客の仕組みづくり",
  },
  {
    axis: "リピート",
    head: "せっかくのお客様が、1回で離れているかも",
    ben: "「また来たい」と思われ、リピートが続く仕組みをつくるヒント",
    sem: "“また来たい”を生む、リピートの仕組みづくり",
  },
  {
    axis: "単価・指名",
    head: "安売りから、抜け出せていないかも",
    ben: "価値をきちんと伝え、指名と単価を上げていく接客のヒント",
    sem: "安売りをやめる — 指名と単価を上げる伝え方",
  },
  {
    axis: "時間・運営",
    head: "雑務に時間を奪われ、余裕がないかも",
    ben: "予約・連絡・事務の手間を減らし、施術と接客に集中する時間をつくるヒント",
    sem: "1日30分の余白をつくる — 事務作業を手放す運営術",
  },
  {
    axis: "発信・口コミ",
    head: "発信が、集客につながっていないかも",
    ben: "何を・どう出せば響くのかが分かり、発信が集客に変わるヒント",
    sem: "反応が変わる — 集客につながるSNS発信のコツ",
  },
  {
    axis: "数字・経営",
    head: "“どんぶり勘定”で、判断が勘になっているかも",
    ben: "見るべき数字が分かり、感覚でなく数字で手を打てるようになるヒント",
    sem: "数字で回すサロン経営 — 見るべき数字と打ち手",
  },
];

/** 各軸の満点（その軸で取りうる最大点の合計） */
export function maxPerAxis(set: QuizSet): number[] {
  return AXES.map((_, ax) =>
    set.questions.reduce(
      (m, q) => m + Math.max(...q.opts.map((o) => o.s[ax])),
      0,
    ),
  );
}

/** 全軸合計の満点 */
export function maxTotal(set: QuizSet): number {
  return set.questions.reduce(
    (m, q) => m + Math.max(...q.opts.map((o) => o.s.reduce((a, b) => a + b, 0))),
    0,
  );
}

/** 選択履歴（picks）から6軸スコアを算出する純粋関数 */
export function scoreFromPicks(set: QuizSet, picks: number[]): number[] {
  const scores = [0, 0, 0, 0, 0, 0];
  picks.forEach((pick, qi) => {
    const opt = set.questions[qi]?.opts[pick];
    if (!opt) return;
    opt.s.forEach((v, ax) => (scores[ax] += v));
  });
  return scores;
}

export type QuizResult = {
  scores: number[];
  score112: number;
  rank: Rank;
  weakAxis: number;
  weak: Weak;
};

/** スコアから結果（112点換算・ランク・最弱軸・連動セミナー）を算出 */
export function computeResult(mode: QuizMode, scores: number[]): QuizResult {
  const set = QUIZ[mode];
  const total = maxTotal(set);
  const raw = scores.reduce((a, b) => a + b, 0);
  const score112 = total > 0 ? Math.round((raw / total) * 112) : 0;
  const pct = Math.round((score112 / 112) * 100);
  const rank = RANKS.find((r) => pct >= r.min) ?? RANKS[RANKS.length - 1];

  const mpa = maxPerAxis(set);
  let weakAxis = 0;
  let weakRatio = 2;
  scores.forEach((s, ax) => {
    const r = s / (mpa[ax] || 1);
    if (r < weakRatio) {
      weakRatio = r;
      weakAxis = ax;
    }
  });

  return { scores, score112, rank, weakAxis, weak: WEAK[weakAxis] };
}
