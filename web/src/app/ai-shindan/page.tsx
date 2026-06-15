import type { Metadata } from "next";
import AiShindan from "@/components/AiShindan";

export const metadata: Metadata = {
  title: "AI活用診断（β）",
  description:
    "あなたのサロンは、AIを“安全に”使えていますか。活用度とコンプライアンスの両面を6つの視点で可視化する無料の自己診断。約2分・サーバー送信なし。",
};

export default function AiShindanPage() {
  return (
    <>
      {/* 診断ページ用のコンパクトなヘッダー（.heroのスタイルを流用し高さを抑える） */}
      <section className="hero" style={{ minHeight: "auto", paddingTop: 76, paddingBottom: 8 }}>
        <div className="eyebrow" style={{ textAlign: "center" }}>
          AI Readiness Check
        </div>
        <h1 style={{ fontSize: "2.1rem" }}>
          あなたのサロンは、
          <br />
          <span className="grad">AIを“安全に”</span>使えていますか？
        </h1>
        <p className="sub">
          「使えているか」と「安全に使えているか」。両方の視点で、いまの“AI活用度”を6つの視点で可視化します。
        </p>
      </section>

      <AiShindan />

      <footer>
        © 2026 DigiLab Beauty / 一般社団法人デジラボビューティー
        <span className="legal">
          ※本診断はデモ（β・たたき台）です。「美容業界AI活用ガイドライン」は策定中。掲載の表現は法務監修前のため、公開前に薬機法・景表法・個人情報保護法の最終確認が必要です。
        </span>
      </footer>
    </>
  );
}
