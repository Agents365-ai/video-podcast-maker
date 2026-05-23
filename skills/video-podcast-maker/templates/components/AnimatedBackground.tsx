/**
 * AnimatedBackground — composable background layers for visual depth
 *
 * Usage: Stack one or more background elements behind section content.
 * Each is position:absolute and fills its container.
 *
 * <FullBleedLayout bg="#fff">
 *   <MovingGradient color1={primaryColor} color2={accentColor} />
 *   <FloatingShapes color={primaryColor} count={5} />
 *   <GridPattern color={primaryColor} />
 *   {content}
 * </FullBleedLayout>
 */

import { useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { useFloat, usePulse, useGradientShift, useOpacityWave } from "./animations";

// --- Moving Gradient Background ---
// Slowly rotating gradient that adds subtle motion to any section
export const MovingGradient = ({
  color1 = "#4f6ef7",
  color2 = "#FF6B6B",
  opacity = 0.08,
  speed = 0.3,
}: {
  color1?: string;
  color2?: string;
  opacity?: number;
  speed?: number;
}) => {
  const { angle } = useGradientShift(speed);

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        background: `linear-gradient(${angle}deg, ${color1}${Math.round(opacity * 255).toString(16).padStart(2, "0")}, transparent 50%, ${color2}${Math.round(opacity * 255).toString(16).padStart(2, "0")})`,
        pointerEvents: "none",
      }}
    />
  );
};

// --- Floating Shapes ---
// Gentle drifting geometric shapes for depth and visual interest
const SHAPE_CONFIGS = [
  { size: 180, x: 85, y: 15, period: 140, phase: 0 },
  { size: 120, x: 10, y: 75, period: 160, phase: 40 },
  { size: 90, x: 70, y: 80, period: 130, phase: 80 },
  { size: 200, x: 5, y: 20, period: 170, phase: 20 },
  { size: 60, x: 50, y: 10, period: 110, phase: 60 },
  { size: 140, x: 90, y: 55, period: 150, phase: 100 },
  { size: 70, x: 30, y: 90, period: 120, phase: 30 },
];

export const FloatingShapes = ({
  color = "#4f6ef7",
  count = 5,
  opacity = 0.06,
  shape = "circle",
}: {
  color?: string;
  count?: number;
  opacity?: number;
  shape?: "circle" | "hexagon" | "ring";
}) => {
  const configs = SHAPE_CONFIGS.slice(0, Math.min(count, SHAPE_CONFIGS.length));

  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden", pointerEvents: "none" }}>
      {configs.map((cfg, i) => (
        <FloatingShape key={i} config={cfg} color={color} opacity={opacity} shape={shape} />
      ))}
    </div>
  );
};

const FloatingShape = ({
  config,
  color,
  opacity,
  shape,
}: {
  config: typeof SHAPE_CONFIGS[0];
  color: string;
  opacity: number;
  shape: "circle" | "hexagon" | "ring";
}) => {
  const { translateY, translateX } = useFloat(15, config.period, config.phase);
  const { scale } = usePulse(0.9, 1.1, config.period * 1.3, config.phase);

  const borderRadius = shape === "circle" ? "50%" : shape === "hexagon" ? "25%" : "50%";
  const bg = shape === "ring" ? "transparent" : color;
  const border = shape === "ring" ? `3px solid ${color}` : "none";

  return (
    <div
      style={{
        position: "absolute",
        left: `${config.x}%`,
        top: `${config.y}%`,
        width: config.size,
        height: config.size,
        borderRadius,
        backgroundColor: bg,
        border,
        opacity,
        transform: `translate(${translateX}px, ${translateY}px) scale(${scale})`,
        filter: "blur(1px)",
      }}
    />
  );
};

// --- Grid / Dot Pattern ---
// Subtle repeating pattern overlay for texture
export const GridPattern = ({
  color = "#4f6ef7",
  opacity = 0.04,
  spacing = 60,
  dotSize = 2,
  variant = "dots",
}: {
  color?: string;
  opacity?: number;
  spacing?: number;
  dotSize?: number;
  variant?: "dots" | "lines" | "crosses";
}) => {
  let backgroundImage: string;

  if (variant === "dots") {
    backgroundImage = `radial-gradient(circle, ${color} ${dotSize}px, transparent ${dotSize}px)`;
  } else if (variant === "lines") {
    backgroundImage = `
      linear-gradient(${color}${Math.round(opacity * 255).toString(16).padStart(2, "0")} 1px, transparent 1px),
      linear-gradient(90deg, ${color}${Math.round(opacity * 255).toString(16).padStart(2, "0")} 1px, transparent 1px)
    `;
  } else {
    // crosses
    backgroundImage = `
      radial-gradient(circle, ${color} ${dotSize}px, transparent ${dotSize}px),
      linear-gradient(${color}${Math.round(opacity * 255 * 0.5).toString(16).padStart(2, "0")} 1px, transparent 1px),
      linear-gradient(90deg, ${color}${Math.round(opacity * 255 * 0.5).toString(16).padStart(2, "0")} 1px, transparent 1px)
    `;
  }

  return (
    <div
      style={{
        position: "absolute",
        inset: 0,
        backgroundImage,
        backgroundSize: variant === "dots" ? `${spacing}px ${spacing}px` : `${spacing}px ${spacing}px`,
        opacity: variant === "dots" ? opacity : 1,
        pointerEvents: "none",
      }}
    />
  );
};

// --- Glow Orb ---
// Large pulsing color orb for focal point emphasis
export const GlowOrb = ({
  color = "#4f6ef7",
  size = 400,
  x = "50%",
  y = "40%",
  opacity = 0.12,
  blur = 80,
}: {
  color?: string;
  size?: number;
  x?: string;
  y?: string;
  opacity?: number;
  blur?: number;
}) => {
  const { scale } = usePulse(0.85, 1.15, 150);
  const pulseOpacity = useOpacityWave(180, opacity * 0.7, opacity);

  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        width: size,
        height: size,
        borderRadius: "50%",
        background: `radial-gradient(circle, ${color}, transparent 70%)`,
        opacity: pulseOpacity,
        transform: `translate(-50%, -50%) scale(${scale})`,
        filter: `blur(${blur}px)`,
        pointerEvents: "none",
      }}
    />
  );
};

// --- Decorative Accent Line ---
// Animated line that grows from center, good for section dividers
export const AccentLine = ({
  color = "#4f6ef7",
  width = 120,
  thickness = 3,
  delay = 10,
  position = "top",
}: {
  color?: string;
  width?: number;
  thickness?: number;
  delay?: number;
  position?: "top" | "bottom" | "center";
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = spring({ frame, fps, delay, config: { damping: 200 }, durationInFrames: 30 });

  const scaleX = interpolate(progress, [0, 1], [0, 1]);
  const top = position === "top" ? 0 : position === "center" ? "50%" : undefined;
  const bottom = position === "bottom" ? 0 : undefined;

  return (
    <div
      style={{
        position: "absolute",
        left: "50%",
        top,
        bottom,
        width,
        height: thickness,
        borderRadius: thickness,
        background: `linear-gradient(90deg, transparent, ${color}, transparent)`,
        transform: `translateX(-50%) scaleX(${scaleX})`,
        pointerEvents: "none",
      }}
    />
  );
};

