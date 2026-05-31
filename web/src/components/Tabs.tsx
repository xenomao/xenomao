"use client";

import { useRef, useState } from "react";

type TabsProps = {
  salon: React.ReactNode;
  biz: React.ReactNode;
};

/**
 * サロン / 企業 の切替タブ（sticky）。
 * 両ペインは常にDOMに保持し、表示のみ切り替える（デモ準拠・診断の状態も保持される）。
 */
export default function Tabs({ salon, biz }: TabsProps) {
  const [which, setWhich] = useState<"salon" | "biz">("salon");
  const tabsRef = useRef<HTMLDivElement>(null);

  const select = (w: "salon" | "biz") => {
    setWhich(w);
    // ペイン切替後にタブ位置までスクロール（デモの window.scrollTo を再現）
    requestAnimationFrame(() => {
      const el = tabsRef.current;
      if (el) window.scrollTo({ top: el.offsetTop, behavior: "smooth" });
    });
  };

  return (
    <>
      <div className="tabs" ref={tabsRef}>
        <button
          className={which === "salon" ? "active" : undefined}
          onClick={() => select("salon")}
          aria-pressed={which === "salon"}
        >
          サロン・個人の方
          <span className="tb-sub">集客・リピートの悩みに</span>
        </button>
        <button
          className={which === "biz" ? "active" : undefined}
          onClick={() => select("biz")}
          aria-pressed={which === "biz"}
        >
          企業・団体の方
          <span className="tb-sub">品質基準・認証</span>
        </button>
      </div>

      <div className={which === "salon" ? "pane active" : "pane"}>{salon}</div>
      <div className={which === "biz" ? "pane active" : "pane"}>{biz}</div>
    </>
  );
}
