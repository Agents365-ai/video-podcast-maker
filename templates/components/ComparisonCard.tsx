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
  const anim = useEntrance(props.enableAnimations, delay);
  const leftAnim = useEntrance(props.enableAnimations, delay + 5);
  const rightAnim = useEntrance(props.enableAnimations, delay + 10);

  return (
    <div style={{ display: "flex", alignItems: "center", gap: 40, width: "100%", opacity: anim.opacity }}>
      {[{ side: left, a: leftAnim }, { side: right, a: rightAnim }].map(({ side, a }, i) => (
        <React.Fragment key={i}>
          {i === 1 && (
            <div style={{
              fontSize: 48, fontWeight: 800, color: props.primaryColor, opacity: 0.6,
              flexShrink: 0,
            }}>
              VS
            </div>
          )}
          <div style={{
            flex: 1, background: side.highlight ? `${props.primaryColor}08` : "rgba(0,0,0,0.02)",
            border: side.highlight ? `2px solid ${props.primaryColor}30` : "1px solid rgba(0,0,0,0.08)",
            borderRadius: 24, padding: "40px 44px",
            opacity: a.opacity, transform: `translateY(${a.translateY}px)`,
          }}>
            <h3 style={{ fontSize: 38, fontWeight: 700, color: props.primaryColor, marginBottom: 24 }}>
              {side.title}
            </h3>
            {side.items.map((item, j) => (
              <div key={j} style={{
                fontSize: 28, color: props.textColor, padding: "10px 0",
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
