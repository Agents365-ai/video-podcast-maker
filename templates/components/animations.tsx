import { useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { fade } from "@remotion/transitions/fade";
import { slide } from "@remotion/transitions/slide";
import { wipe } from "@remotion/transitions/wipe";
import { none } from "@remotion/transitions/none";

// Spring-based entrance animation with stagger support
export const useEntrance = (enabled: boolean, delay = 0) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (!enabled) {
    return { opacity: 1, translateY: 0, scale: 1 };
  }

  const progress = spring({ frame, fps, delay, config: { damping: 200 }, durationInFrames: 30 });

  return {
    opacity: interpolate(progress, [0, 1], [0, 1]),
    translateY: interpolate(progress, [0, 1], [40, 0]),
    scale: interpolate(progress, [0, 1], [0.95, 1]),
  };
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
