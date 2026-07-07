import type { Metadata } from "next";
import Hero from "@/components/Hero";
import Tabs from "@/components/Tabs";
import SalonPane from "@/components/SalonPane";
import BizPane from "@/components/BizPane";

export const metadata: Metadata = {
  title: { absolute: "DigiLab Beauty｜美容業界に、品質の標準を。" },
  description:
    "サロン・個人の集客/リピートの悩みから、企業・団体の品質基準・認証まで。学びと基準の両輪で、美容のこれからを支えます。",
};

export default function Home() {
  return (
    <>
      <Hero />

      {/* 切替タブ（サロン・個人 / 企業・団体）。両ペインを保持し表示切替 */}
      <Tabs salon={<SalonPane />} biz={<BizPane />} />

      <footer>
        © 2026 DigiLab Beauty / 一般社団法人デジラボビューティー
        <span className="legal">
          ※本ページはデモ（たたき台）です。掲載の表現は法務監修前のため、ローンチ前に薬機法・景表法・個人情報保護法の最終確認が必要です。
        </span>
      </footer>
    </>
  );
}
