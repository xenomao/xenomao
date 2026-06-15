/**
 * 汎用レーダーチャート（軽量SVG・外部ライブラリ不要）。
 * 経営自己診断（Quiz）とAI活用診断（AiShindan）で共用する。
 * 1ページに複数描画する場合は gradientId を分けてグラデの id 衝突を避ける。
 */
type RadarChartProps = {
  labels: string[];
  values: number[];
  max: number[];
  gradientId?: string;
};

export default function RadarChart({
  labels,
  values,
  max,
  gradientId = "rg",
}: RadarChartProps) {
  const N = labels.length;
  const cx = 150;
  const cy = 140;
  const R = 104;
  const pt = (ax: number, r: number) => {
    const a = -Math.PI / 2 + (ax * 2 * Math.PI) / N;
    return [cx + r * Math.cos(a), cy + r * Math.sin(a)] as const;
  };

  const grid = [0.25, 0.5, 0.75, 1].map((f, gi) => {
    let p = "";
    for (let i = 0; i < N; i++) {
      const [x, y] = pt(i, R * f);
      p += (i ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1);
    }
    return <path key={gi} d={`${p}Z`} fill="none" stroke="#E7DEF0" strokeWidth="1" />;
  });

  const axesL = [];
  for (let i = 0; i < N; i++) {
    const [x, y] = pt(i, R);
    axesL.push(
      <line
        key={i}
        x1={cx}
        y1={cy}
        x2={Number(x.toFixed(1))}
        y2={Number(y.toFixed(1))}
        stroke="#E7DEF0"
        strokeWidth="1"
      />,
    );
  }

  let poly = "";
  for (let i = 0; i < N; i++) {
    const r = R * Math.min(1, values[i] / (max[i] || 1));
    const [x, y] = pt(i, r);
    poly += (i ? "L" : "M") + x.toFixed(1) + " " + y.toFixed(1);
  }

  const labelEls = [];
  for (let i = 0; i < N; i++) {
    const [x, y] = pt(i, R + 16);
    labelEls.push(
      <text
        key={i}
        x={Number(x.toFixed(1))}
        y={Number(y.toFixed(1))}
        fontSize="9"
        fill="#6E6781"
        textAnchor="middle"
        dominantBaseline="middle"
        fontFamily="Shippori Mincho"
      >
        {labels[i]}
      </text>,
    );
  }

  return (
    <svg viewBox="0 0 300 290">
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="#5B8DF0" />
          <stop offset="100%" stopColor="#F0467A" />
        </linearGradient>
      </defs>
      {grid}
      {axesL}
      <path
        d={`${poly}Z`}
        fill={`url(#${gradientId})`}
        fillOpacity="0.22"
        stroke={`url(#${gradientId})`}
        strokeWidth="2"
      />
      {labelEls}
    </svg>
  );
}
