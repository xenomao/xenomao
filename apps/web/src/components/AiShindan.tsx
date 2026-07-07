"use client";

import { useState } from "react";
import {
  AI_AXES,
  AI_QUESTIONS,
  computeAiResult,
} from "@/lib/aiShindan";
import RadarChart from "./RadarChart";
import LineButton from "./LineButton";

/** 設問1問の表示 */
function Question({
  qIdx,
  onAnswer,
  onBack,
}: {
  qIdx: number;
  onAnswer: (i: number) => void;
  onBack: () => void;
}) {
  const question = AI_QUESTIONS[qIdx];
  return (
    <>
      <div className="q-head">
        Q{qIdx + 1} / {AI_QUESTIONS.length}
      </div>
      <div style={{ fontSize: ".74rem", color: "var(--ink-soft)", marginBottom: 8 }}>
        視点：{AI_AXES[question.axis]}
      </div>
      <div className="q-text">{question.q}</div>
      <div className="pick">
        {question.opts.map((o, i) => (
          <button key={i} className="opt" onClick={() => onAnswer(i)}>
            {o.t}
          </button>
        ))}
      </div>
      <button className="back" onClick={onBack}>
        {qIdx > 0 ? "← 前の質問へ" : "← はじめに戻る"}
      </button>
    </>
  );
}

/** 診断結果（100点換算・レベル・最弱視点・連動セミナー） */
function Result({ picks, onRestart }: { picks: number[]; onRestart: () => void }) {
  const { axisScores, max, score100, level, reco } = computeAiResult(picks);

  return (
    <div className="result">
      <div className="score-big">
        {score100}
        <span
          style={{
            fontSize: "1.4rem",
            color: "var(--ink-soft)",
            WebkitTextFillColor: "var(--ink-soft)",
          }}
        >
          {" "}
          点
        </span>
      </div>
      <div className="score-cap">100点満点・あなたのAI活用スコア</div>
      <div className="rank-badge">
        {level.tier}　{level.name}
      </div>
      <div className="radar-wrap">
        <RadarChart labels={[...AI_AXES]} values={axisScores} max={max} gradientId="rg-ai" />
      </div>
      <p className="msg">{level.msg}</p>

      <div className="weak">
        <div className="weak-tag">いちばんの伸びしろ</div>
        <div className="weak-head">{reco.head}</div>
        <div className="weak-ben">{reco.step}。</div>
      </div>

      <div className="offer">
        <div className="offer-ey">Recommended Seminar</div>
        <div className="offer-h">
          あなたに今おすすめの「<span className="grad">{reco.axis}</span>」の回
        </div>
        <div className="next" style={{ boxShadow: "none", marginTop: 8, padding: "18px 18px" }}>
          <span className="nx-tag">Next Step</span>
          <div className="nx-title" style={{ fontSize: "1.08rem" }}>
            {reco.seminar}
          </div>
          <div className="nx-meta" style={{ marginBottom: 0 }}>
            月2回のオンラインセミナーで、現場ですぐ試せる形で解説します。
          </div>
        </div>
        <LineButton style={{ marginTop: 14 }} />
        <p className="line-sub">セミナーで詳しい解説と、次の一歩をご案内します。</p>
      </div>

      <button className="back" onClick={onRestart} style={{ display: "block", margin: "20px auto 0" }}>
        ↺ もう一度診断する
      </button>
      <p className="disc">
        ※本診断は「美容業界AI活用ガイドライン（策定中・v0.1）」の考え方にもとづく簡易的な自己診断です。認証の合否や水準、特定の成果を保証・約束するものではありません。回答はこの場の表示のみに使用し、サーバーには送信・保存していません。
      </p>
    </div>
  );
}

/**
 * AI活用診断（AI Readiness Check）本体。
 * 立場選択なしの一本道。状態は picks（回答履歴）のみ・localStorage不使用・サーバー送信なし。
 */
export default function AiShindan() {
  const [started, setStarted] = useState(false);
  const [picks, setPicks] = useState<number[]>([]);

  const qIdx = picks.length;
  const finished = qIdx >= AI_QUESTIONS.length;

  const reset = () => {
    setStarted(false);
    setPicks([]);
  };
  const answer = (i: number) => setPicks((p) => [...p, i]);
  const back = () => setPicks((p) => p.slice(0, -1));

  let title: React.ReactNode;
  let lead: string;
  if (!started) {
    title = (
      <>
        まずは、6つの視点で
        <br />
        <span className="grad">セルフチェック</span>
      </>
    );
    lead = "「使えているか」だけでなく「安全に使えているか」まで。約2分・12問・サーバー送信なし。";
  } else if (!finished) {
    title = (
      <>
        AI活用 <span className="grad">セルフチェック</span>
      </>
    );
    lead = "いまのサロンに、いちばん近いものを選んでください。";
  } else {
    title = <span className="grad">あなたのAI活用度</span>;
    lead = "いまの自己診断の結果";
  }

  const progress = !started ? 0 : finished ? 100 : (qIdx / AI_QUESTIONS.length) * 100;

  return (
    <section className="quiz" id="ai-shindan">
      <div className="quiz-card">
        <div className="label">AI Readiness Check</div>
        <h2>{title}</h2>
        <p className="lead">{lead}</p>

        {started && (
          <div className="progress">
            <i style={{ width: `${progress}%` }} />
          </div>
        )}

        <div>
          {!started && (
            <div className="pick">
              <button onClick={() => setStarted(true)}>
                診断をはじめる（約2分・12問）
                <span className="o-sub">サロン経営者・スタッフ どなたでも</span>
              </button>
            </div>
          )}
          {started && !finished && (
            <Question qIdx={qIdx} onAnswer={answer} onBack={qIdx > 0 ? back : reset} />
          )}
          {started && finished && <Result picks={picks} onRestart={reset} />}
        </div>
      </div>
    </section>
  );
}
