/**
 * Remotion 视频组件模板 - 支持 Studio 可视化编辑
 *
 * 使用说明：
 * 1. 将此文件复制到项目的 src/ 目录
 * 2. 根据需要修改 SectionComponent 中的 section 渲染逻辑
 * 3. 确保 timing.json 和 podcast_audio.wav 已生成
 * 4. 在 Remotion Studio 右侧面板可实时调整样式
 */

import { useCurrentFrame, Audio, Sequence, staticFile, AbsoluteFill, interpolate, spring, useVideoConfig } from "remotion";
import timing from "../public/timing.json";
import type { VideoProps } from "./Root";

// 4K 缩放包装器 - 所有内容使用 1080p 设计，自动放大到 4K
const Scale4K = ({ children }: { children: React.ReactNode }) => (
  <AbsoluteFill style={{ transform: "scale(2)", transformOrigin: "top left" }}>
    <div style={{ width: 1920, height: 1080, position: "relative", overflow: "hidden" }}>
      {children}
    </div>
  </AbsoluteFill>
);

// 全出血布局 - 无内边距，适合大标题和图表
const FullBleedLayout = ({
  children,
  bg,
  style,
}: {
  children: React.ReactNode;
  bg?: string;
  style?: React.CSSProperties;
}) => (
  <AbsoluteFill style={{ backgroundColor: bg || "#FFFFFF", padding: 0, ...style }}>
    {children}
  </AbsoluteFill>
);

// 标准布局 - 带内边距，适合正文内容
const PaddedLayout = ({
  children,
  bg,
  style,
}: {
  children: React.ReactNode;
  bg?: string;
  style?: React.CSSProperties;
}) => (
  <AbsoluteFill style={{ backgroundColor: bg || "#FFFFFF", padding: 40, ...style }}>
    {children}
  </AbsoluteFill>
);

// 入场动画 Hook
const useEntrance = (enabled: boolean) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  if (!enabled) {
    return { opacity: 1, translateY: 0 };
  }

  const opacity = interpolate(frame, [0, 15], [0, 1], { extrapolateRight: "clamp" });
  const translateY = spring({ frame, fps, from: 30, to: 0, durationInFrames: 20 });

  return { opacity, translateY };
};

// 章节进度条组件 (matches Superpowers reference style)
// Renders at native 4K resolution (outside scale(2) wrapper)
const ChapterProgressBar = ({
  props,
  chapters,
}: {
  props: VideoProps;
  chapters: typeof timing.sections;
}) => {
  const frame = useCurrentFrame();
  const totalFrames = timing.total_frames;
  const progress = frame / totalFrames;

  if (!props.showProgressBar) return null;

  return (
    <div
      style={{
        position: "absolute",
        bottom: 0,
        left: 0,
        right: 0,
        height: props.progressBarHeight,
        background: "#fff",
        borderTop: "2px solid #e5e7eb",
        display: "flex",
        alignItems: "center",
        padding: "0 60px",
        gap: 20,
        fontFamily: "PingFang SC, Microsoft YaHei, sans-serif",
      }}
    >
      {chapters.map((ch) => {
        const chStart = ch.start_frame / totalFrames;
        const chEnd = (ch.start_frame + ch.duration_frames) / totalFrames;
        const isActive = progress >= chStart && progress < chEnd;
        const isPast = progress >= chEnd;
        const chProgress = isActive ? (progress - chStart) / (chEnd - chStart) : isPast ? 1 : 0;

        return (
          <div
            key={ch.name}
            style={{
              flex: ch.duration_frames,
              height: 76,
              borderRadius: 38,
              position: "relative",
              overflow: "hidden",
              background: isActive ? props.progressActiveColor : isPast ? "#f3f4f6" : "#f9fafb",
              border: isActive ? "none" : "2px solid #e5e7eb",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {isActive && (
              <div
                style={{
                  position: "absolute",
                  left: 0,
                  top: 0,
                  bottom: 0,
                  width: `${chProgress * 100}%`,
                  background: "rgba(255,255,255,0.25)",
                  borderRadius: 38,
                }}
              />
            )}
            <span
              style={{
                position: "relative",
                zIndex: 1,
                color: isActive ? "#fff" : isPast ? "#374151" : "#9ca3af",
                fontSize: props.progressFontSize,
                fontWeight: isActive ? 700 : 500,
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
                padding: "0 20px",
              }}
            >
              {ch.label || ch.name}
            </span>
          </div>
        );
      })}
      {/* Bottom progress line */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          height: 5,
          background: "#e5e7eb",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${progress * 100}%`,
            background: props.progressActiveColor,
          }}
        />
      </div>
    </div>
  );
};

// Section 渲染组件 - 根据 section 名称渲染不同内容
// 【自定义点】: 在这里添加你的 section 渲染逻辑
const SectionComponent = ({
  section,
  props,
}: {
  section: typeof timing.sections[0];
  props: VideoProps;
}) => {
  const { opacity, translateY } = useEntrance(props.enableAnimations);
  const animStyle = { opacity, transform: `translateY(${translateY}px)` };

  switch (section.name) {
    // Reference font sizes (1080p design space):
    // Hero title: 72-120px/800wt, Section title: 72-80px/700-800wt
    // Subtitle: 30-40px, Card title: 34-38px, Body: 26-34px, Tags: 20-26px

    case "hero":
      return (
        <FullBleedLayout bg={props.backgroundColor}>
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              alignItems: "center",
              textAlign: "center",
              ...animStyle,
            }}
          >
            <h1
              style={{
                fontSize: props.titleSize,
                fontWeight: 800,
                color: props.primaryColor,
              }}
            >
              视频标题
            </h1>
            <p
              style={{
                fontSize: props.subtitleSize,
                color: props.textColor,
                marginTop: 20,
                opacity: 0.5,
                fontWeight: 500,
              }}
            >
              副标题或引导语
            </p>
          </div>
        </FullBleedLayout>
      );

    case "overview":
      return (
        <PaddedLayout bg={props.backgroundColor}>
          <div
            style={{
              position: "absolute",
              inset: 0,
              padding: "80px 100px",
              display: "flex",
              flexDirection: "column",
              ...animStyle,
            }}
          >
            <h2
              style={{
                fontSize: 80,
                fontWeight: 700,
                marginBottom: 12,
                color: props.primaryColor,
              }}
            >
              今天的内容
            </h2>
            <p style={{ fontSize: 30, color: "rgba(0,0,0,0.5)", marginBottom: 40 }}>
              Section description here
            </p>
            <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: 28, width: "100%", maxWidth: 800 }}>
                <div style={{
                  background: "rgba(0,0,0,0.02)", border: "1px solid rgba(0,0,0,0.08)",
                  borderRadius: 20, padding: "32px 40px", display: "flex", alignItems: "center", gap: 24,
                }}>
                  <div style={{ fontSize: 52 }}>💡</div>
                  <div style={{ fontSize: 34, fontWeight: 600, color: props.textColor }}>要点一</div>
                </div>
                <div style={{
                  background: "rgba(0,0,0,0.02)", border: "1px solid rgba(0,0,0,0.08)",
                  borderRadius: 20, padding: "32px 40px", display: "flex", alignItems: "center", gap: 24,
                }}>
                  <div style={{ fontSize: 52 }}>🎯</div>
                  <div style={{ fontSize: 34, fontWeight: 600, color: props.textColor }}>要点二</div>
                </div>
                <div style={{
                  background: "rgba(0,0,0,0.02)", border: "1px solid rgba(0,0,0,0.08)",
                  borderRadius: 20, padding: "32px 40px", display: "flex", alignItems: "center", gap: 24,
                }}>
                  <div style={{ fontSize: 52 }}>✅</div>
                  <div style={{ fontSize: 34, fontWeight: 600, color: props.textColor }}>要点三</div>
                </div>
              </div>
            </div>
          </div>
        </PaddedLayout>
      );

    case "summary":
      return (
        <FullBleedLayout bg={props.backgroundColor}>
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              padding: "80px 100px",
              ...animStyle,
            }}
          >
            <div
              style={{
                background: `linear-gradient(135deg, ${props.primaryColor}10, ${props.accentColor}10)`,
                borderRadius: 28,
                padding: "56px 72px",
                textAlign: "center",
              }}
            >
              <h2
                style={{
                  fontSize: 52,
                  fontWeight: 700,
                  color: props.primaryColor,
                  marginBottom: 28,
                }}
              >
                总结
              </h2>
              <p
                style={{
                  fontSize: 30,
                  color: props.textColor,
                  lineHeight: 1.6,
                }}
              >
                核心结论...
              </p>
            </div>
          </div>
        </FullBleedLayout>
      );

    case "outro":
      // Option A: Use pre-made MP4 animation (recommended)
      // import { OffthreadVideo, staticFile } from "remotion";
      // return <OffthreadVideo src={staticFile("media/{video-name}/bilibili-triple-white.mp4")} />;

      // Option B: Remotion-generated outro (matches reference style)
      return (
        <FullBleedLayout bg={props.backgroundColor}>
          <div
            style={{
              position: "absolute",
              inset: 0,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              alignItems: "center",
              ...animStyle,
            }}
          >
            <h2
              style={{
                fontSize: 80,
                fontWeight: 700,
                color: props.textColor,
                marginBottom: 48,
              }}
            >
              感谢观看
            </h2>
            <div style={{ display: "flex", gap: 40 }}>
              <div style={{ textAlign: "center" }}>
                <div style={{ fontSize: 64 }}>👍</div>
                <div style={{ fontSize: 26, color: "rgba(0,0,0,0.5)", marginTop: 10 }}>点赞</div>
              </div>
              <div style={{ textAlign: "center" }}>
                <div style={{ fontSize: 64 }}>⭐</div>
                <div style={{ fontSize: 26, color: "rgba(0,0,0,0.5)", marginTop: 10 }}>收藏</div>
              </div>
              <div style={{ textAlign: "center" }}>
                <div style={{ fontSize: 64 }}>🔔</div>
                <div style={{ fontSize: 26, color: "rgba(0,0,0,0.5)", marginTop: 10 }}>关注</div>
              </div>
            </div>
            <p
              style={{
                fontSize: 36,
                color: props.primaryColor,
                marginTop: 48,
              }}
            >
              下期再见！
            </p>
          </div>
        </FullBleedLayout>
      );

    default:
      // Generic content section (matches reference Card layout)
      return (
        <PaddedLayout bg={props.backgroundColor}>
          <div
            style={{
              position: "absolute",
              inset: 0,
              padding: "80px 100px",
              display: "flex",
              flexDirection: "column",
              ...animStyle,
            }}
          >
            <h2
              style={{
                fontSize: 80,
                fontWeight: 700,
                color: props.primaryColor,
              }}
            >
              {section.name}
            </h2>
            <p style={{ fontSize: 30, color: "rgba(0,0,0,0.5)", marginTop: 12 }}>
              Section description here
            </p>
            <div
              style={{
                flex: 1,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                marginTop: 24,
              }}
            >
              <p
                style={{
                  fontSize: props.bodySize,
                  color: props.textColor,
                  fontWeight: 500,
                }}
              >
                Section content goes here...
              </p>
            </div>
          </div>
        </PaddedLayout>
      );
  }
};

// 主视频组件 - 接收可视化编辑的 props
export const Video = (props: VideoProps) => {
  return (
    <AbsoluteFill style={{ backgroundColor: props.backgroundColor }}>
      {/* 4K 缩放包装 */}
      <Scale4K>
        {/* 按 timing.json 生成 Sequence */}
        {timing.sections.map((section) => (
          <Sequence
            key={section.name}
            from={section.start_frame}
            durationInFrames={section.duration_frames}
            name={section.name}
          >
            <SectionComponent section={section} props={props} />
          </Sequence>
        ))}
      </Scale4K>

      {/* 进度条 - 在 4K 缩放外，保持原始尺寸 */}
      <ChapterProgressBar props={props} chapters={timing.sections} />

      {/* BGM - 使用可配置音量 */}
      {props.bgmVolume > 0 && (
        <Audio src={staticFile("bgm.mp3")} volume={props.bgmVolume} />
      )}

      {/* TTS 语音 */}
      <Audio src={staticFile("podcast_audio.wav")} />
    </AbsoluteFill>
  );
};

export default Video;
