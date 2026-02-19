/**
 * Remotion 视频组件模板 - 支持 Studio 可视化编辑
 *
 * 使用说明：
 * 1. 将此文件复制到项目的 src/ 目录
 * 2. 根据需要修改 SectionComponent 中的 section 渲染逻辑
 * 3. 确保 timing.json 和 audio.mp3 已生成
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

// 章节进度条组件
const ChapterProgressBar = ({
  props,
  chapters,
}: {
  props: VideoProps;
  chapters: typeof timing.sections;
}) => {
  const frame = useCurrentFrame();
  const totalFrames = timing.totalFrames;
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
        borderTop: "1px solid #e5e7eb",
        display: "flex",
        alignItems: "center",
        padding: "0 50px",
        gap: 16,
        fontFamily: "PingFang SC, Microsoft YaHei, sans-serif",
      }}
    >
      {chapters.map((ch) => {
        const chStart = ch.startFrame / totalFrames;
        const chEnd = (ch.startFrame + ch.durationInFrames) / totalFrames;
        const isActive = progress >= chStart && progress < chEnd;
        const isPast = progress >= chEnd;
        const chProgress = isActive ? (progress - chStart) / (chEnd - chStart) : isPast ? 1 : 0;
        const buttonHeight = props.progressBarHeight - 50;
        const borderRadius = buttonHeight / 2;

        return (
          <div
            key={ch.name}
            style={{
              flex: ch.durationInFrames,
              height: buttonHeight,
              borderRadius,
              position: "relative",
              overflow: "hidden",
              background: isActive ? props.progressActiveColor : isPast ? "#f3f4f6" : "#f9fafb",
              border: isActive ? "none" : "1px solid #e5e7eb",
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
                  borderRadius,
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
      {/* 底部总进度条 */}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          height: 4,
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
    case "hero":
      return (
        <FullBleedLayout bg={props.backgroundColor}>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              alignItems: "center",
              height: "100%",
              textAlign: "center",
              ...animStyle,
            }}
          >
            <h1
              style={{
                fontSize: props.titleSize,
                fontWeight: 700,
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
                opacity: 0.8,
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
          <div style={animStyle}>
            <h2
              style={{
                fontSize: props.subtitleSize,
                fontWeight: 600,
                marginBottom: 30,
                color: props.primaryColor,
              }}
            >
              今天的内容
            </h2>
            <ul
              style={{
                fontSize: props.bodySize,
                lineHeight: 2,
                color: props.textColor,
              }}
            >
              <li>要点一</li>
              <li>要点二</li>
              <li>要点三</li>
            </ul>
          </div>
        </PaddedLayout>
      );

    case "summary":
      return (
        <FullBleedLayout bg="#f5f5f5">
          <div style={{ padding: 40, ...animStyle }}>
            <h2
              style={{
                fontSize: props.subtitleSize,
                fontWeight: 600,
                color: props.primaryColor,
              }}
            >
              总结
            </h2>
            <p
              style={{
                fontSize: props.bodySize,
                marginTop: 20,
                color: props.textColor,
              }}
            >
              核心结论...
            </p>
          </div>
        </FullBleedLayout>
      );

    case "outro":
      return (
        <FullBleedLayout bg={props.backgroundColor}>
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              alignItems: "center",
              height: "100%",
              ...animStyle,
            }}
          >
            <h2
              style={{
                fontSize: props.titleSize * 0.75,
                fontWeight: 700,
                color: props.textColor,
              }}
            >
              感谢观看
            </h2>
            <p
              style={{
                fontSize: props.subtitleSize * 0.75,
                color: props.accentColor,
                marginTop: 30,
              }}
            >
              一键三连 👍
            </p>
          </div>
        </FullBleedLayout>
      );

    default:
      // 通用 content section 渲染
      return (
        <PaddedLayout bg={props.backgroundColor}>
          <div style={animStyle}>
            <h2
              style={{
                fontSize: props.subtitleSize,
                fontWeight: 600,
                marginBottom: 20,
                color: props.primaryColor,
              }}
            >
              {section.name}
            </h2>
            <p
              style={{
                fontSize: props.bodySize,
                color: props.textColor,
                opacity: 0.8,
              }}
            >
              Section content goes here...
            </p>
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
            from={section.startFrame}
            durationInFrames={section.durationInFrames}
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
      <Audio src={staticFile("audio.mp3")} />
    </AbsoluteFill>
  );
};

export default Video;
