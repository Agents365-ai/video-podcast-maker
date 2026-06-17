import React from "react";
import type { VideoProps } from "../Root";
import { useEntrance } from "./animations";

export const DataTable = ({
  props,
  headers,
  rows,
  highlightRows = [],
  delay = 0,
}: {
  props: VideoProps;
  headers: string[];
  rows: string[][];
  highlightRows?: number[];
  delay?: number;
}) => {
  const v = props.orientation === "vertical";
  const anim = useEntrance(props.enableAnimations, delay);

  return (
    <div style={{
      width: "100%",
      borderRadius: 20,
      overflow: "hidden",
      border: "1px solid rgba(0,0,0,0.08)",
      boxShadow: "0 2px 8px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.06)",
      opacity: anim.opacity,
      transform: `translateY(${anim.translateY}px)`,
    }}>
      {/* Header row */}
      <div style={{
        display: "flex",
        background: `linear-gradient(135deg, ${props.primaryColor}12, ${props.primaryColor}08)`,
        borderBottom: `2px solid ${props.primaryColor}20`,
      }}>
        {headers.map((h, i) => (
          <div key={i} style={{
            flex: 1,
            padding: v ? "16px 20px" : "20px 28px",
            fontSize: v ? 28 : 30,
            fontWeight: 700,
            color: props.primaryColor,
            textAlign: i === 0 ? "left" : "center",
          }}>
            {h}
          </div>
        ))}
      </div>
      {/* Data rows */}
      {rows.map((row, ri) => {
        const highlighted = highlightRows.includes(ri);
        return (
          <div key={ri} style={{
            display: "flex",
            background: highlighted
              ? `${props.primaryColor}08`
              : ri % 2 === 0 ? "rgba(255,255,255,0.95)" : "rgba(0,0,0,0.015)",
            borderBottom: ri < rows.length - 1 ? "1px solid rgba(0,0,0,0.06)" : "none",
            borderLeft: highlighted ? `3px solid ${props.primaryColor}40` : "3px solid transparent",
          }}>
            {row.map((cell, ci) => (
              <div key={ci} style={{
                flex: 1,
                padding: v ? "14px 20px" : "16px 28px",
                fontSize: v ? 26 : 28,
                color: ci === 0 ? props.textColor : props.textColor,
                fontWeight: ci === 0 || highlighted ? 600 : 400,
                textAlign: ci === 0 ? "left" : "center",
              }}>
                {cell}
              </div>
            ))}
          </div>
        );
      })}
    </div>
  );
};
