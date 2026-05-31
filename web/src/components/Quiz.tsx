"use client";

import { useState } from "react";
import {
  AXES,
  QUIZ,
  computeResult,
  maxPerAxis,
  scoreFromPicks,
  type QuizMode,
  type QuizSet,
} from "@/lib/quiz";
import LineButton from "./LineButton";

/** 立場の選択（診断のスタート画面） */
function RoleSelect({ onChoose }: { onChoose: (m: QuizMode) => void }) {
  return (
    <div className="pick">
      <button onClick={() => onChoose("salon")}>
        サロン経営者として診断
        <span className="o-sub">集客・リピート・売上の現在地をチェック</span>
      </button>
      <button onClick={() => onChoose("pro")}>
        個人セラピストとして診断
        <span className="o-sub">指名・単価・働き方の現在地をチェック</span>
      </button>
    </div>
  );
}

/** 設問1問の表示 */
function Question({
  set,
  qIdx,
  onAnswer,
  onBack,
  backLabel,
}: {
  set: QuizSet;
  qIdx: number;
  onAnswer: (i: number) => void;
  onBack: () => void;
  backLabel: string;
}) {
  const q = set.questions[qIdx];
  return (
    <>
      <div className="q-head">
        Q{qIdx + 1} / {set.questions.length}
      </div>
      <div className="q-text">{q.q}</div>
      <div className="pick">
        {q.opts.map((o, i) => (
          <button key={i} className="opt" onClick={() => onAnswer(i)}>
            {o.t}
          </button>
        ))}
      </div>
      <button className="back" onClick={onBack}>
        {backLabel}
      </button>
    </>
  );
}

/** 6軸レーダーチャート（軽量SVGを自前描画・外部ライブラリ不要） */
function RadarChart({ set, scores }: { set: QuizSet; scores: number[] }) {
  const maxPer = maxPerAxis(set);
  const cx = 150;
  const cy = 140;
  const R = 104;
  const N = 6;
  const pt = (ax: number, r: number) => {
    const a = -Math.PI / 2 + (ax * 2 * Math.PI) / N;
    return [cx + r * Math.cos(a), cy + r * Math.sin(a)] as const;
  };

  const grid = [0.25, 0.5, 0.75, 1].map((f, gi) => {
    let p = "";
    for (let i = 0; i < N; i++) {
      const [x, y] = pt(i, R * f);
      p += (i ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1);
    }
    return <path key={gi} d={`${p}Z`} fill="none" stroke="#E7DEF0" strokeWidth="1" />;
  });

  const axesL = [];
  for (let i = 0; i < N; i++) {
    const [x, y] = pt(i, R);
    axesL.push(
      <line
        key={i}
        x1={cx}
        y1={cy}
        x2={Number(x.toFixed(1))}
        y2={Number(y.toFixed(1))}
        stroke="#E7DEF0"
        strokeWidth="1"
      />,
    );
  }

  let poly = "";
  for (let i = 0; i < N; i++) {
    const r = R * Math.min(1, scores[i] / (maxPer[i] || 1));
    const [x, y] = pt(i, r);
    poly += (i ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1);
  }

  const labels = [];
  for (let i = 0; i < N; i++) {
    const [x, y] = pt(i, R + 16);
    labels.push(
      <text
        key={i}
        x={Number(x.toFixed(1))}
        y={Number(y.toFixed(1))}
        fontSize="9"
        fill="#6E6781"
        textAnchor="middle"
        dominantBaseline="middle"
        fontFamily="Shippori Mincho"
      >
        {AXES[i]}
      </text>,
    );
  }

  return (
    <svg viewBox="0 0 300 290">
      <defs>
        <linearGradient id="rg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#5B8DF0" />
          <stop offset="100%" stopColor="#F0467A" />
        </linearGradient>
      </defs>
      {grid}
      {axesL}
      <path d={`${poly}Z`} fill="url(#rg)" fillOpacity="0.22" stroke="url(#rg)" strokeWidth="2" />
      {labels}
    </svg>
  );
}

/** 診断結果（112点換算・ランク・最弱軸・連動セミナー） */
function Result({
  mode,
  picks,
  onRestart,
}: {
  mode: QuizMode;
  picks: number[];
  onRestart: () => void;
}) {
  const set = QUIZ[mode];
  const scores = scoreFromPicks(set, picks);
  const { score112, rank, weak } = computeResult(mode, scores);

  return (
    <div className="result">
      <div className="score-big">
        {score112}
        <span
          style={{
            fontSize: "1.4rem",
            color: "var(--ink-soft)",
            WebkitTextFillColor: "var(--ink-soft)",
          }}
        >
          {" "}
          / 112
        </span>
      </div>
      <div className="score-cap">いまのあなたのスコア</div>
      <div className="rank-badge">{rank.name}</div>
      <div className="radar-wrap">
        <RadarChart set={set} scores={scores} />
      </div>
      <p className="msg">{rank.msg}</p>

      <div className="weak">
        <div className="weak-tag">いちばんの伸びしろ</div>
        <div className="weak-head">{weak.head}</div>
        <div className="weak-ben">{weak.ben}が、いま必要かもしれません。</div>
      </div>

      <div className="offer">
        <div className="offer-ey">Recommended for You</div>
        <div className="offer-h">
          あなたの伸びしろ「<span className="grad">{weak.axis}</span>」に
          <br />
          ぴったりの次回セミナー
        </div>
        <div className="next" style={{ boxShadow: "none", marginTop: 8, padding: "18px 18px" }}>
          <span className="nx-tag">Coming Next</span>
          <div className="nx-title" style={{ fontSize: "1.08rem" }}>
            {weak.sem}
          </div>
          <div className="nx-meta" style={{ marginBottom: 0 }}>
            <b>日時</b>　2026年6月21日（土）20:00–21:00
            <br />
            <b>形式</b>　オンライン（アーカイブ視聴あり）
          </div>
        </div>
        <p className="offer-p" style={{ marginTop: 14 }}>
          サロン経営のための学びの会。集客・リピート・お客様満足を高めるヒントを、月2回のオンラインセミナーで。「これ、うちでもできそう」を、毎月ひとつずつ。
        </p>
        <div className="offer-price">
          <b>1,000</b>
          <span className="yen">円</span>
          <span className="per">/ 月（税込・いつでも退会できます）</span>
        </div>
        <LineButton style={{ marginTop: 10 }} />
        <p className="line-sub">まずは初回セミナーに無料でご招待します。</p>
      </div>

      <button className="back" onClick={onRestart} style={{ display: "block", margin: "20px auto 0" }}>
        ↺ もう一度診断する
      </button>
      <p className="disc">
        ※本診断は自分の現在地を知るための簡易版で、認証の合否や水準、特定の成果を保証・約束するものではありません。診断回答はこの場の表示のみに使用し、サーバーには送信・保存していません。
      </p>
    </div>
  );
}

/**
 * 自己診断（DQSミニ診断）本体。
 * 状態は mode（立場）と picks（回答履歴）のみ。スコアは純粋関数で都度算出。
 * localStorage は使わず、ページ内のみで完結する。
 */
export default function Quiz() {
  const [mode, setMode] = useState<QuizMode | null>(null);
  const [picks, setPicks] = useState<number[]>([]);

  const set = mode ? QUIZ[mode] : null;
  const qIdx = picks.length;
  const finished = set ? qIdx >= set.questions.length : false;

  const start = () => {
    setMode(null);
    setPicks([]);
  };
  const choose = (m: QuizMode) => {
    setMode(m);
    setPicks([]);
  };
  const answer = (i: number) => setPicks((p) => [...p, i]);
  const back = () => setPicks((p) => p.slice(0, -1));

  let title: React.ReactNode;
  let lead: string;
  if (!set) {
    title = (
      <>
        あなたのサロン経営、
        <br />
        <span className="grad">どこに伸びしろ</span>がある?
      </>
    );
    lead =
      "売り込みではありません。集客・リピート・単価…日々の悩みから、いまの現在地が30秒でわかります。";
  } else if (!finished) {
    title = (
      <>
        {set.label}　<span className="grad">自己診断</span>
      </>
    );
    lead = set.lead;
  } else {
    title = <span className="grad">あなたの現在地</span>;
    lead = `${set.label} / いまの自己診断の結果`;
  }

  const progress = !set ? 0 : finished ? 100 : (qIdx / set.questions.length) * 100;

  return (
    <section className="quiz" id="quiz">
      <div className="quiz-card">
        <div className="label">Self Check</div>
        <h2>{title}</h2>
        <p className="lead">{lead}</p>

        {set && (
          <div className="progress">
            <i style={{ width: `${progress}%` }} />
          </div>
        )}

        <div>
          {!set && <RoleSelect onChoose={choose} />}
          {set && !finished && (
            <Question
              set={set}
              qIdx={qIdx}
              onAnswer={answer}
              onBack={qIdx > 0 ? back : start}
              backLabel={qIdx > 0 ? "← 前の質問へ" : "← 立場を選び直す"}
            />
          )}
          {set && finished && mode && (
            <Result mode={mode} picks={picks} onRestart={start} />
          )}
        </div>
      </div>
    </section>
  );
}
