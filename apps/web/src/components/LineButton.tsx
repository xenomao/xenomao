import { LINKS } from "@/lib/links";

/** LINE の吹き出しアイコン（デモから移植） */
export function LineIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 2C6.5 2 2 5.6 2 10.1c0 4 3.6 7.4 8.4 8 .3.1.8.2.9.5.1.3.1.7 0 1l-.1.9c0 .3-.2 1 .9.6 1.1-.5 6-3.5 8.2-6C21.6 13.6 22 11.9 22 10.1 22 5.6 17.5 2 12 2z" />
    </svg>
  );
}

type LineButtonProps = {
  /** ボタン文言（HANDOFF: 全箇所「公式LINEで無料招待を受け取る」に統一） */
  label?: string;
  className?: string;
  style?: React.CSSProperties;
};

/**
 * 公式LINE 友だち追加への大ボタン。href は環境変数（LINKS.line）。
 * URL未設定（"#"）のときは新規タブ遷移属性を付けない。
 */
export default function LineButton({
  label = "公式LINEで無料招待を受け取る",
  className,
  style,
}: LineButtonProps) {
  const href = LINKS.line;
  const isExternal = /^https?:\/\//.test(href);
  return (
    <a
      className={className ? `line-btn ${className}` : "line-btn"}
      href={href}
      style={style}
      {...(isExternal
        ? { target: "_blank", rel: "noopener noreferrer" }
        : {})}
    >
      <LineIcon />
      {label}
    </a>
  );
}
