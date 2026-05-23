import React from "react";
import type { VideoProps } from "../Root";
import { useEntrance } from "./animations";

export const ComparisonCard = ({
  props,
  left,
  right,
  delay = 0,
}: {
  props: VideoProps;
  left: { title: string; items: string[]; highlight?: boolean };
  right: { title: string; items: string[]; highlight?: boolean };
  delay?: number;
}) => {
  const v = props.orientation === "vertical";
  const anim = useEntrance(props.enableAnimations, delay);
  const leftAnim = useEntrance(props.enableAnimations, delay + 5, "snappy");
  const rightAnim = useEntrance(props.enableAnimations, delay + 10, "snappy");

  const cardStyle = (side: typeof left, highlighted: boolean): React.CSSProperties => ({
    flex: v ? undefined : 1, width: v ? "100%" : undefined,
    background: highlighted
      ? `linear-gradient(135deg, ${props.primaryColor}0A, ${props.primaryColor}14)`
      : "linear-gradient(135deg, rgba(255,255,255,0.95), rgba(0,0,0,0.02))",
    border: highlighted
      ? `2px solid ${props.primaryColor}30`
      : "1px solid rgba(0,0,0,0.08)",
    borderRadius: 24, padding: v ? "36px 40px" : "40px 44px",
    boxShadow: highlighted
      ? `0 4px 16px ${props.primaryColor}15, 0 8px 32px rgba(0,0,0,0.06)`
      : "0 2px 8px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.06)",
  });

  return (
    <div style={{
      display: "flex", alignItems: "center", gap: v ? 28 : 40, width: "100%",
      flexDirection: v ? "column" : "row", opacity: anim.opacity,
    }}>
      {[{ side: left, a: leftAnim }, { side: right, a: rightAnim }].map(({ side, a }, i) => (
        <React.Fragment key={i}>
          {i === 1 && (
            <div style={{
              fontSize: v ? 40 : 48, fontWeight: 800, color: props.primaryColor, opacity: 0.6,
              flexShrink: 0,
              textShadow: `0 2px 8px ${props.primaryColor}20`,
            }}>
              VS
            </div>
          )}
          <div style={{
            ...cardStyle(side, !!side.highlight),
            opacity: a.opacity, transform: `translateY(${a.translateY}px)`,
          }}>
            <h3 style={{ fontSize: v ? 36 : 38, fontWeight: 700, color: props.primaryColor, marginBottom: 24 }}>
              {side.title}
            </h3>
            {side.items.map((item, j) => (
              <div key={j} style={{
                fontSize: v ? 30 : 28, color: props.textColor, padding: "10px 0",
                borderTop: j > 0 ? "1px solid rgba(0,0,0,0.06)" : "none",
              }}>
                {item}
              </div>
            ))}
          </div>
        </React.Fragment>
      ))}
    </div>
  );
};
