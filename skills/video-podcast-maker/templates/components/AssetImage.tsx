import { AbsoluteFill, Img, interpolate, useCurrentFrame } from "remotion";
import type { VideoProps } from "../Root";
import { MediaSection } from "./MediaSection";
import { useAssets, getAsset, assetSrc } from "./useAssets";

/**
 * Manifest-aware image renderer with designed default layouts per role.
 *
 * Usage:
 *   <AssetImage props={props} id="hero_bg" role="background" />
 *   <AssetImage props={props} id="app_shot" role="inline" caption="…" />
 *
 * `id` resolves through assets/manifest.json (via --public-dir); pass `src`
 * instead to bypass the manifest. Renders nothing when the asset is absent
 * or unresolved, so compositions stay safe on text-only videos.
 */
export const AssetImage = ({
  props,
  id,
  src,
  role = "inline",
  caption,
  layout = "full",
  kenBurns = true,
  dim = 0.35,
  delay = 0,
}: {
  props: VideoProps;
  id?: string;
  src?: string;
  role?: "background" | "inline";
  caption?: string;
  layout?: "full" | "card";
  kenBurns?: boolean;
  dim?: number;
  delay?: number;
}) => {
  const manifest = useAssets();
  const frame = useCurrentFrame();

  const entry = id ? getAsset(manifest, id) : null;
  const resolvedSrc = src ?? (entry ? assetSrc(entry) : null);
  if (!resolvedSrc) return null;

  if (role === "background") {
    // Slow push-in over ~20s, clamped — subtle motion for static backgrounds
    const scale =
      kenBurns && props.enableAnimations
        ? interpolate(frame, [0, 600], [1.04, 1.14], {
            extrapolateRight: "clamp",
          })
        : 1;
    return (
      <AbsoluteFill>
        <Img
          src={resolvedSrc}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${scale})`,
          }}
        />
        {/* Scrim keeps foreground text readable on any photo */}
        <AbsoluteFill
          style={{
            background: `linear-gradient(180deg, rgba(0,0,0,${dim * 0.7}) 0%, rgba(0,0,0,${dim}) 100%)`,
          }}
        />
      </AbsoluteFill>
    );
  }

  return (
    <MediaSection
      props={props}
      src={resolvedSrc}
      caption={caption ?? entry?.credit}
      layout={layout}
      delay={delay}
    />
  );
};
