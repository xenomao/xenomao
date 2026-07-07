import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "DigiLab Beauty｜美容の“品質”を、育てる場所。",
    template: "%s｜DigiLab Beauty",
  },
  description:
    "サロンの成長も、業界の信頼も、根っこは同じ「品質」。デジラボビューティーは、学びと基準の両輪で、美容のこれからを支えます。",
  applicationName: "DigiLab Beauty",
  authors: [{ name: "一般社団法人デジラボビューティー" }],
  openGraph: {
    title: "DigiLab Beauty｜美容の“品質”を、育てる場所。",
    description:
      "サロンの成長も、業界の信頼も、根っこは同じ「品質」。学びと基準の両輪で、美容のこれからを支えます。",
    siteName: "DigiLab Beauty",
    locale: "ja_JP",
    type: "website",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  colorScheme: "light",
  themeColor: "#FFFDFB",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        {/* 日本語（Shippori Mincho）の確実な表示のため Google Fonts を利用。
            CJK はブラウザが unicode-range で必要分のみ取得する。 */}
        <link
          href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400&family=Shippori+Mincho:wght@400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        {/* 波動レイヤー（白の上で淡く・全ページ共通の固定背景） */}
        <div className="aurora" aria-hidden="true">
          <div className="wave w1" />
          <div className="wave w2" />
          <div className="wave w3" />
        </div>
        <div className="wrap">{children}</div>
      </body>
    </html>
  );
}
