import type { CSSProperties } from "react";
import { AbsoluteFill, OffthreadVideo } from "remotion";
import { useAssets, getAsset, assetSrc } from "./useAssets";

/**
 * Transparent animation overlay (Hyperframes renders, type "overlay").
 *
 * Place inside the section's Sequence so the overlay starts with the slide:
 *   <OverlayLayer id="growth_chart" />
 *
 * Format contract (see references/hyperframes-overlays.md): WebM VP9 with
 * alpha (yuva420p), 30 fps, 3840×2160, duration matching the section window.
 * WebM previews natively in Studio; `transparent` extracts alpha frames
 * during the actual render. Renders nothing when the asset is unresolved.
 */
export const OverlayLayer = ({
  id,
  src,
  style,
}: {
  id?: string;
  src?: string;
  style?: CSSProperties;
}) => {
  const manifest = useAssets();

  const entry = id ? getAsset(manifest, id) : null;
  const resolvedSrc = src ?? (entry ? assetSrc(entry) : null);
  if (!resolvedSrc) return null;

  return (
    <AbsoluteFill style={{ pointerEvents: "none", ...style }}>
      <OffthreadVideo
        src={resolvedSrc}
        transparent
        muted
        style={{ width: "100%", height: "100%" }}
      />
    </AbsoluteFill>
  );
};
