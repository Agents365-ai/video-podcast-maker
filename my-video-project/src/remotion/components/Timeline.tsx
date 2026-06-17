// React import not needed with react-jsx transform
import type { VideoProps } from "../Root";
import { useEntrance, useDrawOn, staggerDelay } from "./animations";

// Animated SVG node circle that draws itself on
const TimelineNode = ({
  color, enabled, delay, size = 28,
}: {
  color: string; enabled: boolean; delay: number; size?: number;
}) => {
  const r = size / 2;
  // Circle as SVG path (clockwise arc)
  const circlePath = `M ${r} 0 A ${r} ${r} 0 1 1 ${r} ${size} A ${r} ${r} 0 1 1 ${r} 0`;
  const draw = useDrawOn(circlePath, enabled, delay, 15, "snappy");

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} style={{ flexShrink: 0 }}>
      {/* Glow background (always visible once drawn) */}
      <circle
        cx={r} cy={r} r={r}
        fill={color}
        opacity={draw.progress}
      />
      {/* Draw-on ring */}
      <path
        d={circlePath}
        fill="none"
        stroke={color}
        strokeWidth={2}
        strokeDasharray={draw.strokeDasharray}
        strokeDashoffset={draw.strokeDashoffset}
        filter={`drop-shadow(0 0 6px ${color})`}
      />
    </svg>
  );
};

// Animated SVG connector line between nodes
const TimelineConnector = ({
  color, enabled, delay, height,
}: {
  color: string; enabled: boolean; delay: number; height: number;
}) => {
  const linePath = `M 1.5 0 L 1.5 ${height}`;
  const draw = useDrawOn(linePath, enabled, delay, 20, "gentle");

  return (
    <svg width={3} height={height} viewBox={`0 0 3 ${height}`} style={{ flexShrink: 0 }}>
      <path
        d={linePath}
        fill="none"
        stroke={color}
        strokeWidth={3}
        strokeOpacity={0.4}
        strokeLinecap="round"
        strokeDasharray={draw.strokeDasharray}
        strokeDashoffset={draw.strokeDashoffset}
      />
      {/* Gradient overlay for fade effect */}
      <defs>
        <linearGradient id={`tl-grad-${delay}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity={0.6} />
          <stop offset="100%" stopColor={color} stopOpacity={0.1} />
        </linearGradient>
      </defs>
      <path
        d={linePath}
        fill="none"
        stroke={`url(#tl-grad-${delay})`}
        strokeWidth={3}
        strokeLinecap="round"
        strokeDasharray={draw.strokeDasharray}
        strokeDashoffset={draw.strokeDashoffset}
      />
    </svg>
  );
};

export const Timeline = ({
  props,
  items,
  delay = 0,
}: {
  props: VideoProps;
  items: { label: string; description: string }[];
  delay?: number;
}) => {
  const connectorHeight = 32;

  return (
    <div style={{
      display: "flex", flexDirection: "column", gap: 0,
      width: "100%", maxWidth: 700,
      margin: "0 auto",
    }}>
      {items.map((item, i) => {
        const itemDelay = staggerDelay(i, delay, 10);
        const a = useEntrance(props.enableAnimations, itemDelay, "snappy");
        return (
          <div key={i} style={{
            display: "flex", gap: 28, opacity: a.opacity,
            transform: `translateY(${a.translateY}px)`,
          }}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 32 }}>
              <TimelineNode
                color={props.primaryColor}
                enabled={props.enableAnimations}
                delay={itemDelay}
              />
              {i < items.length - 1 && (
                <TimelineConnector
                  color={props.primaryColor}
                  enabled={props.enableAnimations}
                  delay={itemDelay + 8}
                  height={connectorHeight}
                />
              )}
            </div>
            <div style={{ paddingBottom: i < items.length - 1 ? 32 : 0, flex: 1 }}>
              <div style={{ fontSize: 34, fontWeight: 700, color: props.primaryColor }}>{item.label}</div>
              <div style={{ fontSize: 26, color: props.textColor, marginTop: 6, lineHeight: 1.5, opacity: 0.75 }}>
                {item.description}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
