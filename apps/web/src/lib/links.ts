/**
 * 外部リンクの一元管理。
 * 公式LINE / Instagram / Stripe Checkout / 企業向け問い合わせ の各URLは
 * 環境変数（.env.local）で差し替える。クライアントからも参照するため
 * すべて NEXT_PUBLIC_ プレフィックスにしている。
 * 未設定時は "#"（ダミー）にフォールバックする。
 */
const fallback = "#";

export const LINKS = {
  /** 公式LINE 友だち追加URL */
  line: process.env.NEXT_PUBLIC_LINE_URL || fallback,
  /** Instagram プロフィールURL */
  instagram: process.env.NEXT_PUBLIC_INSTAGRAM_URL || fallback,
  /** Stripe Checkout（月額サブスク）URL ※決済は最終フェーズで実装 */
  stripeCheckout: process.env.NEXT_PUBLIC_STRIPE_CHECKOUT_URL || fallback,
  /** 企業向け 資料請求・問い合わせURL */
  businessContact: process.env.NEXT_PUBLIC_BUSINESS_CONTACT_URL || fallback,
} as const;

export type LinkKey = keyof typeof LINKS;
