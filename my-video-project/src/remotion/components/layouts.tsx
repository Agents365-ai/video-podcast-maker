import React from "react";
import { AbsoluteFill } from "remotion";

// 4K scaling wrapper - design at half resolution, auto-scale to 4K
// Horizontal: 1920x1080 → scale(2) → 3840x2160
// Vertical: 1080x1920 → scale(2) → 2160x3840
export const Scale4K = ({
  children,
  orientation = "horizontal",
}: {
  children: React.ReactNode;
  orientation?: "horizontal" | "vertical";
}) => {
  const isVertical = orientation === "vertical";
  const w = isVertical ? 1080 : 1920;
  const h = isVertical ? 1920 : 1080;
  return (
    <AbsoluteFill style={{ transform: "scale(2)", transformOrigin: "top left" }}>
      <div style={{ width: w, height: h, position: "relative", overflow: "hidden" }}>
        {children}
      </div>
    </AbsoluteFill>
  );
};

// Full-bleed layout - no padding, for hero titles and charts
export const FullBleedLayout = ({
  children,
  bg,
  style,
}: {
  children: React.ReactNode;
  bg?: string;
  style?: React.CSSProperties;
}) => (
  <AbsoluteFill style={{ backgroundColor: bg || "#FFFFFF", padding: 0, ...style }}>
    {children}
  </AbsoluteFill>
);

// Padded layout - with padding, for body content
// Vertical uses narrower horizontal padding for taller aspect ratio
export const PaddedLayout = ({
  children,
  bg,
  style,
  orientation = "horizontal",
}: {
  children: React.ReactNode;
  bg?: string;
  style?: React.CSSProperties;
  orientation?: "horizontal" | "vertical";
}) => {
  const padding = orientation === "vertical" ? "20px 24px" : "20px 30px";
  return (
    <AbsoluteFill style={{ backgroundColor: bg || "#FFFFFF", padding, ...style }}>
      {children}
    </AbsoluteFill>
  );
};
