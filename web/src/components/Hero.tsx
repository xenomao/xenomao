/**
 * 共通ヒーロー（メインLP）。
 * 中央に「美質の波動」SVG（中心の光核から波紋が広がるアニメ）。
 * 抽象アートのみ・権利クリアのSVG（人物写真・ストック画像は使わない）。
 */
export default function Hero() {
  return (
    <section className="hero">
      <div className="eyebrow">DigiLab Beauty</div>

      <div className="portrait">
        <div className="ring" />
        <svg
          viewBox="0 0 248 248"
          xmlns="http://www.w3.org/2000/svg"
          role="img"
          aria-label="美質の波動（光が広がる抽象アート）"
        >
          <defs>
            <radialGradient id="bgGrad" cx="50%" cy="42%" r="70%">
              <stop offset="0%" stopColor="#FFFFFF" />
              <stop offset="55%" stopColor="#FBF6FC" />
              <stop offset="100%" stopColor="#F3ECF7" />
            </radialGradient>
            <radialGradient id="glow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#F0467A" stopOpacity=".55" />
              <stop offset="35%" stopColor="#C77FD6" stopOpacity=".35" />
              <stop offset="70%" stopColor="#9AB8F0" stopOpacity=".18" />
              <stop offset="100%" stopColor="#9AB8F0" stopOpacity="0" />
            </radialGradient>
            <linearGradient id="ringGrad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#5B8DF0" />
              <stop offset="50%" stopColor="#A855F7" />
              <stop offset="100%" stopColor="#F0467A" />
            </linearGradient>
          </defs>
          <rect width="248" height="248" fill="url(#bgGrad)" />
          <circle cx="124" cy="124" r="96" fill="url(#glow)" />
          {/* 広がる波動リング */}
          <g fill="none" stroke="url(#ringGrad)" strokeLinecap="round">
            <circle cx="124" cy="124" r="30" strokeWidth="1.6" opacity=".9">
              <animate attributeName="r" values="30;34;30" dur="6s" repeatCount="indefinite" />
            </circle>
            <circle cx="124" cy="124" r="50" strokeWidth="1.2" opacity=".6">
              <animate attributeName="r" values="50;55;50" dur="7s" repeatCount="indefinite" />
            </circle>
            <circle cx="124" cy="124" r="72" strokeWidth="1" opacity=".4">
              <animate attributeName="r" values="72;78;72" dur="8s" repeatCount="indefinite" />
            </circle>
            <circle cx="124" cy="124" r="94" strokeWidth="1" opacity=".22">
              <animate attributeName="r" values="94;100;94" dur="9s" repeatCount="indefinite" />
            </circle>
          </g>
          {/* 外へ放たれる波紋 */}
          <circle cx="124" cy="124" r="20" fill="none" stroke="url(#ringGrad)" strokeWidth="1.4" opacity="0">
            <animate attributeName="r" values="20;110" dur="5s" repeatCount="indefinite" />
            <animate attributeName="opacity" values=".7;0" dur="5s" repeatCount="indefinite" />
          </circle>
          {/* 中心の光核 */}
          <circle cx="124" cy="124" r="9" fill="#F0467A" opacity=".9" />
          <circle cx="124" cy="124" r="14" fill="none" stroke="#F0467A" strokeWidth="1.2" opacity=".5">
            <animate attributeName="r" values="14;20;14" dur="4s" repeatCount="indefinite" />
            <animate attributeName="opacity" values=".5;0;.5" dur="4s" repeatCount="indefinite" />
          </circle>
        </svg>
      </div>

      <h1>
        美容の“品質”を、
        <br />
        <span className="grad">育てる場所</span>。
      </h1>
      <p className="sub">
        サロンの成長も、業界の信頼も、根っこは同じ「品質」。デジラボビューティーは、学びと基準の両輪で、美容のこれからを支えます。
      </p>
      <div className="brand">
        DigiLab Beauty
        <small>デジラボビューティー</small>
      </div>
    </section>
  );
}
