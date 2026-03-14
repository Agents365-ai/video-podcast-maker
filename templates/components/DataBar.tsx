import React from "react";
import type { VideoProps } from "../Root";
import { useEntrance } from "./animations";

export const DataBar = ({
  props,
  items,
  delay = 0,
}: {
  props: VideoProps;
  items: { label: string; value: number; maxValue?: number }[];
  delay?: number;
}) => {
  const max = Math.max(...items.map((d) => d.maxValue ?? d.value));
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24, width: "100%" }}>
      {items.map((item, i) => {
        const pct = (item.value / max) * 100;
        const a = useEntrance(props.enableAnimations, delay + i * 5);
        return (
          <div key={i} style={{
            display: "flex", alignItems: "center", gap: 20,
            opacity: a.opacity, transform: `translateY(${a.translateY}px)`,
          }}>
            <div style={{
              fontSize: 28, fontWeight: 600, color: props.textColor,
              width: 160, textAlign: "right", flexShrink: 0,
            }}>
              {item.label}
            </div>
            <div style={{
              flex: 1, height: 40, background: "rgba(0,0,0,0.06)", borderRadius: 20, overflow: "hidden",
            }}>
              <div style={{
                width: `${pct}%`, height: "100%", borderRadius: 20,
                background: `linear-gradient(90deg, ${props.primaryColor}, ${props.accentColor})`,
              }} />
            </div>
            <div style={{ fontSize: 26, fontWeight: 700, color: props.primaryColor, width: 80 }}>
              {item.value}%
            </div>
          </div>
        );
      })}
    </div>
  );
};
