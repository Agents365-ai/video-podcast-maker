import React from "react";
import type { VideoProps } from "../Root";
import { useEntrance } from "./animations";

export const FeatureGrid = ({
  props,
  items,
  columns = 3,
  delay = 0,
}: {
  props: VideoProps;
  items: { icon: string; title: string; description: string }[];
  columns?: 2 | 3;
  delay?: number;
}) => {
  return (
    <div style={{
      display: "flex", flexWrap: "wrap", gap: 28, width: "100%",
    }}>
      {items.map((item, i) => {
        const a = useEntrance(props.enableAnimations, delay + i * 5);
        return (
          <div key={i} style={{
            flex: `0 0 calc(${100 / columns}% - ${28 * (columns - 1) / columns}px)`,
            background: "rgba(0,0,0,0.02)", border: "1px solid rgba(0,0,0,0.08)",
            borderRadius: 20, padding: "36px 32px", textAlign: "center",
            opacity: a.opacity, transform: `translateY(${a.translateY}px)`,
          }}>
            <div style={{ fontSize: 56, marginBottom: 16 }}>{item.icon}</div>
            <div style={{ fontSize: 32, fontWeight: 700, color: props.primaryColor, marginBottom: 10 }}>
              {item.title}
            </div>
            <div style={{ fontSize: 24, color: props.textColor, lineHeight: 1.5 }}>
              {item.description}
            </div>
          </div>
        );
      })}
    </div>
  );
};
