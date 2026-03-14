import React from "react";
import type { VideoProps } from "../Root";
import { useEntrance } from "./animations";

export const Timeline = ({
  props,
  items,
  delay = 0,
}: {
  props: VideoProps;
  items: { label: string; description: string }[];
  delay?: number;
}) => {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 0, width: "100%" }}>
      {items.map((item, i) => {
        const a = useEntrance(props.enableAnimations, delay + i * 6, "snappy");
        return (
          <div key={i} style={{
            display: "flex", gap: 28, opacity: a.opacity,
            transform: `translateY(${a.translateY}px)`,
          }}>
            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: 32 }}>
              <div style={{
                width: 28, height: 28, borderRadius: 14, flexShrink: 0,
                background: props.primaryColor,
                boxShadow: `0 0 12px ${props.primaryColor}50, 0 0 24px ${props.primaryColor}20`,
              }} />
              {i < items.length - 1 && (
                <div style={{
                  width: 3, flex: 1, minHeight: 32,
                  background: `linear-gradient(180deg, ${props.primaryColor}60, ${props.primaryColor}15)`,
                }} />
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
