import { useState, useEffect } from "react";
import { staticFile, delayRender, continueRender } from "remotion";

export interface TimingSection {
  name: string;
  label?: string;
  start_time: number;
  end_time: number;
  duration: number;
  start_frame: number;
  duration_frames: number;
  is_silent?: boolean;
}

export interface TimingData {
  total_duration: number;
  fps: number;
  total_frames: number;
  speech_rate?: string;
  sections: TimingSection[];
}

// Per-URL cache so each --public-dir gets its own timing data
const cache = new Map<string, TimingData>();
const pending = new Map<string, Promise<TimingData>>();

function fetchTiming(): Promise<TimingData> {
  const url = staticFile("timing.json");
  if (!pending.has(url)) {
    pending.set(
      url,
      fetch(url)
        .then((r) => r.json())
        .then((data: TimingData) => {
          cache.set(url, data);
          return data;
        }),
    );
  }
  return pending.get(url)!;
}

/**
 * Load timing.json at runtime via staticFile().
 * Works with --public-dir so each video can have its own timing data.
 * Uses delayRender/continueRender to block rendering until loaded.
 */
export const useTiming = (): TimingData => {
  const url = staticFile("timing.json");
  const cached = cache.get(url) ?? null;
  const [timing, setTiming] = useState<TimingData | null>(cached);
  const [handle] = useState(() =>
    cached ? null : delayRender("Loading timing.json"),
  );

  useEffect(() => {
    if (cached) {
      setTiming(cached);
      return;
    }
    fetchTiming().then((data) => {
      setTiming(data);
      if (handle !== null) continueRender(handle);
    });
  }, [handle, cached]);

  // Return placeholder while loading (render is delayed anyway)
  if (!timing) {
    return { total_duration: 0, fps: 30, total_frames: 1, sections: [] };
  }
  return timing;
};

/**
 * Standalone fetch for use in calculateMetadata (non-hook context).
 * Returns the cached value if already fetched.
 */
export const fetchTimingData = (): Promise<TimingData> => fetchTiming();
