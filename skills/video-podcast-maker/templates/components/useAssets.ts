import { useState, useEffect } from "react";
import { staticFile, delayRender, continueRender } from "remotion";

export interface AssetEntry {
  id: string;
  section: string;
  type: "image" | "video" | "overlay" | "audio" | "icon" | "font";
  role: "background" | "inline" | "broll" | "overlay" | "bgm" | "sfx";
  source: "user" | "seek" | "imagen" | "videogen" | "hyperframes";
  status: "planned" | "pending_confirmation" | "resolved" | "failed";
  path?: string;
  license?: string;
  prompt?: string;
  credit?: string;
  alpha?: boolean;
  duration_s?: number;
  fps?: number;
}

export interface AssetManifest {
  schema_version: number;
  assets: AssetEntry[];
}

const EMPTY: AssetManifest = { schema_version: 1, assets: [] };

// Per-URL cache so each --public-dir gets its own manifest
const cache = new Map<string, AssetManifest>();
const pending = new Map<string, Promise<AssetManifest>>();

function fetchManifest(): Promise<AssetManifest> {
  const url = staticFile("assets/manifest.json");
  if (!pending.has(url)) {
    pending.set(
      url,
      fetch(url)
        .then((r) => (r.ok ? r.json() : EMPTY))
        // Text-only videos have no manifest — degrade to empty, never block
        .catch(() => EMPTY)
        .then((data: AssetManifest) => {
          cache.set(url, data);
          return data;
        }),
    );
  }
  return pending.get(url)!;
}

/**
 * Load assets/manifest.json at runtime via staticFile().
 * Works with --public-dir; a missing manifest resolves to an empty one.
 */
export const useAssets = (): AssetManifest => {
  const url = staticFile("assets/manifest.json");
  const cached = cache.get(url) ?? null;
  const [manifest, setManifest] = useState<AssetManifest | null>(cached);
  const [handle] = useState(() =>
    cached ? null : delayRender("Loading assets/manifest.json"),
  );

  useEffect(() => {
    if (cached) {
      setManifest(cached);
      return;
    }
    fetchManifest().then((data) => {
      setManifest(data);
      if (handle !== null) continueRender(handle);
    });
  }, [handle, cached]);

  return manifest ?? EMPTY;
};

/** Look up one resolved asset by id. Returns null if absent or unresolved. */
export const getAsset = (
  manifest: AssetManifest,
  id: string,
): AssetEntry | null => {
  const a = manifest.assets.find((e) => e.id === id);
  return a && a.status === "resolved" && a.path ? a : null;
};

/** All resolved assets for a section, optionally filtered by role. */
export const getSectionAssets = (
  manifest: AssetManifest,
  section: string,
  role?: AssetEntry["role"],
): AssetEntry[] =>
  manifest.assets.filter(
    (a) =>
      a.section === section &&
      a.status === "resolved" &&
      a.path &&
      (role === undefined || a.role === role),
  );

/** staticFile() URL for a resolved asset entry. */
export const assetSrc = (entry: AssetEntry): string => staticFile(entry.path!);
