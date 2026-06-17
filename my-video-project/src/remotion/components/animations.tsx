import { useCurrentFrame, useVideoConfig, interpolate, spring, Easing } from "remotion";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import { none } from "@remotion/transitions/none";
import { evolvePath } from "@remotion/paths";

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

// --- Continuous animations (run throughout section lifetime) ---

// Floating drift — continuous vertical oscillation for decorative elements
export const useFloat = (
  amplitude = 12,
  periodFrames = 120,
  phaseOffset = 0,
) => {
  const frame = useCurrentFrame();
  const angle = ((frame + phaseOffset) / periodFrames) * Math.PI * 2;
  return {
    translateY: Math.sin(angle) * amplitude,
    translateX: Math.cos(angle * 0.7) * (amplitude * 0.4),
  };
};

// Pulsing scale — continuous subtle breathing for glows and orbs
export const usePulse = (
  minScale = 0.95,
  maxScale = 1.05,
  periodFrames = 90,
  phaseOffset = 0,
) => {
  const frame = useCurrentFrame();
  const t = ((frame + phaseOffset) / periodFrames) % 1;
  // Smooth sine wave between min and max
  const scale = minScale + (maxScale - minScale) * (0.5 + 0.5 * Math.sin(t * Math.PI * 2));
  return { scale };
};

// Gradient rotation — slowly rotating gradient angle for backgrounds
export const useGradientShift = (
  speed = 0.5, // degrees per frame
  startAngle = 135,
) => {
  const frame = useCurrentFrame();
  const angle = startAngle + frame * speed;
  return { angle: angle % 360 };
};

// Smooth opacity wave — for sequential glow/highlight effects
export const useOpacityWave = (
  periodFrames = 180,
  min = 0.3,
  max = 0.8,
  phaseOffset = 0,
) => {
  const frame = useCurrentFrame();
  const t = ((frame + phaseOffset) / periodFrames) % 1;
  return min + (max - min) * (0.5 + 0.5 * Math.sin(t * Math.PI * 2));
};

// --- Text reveal animations ---

// Word-by-word reveal — returns how many words to show at current frame
export const useTextReveal = (
  text: string,
  enabled: boolean,
  delay = 0,
  framesPerWord = 4,
) => {
  const frame = useCurrentFrame();

  if (!enabled) return { words: text.split(/\s+/), visibleCount: Infinity, progress: 1 };

  const words = text.split(/\s+/);
  const elapsed = Math.max(0, frame - delay);
  const visibleCount = Math.min(words.length, Math.floor(elapsed / framesPerWord) + 1);
  const progress = visibleCount / words.length;

  return { words, visibleCount, progress };
};

// Character-by-character reveal — for hero titles
export const useCharReveal = (
  text: string,
  enabled: boolean,
  delay = 0,
  framesPerChar = 2,
) => {
  const frame = useCurrentFrame();

  if (!enabled) return { chars: text.split(""), visibleCount: Infinity, progress: 1 };

  const chars = text.split("");
  const elapsed = Math.max(0, frame - delay);
  const visibleCount = Math.min(chars.length, Math.floor(elapsed / framesPerChar) + 1);
  const progress = visibleCount / chars.length;

  return { chars, visibleCount, progress };
};

// Stagger helper — compute delay for item at given index
export const staggerDelay = (index: number, baseDelay = 0, interval = 6) =>
  baseDelay + index * interval;

// --- SVG path draw-on animations ---

// Draw-on animation — progressively reveals an SVG path from 0% to 100%
// Returns strokeDasharray/strokeDashoffset to apply to a <path> element
export const useDrawOn = (
  path: string,
  enabled: boolean,
  delay = 0,
  durationFrames = 30,
  preset: SpringPreset = "gentle",
) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (!enabled || !path) return { progress: 1, strokeDasharray: "none", strokeDashoffset: 0 };

  const config = SPRING_PRESETS[preset];
  const progress = spring({ frame, fps, delay, config, durationInFrames: durationFrames });
  const evolved = evolvePath(progress, path);

  return {
    progress,
    strokeDasharray: evolved.strokeDasharray,
    strokeDashoffset: evolved.strokeDashoffset,
  };
};

// Multi-path staggered draw-on — animates an array of paths sequentially
export const useStaggeredDrawOn = (
  paths: string[],
  enabled: boolean,
  delay = 0,
  durationPerPath = 20,
  staggerInterval = 8,
  preset: SpringPreset = "gentle",
) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (!enabled) {
    return paths.map(() => ({ progress: 1, strokeDasharray: "none" as string, strokeDashoffset: 0 }));
  }

  const config = SPRING_PRESETS[preset];

  return paths.map((path, i) => {
    if (!path) return { progress: 1, strokeDasharray: "none", strokeDashoffset: 0 };
    const pathDelay = delay + i * staggerInterval;
    const progress = spring({ frame, fps, delay: pathDelay, config, durationInFrames: durationPerPath });
    const evolved = evolvePath(progress, path);
    return {
      progress,
      strokeDasharray: evolved.strokeDasharray,
      strokeDashoffset: evolved.strokeDashoffset,
    };
  });
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
