import { useCallback, useEffect, useState } from "react";
import { staticFile, cancelRender, continueRender, delayRender } from "remotion";
import { Lottie } from "@remotion/lottie";
import type { LottieAnimationData } from "@remotion/lottie";
import type { CSSProperties } from "react";
import { useEntrance } from "./animations";

/**
 * LottieAnimation — Wrapper for @remotion/lottie with automatic loading
 * from staticFile() or remote URL. Handles delayRender/continueRender
 * lifecycle for reliable frame-accurate playback.
 *
 * Usage with local file (place JSON in the --public-dir directory):
 *   <LottieAnimation src="animations/brain.json" />
 *
 * Usage with remote URL (must support CORS):
 *   <LottieAnimation src="https://assets.lottiefiles.com/..." />
 *
 * Usage with pre-loaded data:
 *   <LottieAnimation animationData={myData} />
 */

export const LottieAnimation = ({
  src,
  animationData: externalData,
  loop = false,
  direction = "forward",
  playbackRate = 1,
  style,
  width,
  height,
  enableEntrance = false,
  entranceDelay = 0,
}: {
  /** Path to JSON file (resolved via staticFile) or full URL */
  src?: string;
  /** Pre-loaded animation data (takes precedence over src) */
  animationData?: LottieAnimationData;
  loop?: boolean;
  direction?: "forward" | "backward";
  playbackRate?: number;
  style?: CSSProperties;
  width?: number | string;
  height?: number | string;
  /** Wrap in entrance animation */
  enableEntrance?: boolean;
  entranceDelay?: number;
}) => {
  const [data, setData] = useState<LottieAnimationData | null>(
    externalData ?? null,
  );
  const [handle] = useState(() =>
    !externalData && src ? delayRender("Loading Lottie animation") : null,
  );

  const entrance = useEntrance(enableEntrance, entranceDelay, "gentle");

  const fetchAnimation = useCallback(async () => {
    if (externalData || !src) return;

    try {
      // Determine if src is a URL or a staticFile path
      const url = src.startsWith("http://") || src.startsWith("https://")
        ? src
        : staticFile(src);

      const response = await fetch(url);
      const json = await response.json();
      setData(json);
      if (handle !== null) continueRender(handle);
    } catch (err) {
      if (handle !== null) cancelRender(err);
    }
  }, [src, externalData, handle]);

  useEffect(() => {
    fetchAnimation();
  }, [fetchAnimation]);

  if (!data) return null;

  const containerStyle: CSSProperties = {
    width: width ?? "100%",
    height: height ?? "auto",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    ...(enableEntrance
      ? { opacity: entrance.opacity, transform: `translateY(${entrance.translateY}px)` }
      : {}),
    ...style,
  };

  return (
    <div style={containerStyle}>
      <Lottie
        animationData={data}
        loop={loop}
        direction={direction}
        playbackRate={playbackRate}
        style={{ width: "100%", height: "100%" }}
      />
    </div>
  );
};
