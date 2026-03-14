import React from "react";
import { AbsoluteFill } from "remotion";

// 4K scaling wrapper - design at 1080p, auto-scale to 4K
export const Scale4K = ({ children }: { children: React.ReactNode }) => (
  <AbsoluteFill style={{ transform: "scale(2)", transformOrigin: "top left" }}>
    <div style={{ width: 1920, height: 1080, position: "relative", overflow: "hidden" }}>
      {children}
    </div>
  </AbsoluteFill>
);

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
export const PaddedLayout = ({
  children,
  bg,
  style,
}: {
  children: React.ReactNode;
  bg?: string;
  style?: React.CSSProperties;
}) => (
  <AbsoluteFill style={{ backgroundColor: bg || "#FFFFFF", padding: 40, ...style }}>
    {children}
  </AbsoluteFill>
);
