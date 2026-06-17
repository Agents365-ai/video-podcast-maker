import React from "react";
import type { VideoProps } from "../Root";
import { useEntrance } from "./animations";

export const CodeBlock = ({
  props,
  title = "terminal",
  lines,
  delay = 0,
}: {
  props: VideoProps;
  title?: string;
  lines: string[];
  delay?: number;
}) => {
  const anim = useEntrance(props.enableAnimations, delay);
  return (
    <div style={{
      width: "100%", borderRadius: 20, overflow: "hidden",
      opacity: anim.opacity, transform: `translateY(${anim.translateY}px)`,
      boxShadow: "0 8px 32px rgba(0,0,0,0.12)",
    }}>
      <div style={{
        background: "#2d2d2d", padding: "14px 24px",
        display: "flex", alignItems: "center", gap: 12,
      }}>
        <div style={{ display: "flex", gap: 8 }}>
          {["#ff5f57", "#febc2e", "#28c840"].map((c) => (
            <div key={c} style={{ width: 14, height: 14, borderRadius: 7, background: c }} />
          ))}
        </div>
        <span style={{ fontSize: 20, color: "rgba(255,255,255,0.5)", marginLeft: 8 }}>{title}</span>
      </div>
      <div style={{ background: "#1e1e1e", padding: "28px 32px" }}>
        {lines.map((line, i) => {
          const lineAnim = useEntrance(props.enableAnimations, delay + 5 + i * 4);
          return (
            <div key={i} style={{
              fontFamily: "SF Mono, Menlo, Monaco, monospace", fontSize: 26,
              color: "#e6e6e6", lineHeight: 1.8,
              opacity: lineAnim.opacity, transform: `translateY(${lineAnim.translateY}px)`,
            }}>
              {line}
            </div>
          );
        })}
      </div>
    </div>
  );
};
