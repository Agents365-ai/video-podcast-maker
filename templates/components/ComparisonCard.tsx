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
  const leftAnim = useEntrance(props.enableAnimations, delay + 5);
  const rightAnim = useEntrance(props.enableAnimations, delay + 10);

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
            }}>
              VS
            </div>
          )}
          <div style={{
            flex: v ? undefined : 1, width: v ? "100%" : undefined,
            background: side.highlight ? `${props.primaryColor}08` : "rgba(0,0,0,0.02)",
            border: side.highlight ? `2px solid ${props.primaryColor}30` : "1px solid rgba(0,0,0,0.08)",
            borderRadius: 24, padding: v ? "36px 40px" : "40px 44px",
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
