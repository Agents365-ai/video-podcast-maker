import { useCurrentFrame, useVideoConfig, interpolate, spring, Easing } from "remotion";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import { none } from "@remotion/transitions/none";

// Spring presets for different animation feels
const SPRING_PRESETS = {
  gentle: { damping: 200, mass: 1 },
  snappy: { damping: 100, mass: 0.5 },
  bouncy: { damping: 80, mass: 0.8 },
} as const;

type SpringPreset = keyof typeof SPRING_PRESETS;

// Spring-based entrance animation with stagger and preset support
export const useEntrance = (
  enabled: boolean,
  delay = 0,
  preset: SpringPreset = "gentle",
) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (!enabled) return { opacity: 1, translateY: 0, scale: 1, rotate: 0 };

  const config = SPRING_PRESETS[preset];
  const progress = spring({ frame, fps, delay, config, durationInFrames: 30 });

  return {
    opacity: interpolate(progress, [0, 1], [0, 1]),
    translateY: interpolate(progress, [0, 1], [40, 0]),
    scale: interpolate(progress, [0, 1], [0.95, 1]),
    rotate: 0,
  };
};

// Exit animation — use with section duration to fade out at end
export const useExit = (
  enabled: boolean,
  sectionDuration: number,
  fadeFrames = 15,
) => {
  const frame = useCurrentFrame();

  if (!enabled) return { opacity: 1, translateY: 0, scale: 1 };

  const exitStart = Math.max(0, sectionDuration - fadeFrames);
  const progress = interpolate(frame, [exitStart, sectionDuration], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.inOut(Easing.ease),
  });

  return {
    opacity: interpolate(progress, [0, 1], [1, 0]),
    translateY: interpolate(progress, [0, 1], [0, -20]),
    scale: interpolate(progress, [0, 1], [1, 0.97]),
  };
};

// Animated number counter — interpolates from 0 to target value
export const useCounter = (target: number, delay = 0, durationFrames = 45) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = spring({ frame, fps, delay, config: { damping: 200 }, durationInFrames: durationFrames });
  return Math.round(interpolate(progress, [0, 1], [0, target]));
};

// Animated bar fill — returns 0-100 percentage
export const useBarFill = (targetPct: number, delay = 0, durationFrames = 40) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const progress = spring({ frame, fps, delay, config: { damping: 150 }, durationInFrames: durationFrames });
  return interpolate(progress, [0, 1], [0, targetPct]);
};

// Transition presentation mapper
export const getPresentation = (type: string) => {
  switch (type) {
    case "fade": return fade();
    case "slide": return slide({ direction: "from-right" });
    case "wipe": return wipe({ direction: "from-right" });
    case "none": return none();
    default: return fade();
  }
};
