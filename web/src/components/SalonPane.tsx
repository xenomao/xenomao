import { LINKS } from "@/lib/links";
import Quiz from "./Quiz";
import LineButton from "./LineButton";

/**
 * サロン・個人向け面（B2C・実利・親しみ）。
 * 1) 自己診断（現在地確認・AIという言葉は出さない）
 * 2) セミナー予告3本
 * 3) 公式LINEワンクリック動線（緑ボタンが主役・Instagramは控えめなテキストリンク）
 *
 * ⚠️ HANDOFF注記: 「予約が埋まる」「自動集客」等は景表法の優良誤認リスク。
 *    ローンチ前に「学ぶ内容」基準へ要調整（現状はデモ文言を保持）。
 */
const SEMINARS = [
  {
    vol: "VOL.1",
    when: "2026年6月21日（土）20:00–",
    title: "予約が埋まりやすくなる、エステサロンの“自動集客”のしくみ",
    desc: "SNS・予約・お礼の連絡まで、手間をかけずに回す流れづくり。今日から試せる形で。",
  },
  {
    vol: "VOL.2",
    when: "2026年7月19日（土）20:00–",
    title: "1日30分の時短ワザ — 事務作業から解放されるサロン運営",
    desc: "予約管理・カルテ・売上集計などの“地味な作業”を軽くして、施術と接客に集中する時間を取り戻す。",
  },
  {
    vol: "VOL.3",
    when: "2026年8月23日（土）20:00–",
    title: "リピートが続く、お客様カルテの活かし方",
    desc: "一度来てくれたお客様に“また会える”仕組み。記録を次の来店につなげる小さな工夫。",
  },
];

export default function SalonPane() {
  const instaExternal = /^https?:\/\//.test(LINKS.instagram);
  return (
    <>
      {/* 自己診断 */}
      <Quiz />

      <div className="divider" />

      {/* セミナー予告 + 公式LINE動線 */}
      <section className="final" id="cta">
        <div className="label">Upcoming Seminars</div>
        <h2>
          <span className="grad">これからのセミナー</span>、
          <br />
          のぞいてみませんか。
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
          いきなり申し込まなくて大丈夫。まずはどんなテーマを学べるか、予定からご覧ください。
        </p>

        <div className="sem-list">
          {SEMINARS.map((s) => (
            <div className="sem-item" key={s.vol}>
              <span className="sem-vol">{s.vol}</span>
              <div className="sem-when">{s.when}</div>
              <div className="sem-ttl">{s.title}</div>
              <div className="sem-desc">{s.desc}</div>
            </div>
          ))}
        </div>

        <div
          className="nx-price"
          style={{
            maxWidth: 440,
            margin: "18px auto 24px",
            justifyContent: "center",
            borderTop: "none",
            paddingTop: 0,
          }}
        >
          <b>1,000</b>
          <span className="yen">円</span>
          <span className="per">/ 月（税込・いつでも退会できます）</span>
        </div>

        <LineButton />
        <p className="line-sub">
          友だち追加で、初回セミナーに無料ご招待。
          <br />
          最新の開催情報もLINEでお届けします。
        </p>
        <p style={{ textAlign: "center", marginTop: 14 }}>
          <a
            href={LINKS.instagram}
            style={{
              color: "var(--ink-soft)",
              fontSize: ".8rem",
              textDecoration: "none",
              borderBottom: "1px solid var(--line)",
            }}
            {...(instaExternal ? { target: "_blank", rel: "noopener noreferrer" } : {})}
          >
            Instagramで雰囲気を見る →
          </a>
        </p>
      </section>
    </>
  );
}
