import { LINKS } from "@/lib/links";

/**
 * 企業・団体向け面（B2B・実利・権威）。
 * メインLP内の軽量版。「標準」という語は前面に出さない。
 *
 * NOTE: ★最重要タスクである「DigiLab AI Code of Practice（10原則）を核とした
 *   規範性のある企業資料」は次フェーズで /business ルートとして本格実装する。
 *   ここはデモ（pane-biz）の構成を忠実移植したもの。
 */
export default function BizPane() {
  const contactExternal = /^https?:\/\//.test(LINKS.businessContact);
  return (
    <>
      {/* Why: 第三者評価で「選ばれる理由」を証明 */}
      <section className="block" style={{ paddingTop: 64 }}>
        <div className="label">Why DigiLab Beauty</div>
        <h2>
          「選ばれる理由」を、
          <br />
          <span className="grad">第三者の目</span>で証明する。
        </h2>
        <p style={{ textAlign: "center", maxWidth: 430, margin: "0 auto" }}>
          技術力も、安全性も、データの扱いも——自社で「大丈夫です」と言うだけでは、もう信頼されない時代。第三者の評価が、選ばれる決め手になります。
        </p>
      </section>

      <div className="divider" />

      {/* 導入メリット3つ */}
      <section className="block">
        <div className="label">Value</div>
        <h2>導入で、得られること</h2>
        <div className="pain">
          <div className="pain-item">
            <b>① 信頼の「見える化」</b>
            <span>
              第三者評価という客観的な裏付けで、取引先・顧客・採用候補者からの信頼を獲得。
            </span>
          </div>
          <div className="pain-item">
            <b>② リスクの先回り</b>
            <span>
              広告表現・衛生・データ管理を客観評価し、トラブルになる前に弱点を可視化。
            </span>
          </div>
          <div className="pain-item">
            <b>③ 競合との差別化</b>
            <span>
              「評価を受けている」こと自体が、価格競争から抜け出す独自の強みになる。
            </span>
          </div>
        </div>
      </section>

      <div className="divider" />

      {/* 評価の枠組み（DQSを"信頼の物差し"として） */}
      <section className="block dqs-hero" id="dqs">
        <div className="label">The Framework</div>
        <h2>112点の「信頼の物差し」</h2>
        <p>
          人の品質と運用の品質を、
          <br />7 つの視点・28項目で客観的に評価します。
        </p>
        <div className="dqs-grid">
          <div className="dqs-cell">
            <div className="k">7</div>
            <div className="t">評価の視点</div>
          </div>
          <div className="dqs-cell">
            <div className="k">28</div>
            <div className="t">評価項目</div>
          </div>
          <div className="dqs-cell">
            <div className="k">112</div>
            <div className="t">スコアで可視化</div>
          </div>
          <div className="dqs-cell">
            <div className="k">第三者</div>
            <div className="t">による客観評価</div>
          </div>
        </div>
      </section>

      <div className="divider" />

      {/* 3つの評価レベル */}
      <section className="block">
        <div className="label">Levels</div>
        <h2>3つの評価レベル</h2>
        <div className="tier">
          <div className="tier-card">
            <div className="bar" />
            <div className="step">LEVEL 01</div>
            <h3>Practitioner</h3>
            <p>基礎を満たし、安全に実務を行えることの証明。導入の第一歩。</p>
          </div>
          <div className="tier-card">
            <div className="bar" />
            <div className="step">LEVEL 02</div>
            <h3>Professional</h3>
            <p>品質を設計・運用できる実践レベル。組織の品質責任を担える証明。</p>
          </div>
          <div className="tier-card">
            <div className="bar" />
            <div className="step">LEVEL 03</div>
            <h3>Master Fellow</h3>
            <p>業界をリードするトップ層。評価の監修・指導に関与できる最上位。</p>
          </div>
        </div>
      </section>

      <div className="divider" />

      {/* 対象 + 資料請求CTA */}
      <section className="final">
        <div className="label">For Business</div>
        <h2>
          貴社の品質を、
          <br />
          <span className="grad">選ばれる強み</span>に。
        </h2>
        <p
          style={{
            color: "var(--ink-soft)",
            marginBottom: 30,
            maxWidth: 430,
            marginLeft: "auto",
            marginRight: "auto",
          }}
        >
          機器メーカー・化粧品・サロンチェーン・教育機関の皆さまへ。評価の導入・パートナーシップのご相談を承ります。まずは詳しい資料をご覧ください。
        </p>
        <a
          href={LINKS.businessContact}
          className="btn btn-primary"
          style={{ display: "inline-block" }}
          {...(contactExternal ? { target: "_blank", rel: "noopener noreferrer" } : {})}
        >
          資料を請求する（無料）
        </a>
        <p style={{ color: "var(--ink-soft)", fontSize: ".82rem", marginTop: 20 }}>
          評価制度の詳細・導入事例・料金の資料をお送りします。
        </p>
      </section>
    </>
  );
}
