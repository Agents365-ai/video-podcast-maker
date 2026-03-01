/**
 * Video Thumbnail Template — Fill-the-Frame Design
 *
 * Dark gradient background, large text filling the entire frame.
 * Optimized for Bilibili mobile feed (~170px display width).
 *
 * Customize: title, subtitle, tags, icons
 */

import { AbsoluteFill } from "remotion";

interface ThumbnailProps {
  aspectRatio?: "16:9" | "4:3";
  title?: string;
  subtitle?: string;
  tags?: string[];
  icons?: string[];
  background?: string;
}

export const Thumbnail = ({
  aspectRatio = "16:9",
  title = "大标题占满",
  subtitle = "副标题铺满宽度",
  tags = ["标签A", "标签B"],
  icons = ["🚀", "⚡"],
  background = "linear-gradient(135deg, #0f0c29, #302b63, #24243e)",
}: ThumbnailProps) => {
  const isWide = aspectRatio === "16:9";
  const titleSize = isWide ? 260 : 220;
  const subtitleSize = isWide ? 120 : 100;
  const tagSize = 80;
  const iconSize = 140;

  return (
    <AbsoluteFill style={{
      background,
      fontFamily: "'PingFang SC', 'Noto Sans SC', 'Source Han Sans SC', sans-serif",
    }}>
      {/* 4K scale(2) wrapper */}
      <AbsoluteFill style={{
        transform: "scale(2)",
        transformOrigin: "top left",
        width: "50%",
        height: "50%",
      }}>
        <div style={{
          position: "absolute",
          inset: 0,
          padding: 20,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
        }}>
          {/* Tags */}
          {tags.length > 0 && (
            <div style={{ display: "flex", gap: 16, marginBottom: 24 }}>
              {tags.map((tag, i) => (
                <div key={i} style={{
                  background: "rgba(249,115,22,0.25)",
                  border: "3px solid rgba(249,115,22,0.4)",
                  borderRadius: 24,
                  padding: "12px 28px",
                  fontSize: tagSize,
                  fontWeight: 700,
                  color: "#fb923c",
                }}>{tag}</div>
              ))}
            </div>
          )}

          {/* Title — fills width */}
          <div style={{
            fontSize: titleSize,
            fontWeight: 900,
            letterSpacing: 4,
            color: "#fff",
            lineHeight: 1.1,
            width: "100%",
          }}>
            {title}
          </div>

          {/* Subtitle — fills width */}
          <div style={{
            fontSize: subtitleSize,
            fontWeight: 700,
            color: "rgba(255,255,255,0.7)",
            marginTop: 16,
            width: "100%",
          }}>
            {subtitle}
          </div>

          {/* Icons */}
          {icons.length > 0 && (
            <div style={{ display: "flex", gap: 24, marginTop: 32 }}>
              {icons.map((icon, i) => (
                <span key={i} style={{ fontSize: iconSize }}>{icon}</span>
              ))}
            </div>
          )}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export default Thumbnail;
