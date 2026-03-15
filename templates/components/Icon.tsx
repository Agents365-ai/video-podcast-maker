import { useCurrentFrame, interpolate } from "remotion";
import { ICON_MAP, isEmoji } from "./iconMap";

type AnimationType = "none" | "entrance" | "pulse" | "bounce";

interface IconProps {
  name: string;
  size?: number;
  color?: string;
  animate?: AnimationType;
  delay?: number;
  strokeWidth?: number;
}

export const Icon = ({
  name,
  size = 56,
  color = "currentColor",
  animate = "entrance",
  delay = 0,
  strokeWidth = 2,
}: IconProps) => {
  const frame = useCurrentFrame();
  const f = Math.max(0, frame - delay);

  // Animation values
  let opacity = 1;
  let scale = 1;
  let translateY = 0;

  if (animate === "entrance") {
    opacity = interpolate(f, [0, 12], [0, 1], { extrapolateRight: "clamp" });
    scale = interpolate(f, [0, 15], [0.5, 1], { extrapolateRight: "clamp" });
    translateY = interpolate(f, [0, 15], [20, 0], { extrapolateRight: "clamp" });
  } else if (animate === "pulse") {
    scale = interpolate(f % 60, [0, 30, 60], [1, 1.08, 1]);
  } else if (animate === "bounce") {
    opacity = interpolate(f, [0, 8], [0, 1], { extrapolateRight: "clamp" });
    const bounce = interpolate(f, [0, 10, 20, 25], [40, -10, 5, 0], { extrapolateRight: "clamp" });
    translateY = bounce;
    scale = interpolate(f, [0, 10, 20], [0.3, 1.1, 1], { extrapolateRight: "clamp" });
  }

  const style: React.CSSProperties = {
    display: "inline-flex",
    alignItems: "center",
    justifyContent: "center",
    width: size,
    height: size,
    opacity,
    transform: `translateY(${translateY}px) scale(${scale})`,
  };

  // Emoji: render directly
  if (isEmoji(name)) {
    return (
      <span style={{ ...style, fontSize: size * 0.85, lineHeight: 1 }}>
        {name}
      </span>
    );
  }

  // Lucide icon: lookup and render
  const LucideIcon = ICON_MAP[name.toLowerCase()];
  if (LucideIcon) {
    return (
      <span style={style}>
        <LucideIcon size={size} color={color} strokeWidth={strokeWidth} />
      </span>
    );
  }

  // Fallback: show name as text (for debugging)
  return (
    <span style={{ ...style, fontSize: size * 0.4, color: "#999" }}>
      [{name}]
    </span>
  );
};
