/**
 * 视频封面/缩略图模板
 *
 * 设计风格：简约纯白
 * - 白色背景，大标题
 * - 数据高亮使用品牌色
 * - 适合技术/知识类视频
 *
 * 【自定义点】: 修改 title, subtitle, highlights
 */

import { AbsoluteFill } from "remotion";

interface ThumbnailProps {
  aspectRatio?: "16:9" | "4:3" | "1:1";
  // 【自定义点】: 添加更多 props
  title?: string;
  subtitle?: string;
  highlights?: { value: string; label: string; color?: string }[];
}

export const Thumbnail = ({
  aspectRatio = "16:9",
  title = "视频标题",
  subtitle = "副标题或关键信息",
  highlights = [
    { value: "99%", label: "准确率", color: "#4CAF50" },
    { value: "10x", label: "效率提升", color: "#2196F3" },
    { value: "免费", label: "开源方案", color: "#FF9800" },
  ]
}: ThumbnailProps) => {

  // 根据比例调整字体大小
  const titleSize = aspectRatio === "1:1" ? 72 : 100;
  const subtitleSize = aspectRatio === "1:1" ? 28 : 36;
  const highlightSize = aspectRatio === "1:1" ? 48 : 64;

  return (
    <AbsoluteFill style={{
      backgroundColor: "#FFFFFF",
      padding: 40,
      fontFamily: "'PingFang SC', 'Microsoft YaHei', sans-serif"
    }}>
      {/* 主标题区域 */}
      <div style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        height: "60%"
      }}>
        <h1 style={{
          fontSize: titleSize,
          fontWeight: 800,
          color: "#1a1a1a",
          margin: 0,
          lineHeight: 1.2
        }}>
          {title}
        </h1>
        <p style={{
          fontSize: subtitleSize,
          color: "#666",
          marginTop: 16,
          fontWeight: 400
        }}>
          {subtitle}
        </p>
      </div>

      {/* 数据高亮区域 */}
      <div style={{
        display: "flex",
        gap: 40,
        marginTop: "auto"
      }}>
        {highlights.map((item, index) => (
          <div key={index} style={{ textAlign: "center" }}>
            <div style={{
              fontSize: highlightSize,
              fontWeight: 700,
              color: item.color || "#1a1a1a"
            }}>
              {item.value}
            </div>
            <div style={{
              fontSize: 20,
              color: "#999",
              marginTop: 4
            }}>
              {item.label}
            </div>
          </div>
        ))}
      </div>

      {/* 品牌角标 - 可选 */}
      {/*
      <div style={{
        position: "absolute",
        bottom: 40,
        right: 40,
        fontSize: 24,
        color: "#ccc"
      }}>
        @你的频道名
      </div>
      */}
    </AbsoluteFill>
  );
};

export default Thumbnail;
