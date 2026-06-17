/**
 * Video Thumbnail Template — 宋韵美学风格
 *
 * 宣纸底色、黛蓝标题、胭脂印章、宋体字形
 * 适配 16:9 / 4:3 / 3:4 / 9:16 四种比例
 */

import { AbsoluteFill } from "remotion";

interface ThumbnailProps {
  aspectRatio?: "16:9" | "4:3" | "3:4" | "9:16";
  title?: string;
  subtitle?: string;
  tags?: string[];
  seal?: string;
}

const songFont = '"Songti SC", "STSong", "Noto Serif SC", serif';

// 宋韵配色
const colors = {
  bg: "#f7f4ef",
  primary: "#3a5a78",
  accent: "#a85c5c",
  text: "#2c2c2c",
  paper: "rgba(255,255,255,0.6)",
};

export const Thumbnail = ({
  aspectRatio = "16:9",
  title = "为何有人病，有人不病？",
  subtitle = "从现代医学到《黄帝内经》",
  tags = ["养生", "健康"],
  seal = "问道",
}: ThumbnailProps) => {
  const vertical = aspectRatio === "9:16";
  const tall = aspectRatio === "3:4";
  const compact = aspectRatio === "4:3";

  const titleSize = vertical ? 110 : tall ? 120 : compact ? 130 : 140;
  const subtitleSize = vertical ? 40 : tall ? 44 : compact ? 48 : 52;
  const tagSize = vertical ? 32 : tall ? 34 : compact ? 36 : 38;
  const sealSize = vertical ? 56 : tall ? 60 : compact ? 64 : 68;

  return (
    <AbsoluteFill style={{ background: colors.bg, fontFamily: songFont }}>
      {/* 淡墨晕染背景 */}
      <div
        style={{
          position: "absolute",
          inset: 0,
          background: `radial-gradient(ellipse at 25% 20%, ${colors.primary}08 0%, transparent 55%), radial-gradient(ellipse at 75% 80%, ${colors.accent}06 0%, transparent 50%)`,
        }}
      />

      {/* 顶部装饰线 */}
      <div style={{ position: "absolute", top: vertical ? 60 : 40, left: "8%", right: "8%", height: 1, background: `${colors.primary}20` }} />
      {/* 底部装饰线 */}
      <div style={{ position: "absolute", bottom: vertical ? 60 : 40, left: "8%", right: "8%", height: 1, background: `${colors.primary}20` }} />

      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: vertical ? "0 60px" : "0 80px",
          gap: vertical ? 28 : 24,
        }}
      >
        {/* 印章 */}
        <div
          style={{
            width: sealSize,
            height: sealSize,
            background: colors.accent,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            marginBottom: vertical ? 16 : 12,
            boxShadow: `0 4px 14px ${colors.accent}25`,
          }}
        >
          <span style={{ color: "#fff", fontSize: sealSize * 0.45, fontWeight: 700, letterSpacing: 2 }}>
            {seal}
          </span>
        </div>

        {/* Tags */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: 16, alignItems: "center", justifyContent: "center" }}>
          {tags.map((tag, i) => (
            <div
              key={i}
              style={{
                background: colors.paper,
                border: `1px solid ${colors.primary}25`,
                borderRadius: 4,
                padding: "10px 28px",
                fontSize: tagSize,
                fontWeight: 600,
                color: colors.primary,
                letterSpacing: 4,
              }}
            >
              {tag}
            </div>
          ))}
        </div>

        {/* Title */}
        <div
          style={{
            fontSize: titleSize,
            fontWeight: 700,
            letterSpacing: vertical ? 8 : 12,
            color: colors.primary,
            lineHeight: 1.35,
            textAlign: "center",
          }}
        >
          {title}
        </div>

        {/* Subtitle */}
        <div
          style={{
            fontSize: subtitleSize,
            fontWeight: 500,
            color: colors.text,
            letterSpacing: 4,
            textAlign: "center",
            opacity: 0.75,
            marginTop: vertical ? 8 : 4,
          }}
        >
          {subtitle}
        </div>
      </div>
    </AbsoluteFill>
  );
};

export default Thumbnail;
