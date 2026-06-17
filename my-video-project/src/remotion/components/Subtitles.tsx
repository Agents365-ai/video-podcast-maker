/**
 * Subtitles — renders SRT subtitles directly inside Remotion.
 *
 * Two display modes:
 *   - "outline": text with CSS text-shadow outline
 *   - "background" (default): dark text on a semi-transparent light background bar
 *
 * Usage in Video.tsx (outside Scale4K, alongside ChapterProgressBar):
 *   <Subtitles src={staticFile("podcast_audio.srt")} />
 *   <Subtitles src={staticFile("podcast_audio.srt")} mode="outline" />
 *
 * The component positions itself at the bottom of the 4K frame,
 * above the progress bar, using absolute positioning.
 */

import React from "react";
import { useCurrentFrame, useVideoConfig, delayRender, continueRender } from "remotion";

interface SrtEntry {
  index: number;
  startMs: number;
  endMs: number;
  text: string;
}

// Parse SRT timestamp "HH:MM:SS,mmm" → milliseconds
const parseSrtTime = (t: string): number => {
  const [hms, ms] = t.trim().split(",");
  const [h, m, s] = hms.split(":").map(Number);
  return h * 3600000 + m * 60000 + s * 1000 + Number(ms);
};

// Parse SRT file content into entries
const parseSrt = (raw: string): SrtEntry[] => {
  const entries: SrtEntry[] = [];
  // Normalize line endings and split into blocks
  const blocks = raw.replace(/\r\n/g, "\n").replace(/\r/g, "\n").trim().split(/\n\n+/);
  for (const block of blocks) {
    const lines = block.trim().split("\n");
    if (lines.length < 3) continue;
    const index = parseInt(lines[0], 10);
    const timeParts = lines[1].split("-->");
    if (timeParts.length !== 2) continue;
    const startMs = parseSrtTime(timeParts[0]);
    const endMs = parseSrtTime(timeParts[1]);
    const text = lines.slice(2).join(" ").trim();
    if (text) entries.push({ index, startMs, endMs, text });
  }
  return entries;
};

// Hook: fetch and cache SRT content, gating Remotion render on completion.
//
// Without delayRender, the renderer starts emitting frames before the SRT
// fetch resolves, so the first ~half-second of every render has no subtitle
// overlay. delayRender returns a handle that blocks frame emission until
// continueRender(handle) is called. Cache hits resolve synchronously and
// release the handle immediately on the next tick.
const srtCache: Record<string, SrtEntry[]> = {};
const useSrt = (src: string): SrtEntry[] => {
  const [entries, setEntries] = React.useState<SrtEntry[]>(
    () => srtCache[src] ?? [],
  );
  const [handle] = React.useState(() =>
    delayRender(`Subtitles: loading ${src}`),
  );

  React.useEffect(() => {
    let cancelled = false;
    if (srtCache[src]) {
      setEntries(srtCache[src]);
      continueRender(handle);
      return () => {
        cancelled = true;
      };
    }
    fetch(src)
      .then((r) => r.text())
      .then((raw) => {
        if (cancelled) return;
        const parsed = parseSrt(raw);
        srtCache[src] = parsed;
        setEntries(parsed);
        continueRender(handle);
      })
      .catch((err) => {
        // Release the handle even on failure so Remotion doesn't hang.
        // The composition still renders without subtitles in that case.
        if (!cancelled) {
          console.warn(`Subtitles: failed to load ${src}`, err);
          continueRender(handle);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [src, handle]);

  return entries;
};

export const Subtitles = ({
  src,
  // Visual style — all sizes are in the 4K (3840x2160) pixel space
  // because this component sits OUTSIDE the Scale4K wrapper.
  mode = "background",      // "outline" = text-shadow outline, "background" = bg bar
  fontSize = 80,            // ~40px in 1080p design space × 2
  color = "#1a1a1a",
  outlineColor = "#ffffff",
  outlineWidth = 6,
  bgColor = "rgba(240, 240, 240, 0.85)", // light gray background for "background" mode
  bgPadding = "16px 40px",
  bgBorderRadius = 16,
  bottomOffset = 56,        // px from bottom of 4K frame
  maxWidth = 3400,          // max line width in 4K pixels
}: {
  src: string;
  mode?: "outline" | "background";
  fontSize?: number;
  color?: string;
  outlineColor?: string;
  outlineWidth?: number;
  bgColor?: string;
  bgPadding?: string;
  bgBorderRadius?: number;
  bottomOffset?: number;
  maxWidth?: number;
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const currentMs = (frame / fps) * 1000;

  const entries = useSrt(src);
  const current = entries.find(
    (e) => currentMs >= e.startMs && currentMs <= e.endMs
  );

  if (!current) return null;

  const isOutline = mode === "outline";

  const textStyle: React.CSSProperties = {
    maxWidth,
    textAlign: "center",
    fontFamily: '"PingFang SC", "Noto Sans SC", sans-serif',
    fontSize,
    fontWeight: 600,
    color,
    lineHeight: 1.4,
    ...(isOutline
      ? {
          textShadow: [
            `${outlineWidth}px 0 0 ${outlineColor}`,
            `-${outlineWidth}px 0 0 ${outlineColor}`,
            `0 ${outlineWidth}px 0 ${outlineColor}`,
            `0 -${outlineWidth}px 0 ${outlineColor}`,
            `${outlineWidth}px ${outlineWidth}px 0 ${outlineColor}`,
            `-${outlineWidth}px ${outlineWidth}px 0 ${outlineColor}`,
            `${outlineWidth}px -${outlineWidth}px 0 ${outlineColor}`,
            `-${outlineWidth}px -${outlineWidth}px 0 ${outlineColor}`,
          ].join(", "),
        }
      : {
          backgroundColor: bgColor,
          padding: bgPadding,
          borderRadius: bgBorderRadius,
        }),
  };

  return (
    <div
      style={{
        position: "absolute",
        bottom: bottomOffset,
        left: 0,
        right: 0,
        display: "flex",
        justifyContent: "center",
        alignItems: "flex-end",
        pointerEvents: "none",
        zIndex: 100,
      }}
    >
      <div style={textStyle}>
        {current.text}
      </div>
    </div>
  );
};
