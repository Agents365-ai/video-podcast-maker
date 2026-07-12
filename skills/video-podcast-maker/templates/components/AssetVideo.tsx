import { AbsoluteFill, OffthreadVideo } from "remotion";
import type { VideoProps } from "../Root";
import { useEntrance } from "./animations";
import { useAssets, getAsset, assetSrc } from "./useAssets";

/**
 * Manifest-aware B-roll renderer. Muted by default — narration audio is the
 * master clock and the only audio track until the Step 11 BGM mix.
 *
 * Usage:
 *   <AssetVideo props={props} id="city_broll" role="background" />
 *   <AssetVideo props={props} id="demo_clip" role="inline" />
 *
 * Renders nothing when the asset is absent or unresolved.
 */
export const AssetVideo = ({
  props,
  id,
  src,
  role = "inline",
  dim = 0.35,
  muted = true,
  delay = 0,
}: {
  props: VideoProps;
  id?: string;
  src?: string;
  role?: "background" | "inline";
  dim?: number;
  muted?: boolean;
  delay?: number;
}) => {
  const manifest = useAssets();
  const a = useEntrance(props.enableAnimations, delay, "gentle");

  const entry = id ? getAsset(manifest, id) : null;
  const resolvedSrc = src ?? (entry ? assetSrc(entry) : null);
  if (!resolvedSrc) return null;

  if (role === "background") {
    return (
      <AbsoluteFill>
        <OffthreadVideo
          src={resolvedSrc}
          muted={muted}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
        <AbsoluteFill
          style={{
            background: `linear-gradient(180deg, rgba(0,0,0,${dim * 0.7}) 0%, rgba(0,0,0,${dim}) 100%)`,
          }}
        />
      </AbsoluteFill>
    );
  }

  const c = props.primaryColor;
  return (
    <div
      style={{
        width: "100%",
        borderRadius: 24,
        overflow: "hidden",
        border: `3px solid ${c}30`,
        boxShadow: `0 8px 32px ${c}15, 0 16px 48px rgba(0,0,0,0.08)`,
        opacity: a.opacity,
        transform: `translateY(${a.translateY}px) scale(${a.scale})`,
      }}
    >
      <OffthreadVideo
        src={resolvedSrc}
        muted={muted}
        style={{ width: "100%", display: "block" }}
      />
    </div>
  );
};
