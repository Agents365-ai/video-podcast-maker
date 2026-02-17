/**
 * Remotion 视频组件模板
 *
 * 使用说明：
 * 1. 将此文件复制到项目的 src/ 目录
 * 2. 根据需要修改 SectionComponent 中的 section 渲染逻辑
 * 3. 确保 timing.json 和 audio.mp3 已生成
 */

import { useCurrentFrame, Audio, Sequence, staticFile, AbsoluteFill } from "remotion";
import timing from "../public/timing.json";

// 4K 缩放包装器 - 所有内容使用 1080p 设计，自动放大到 4K
const Scale4K = ({ children }: { children: React.ReactNode }) => (
  <AbsoluteFill style={{ transform: "scale(2)", transformOrigin: "top left" }}>
    {children}
  </AbsoluteFill>
);

// 全出血布局 - 无内边距，适合大标题和图表
const FullBleedLayout = ({ children, bg = "#FFFFFF" }: { children: React.ReactNode; bg?: string }) => (
  <AbsoluteFill style={{ backgroundColor: bg, padding: 0 }}>
    {children}
  </AbsoluteFill>
);

// 标准布局 - 带内边距，适合正文内容
const PaddedLayout = ({ children, bg = "#FFFFFF" }: { children: React.ReactNode; bg?: string }) => (
  <AbsoluteFill style={{ backgroundColor: bg, padding: 40 }}>
    {children}
  </AbsoluteFill>
);

// Section 渲染组件 - 根据 section 名称渲染不同内容
// 【自定义点】: 在这里添加你的 section 渲染逻辑
const SectionComponent = ({ section }: { section: typeof timing.sections[0] }) => {
  const frame = useCurrentFrame();

  switch (section.name) {
    case "hero":
      return (
        <FullBleedLayout>
          <div style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            height: "100%",
            textAlign: "center"
          }}>
            <h1 style={{ fontSize: 80, fontWeight: 700, color: "#1a1a1a" }}>
              视频标题
            </h1>
            <p style={{ fontSize: 32, color: "#666", marginTop: 20 }}>
              副标题或引导语
            </p>
          </div>
        </FullBleedLayout>
      );

    case "overview":
      return (
        <PaddedLayout>
          <h2 style={{ fontSize: 48, fontWeight: 600, marginBottom: 30 }}>今天的内容</h2>
          <ul style={{ fontSize: 28, lineHeight: 2 }}>
            <li>要点一</li>
            <li>要点二</li>
            <li>要点三</li>
          </ul>
        </PaddedLayout>
      );

    case "summary":
      return (
        <FullBleedLayout bg="#f5f5f5">
          <div style={{ padding: 40 }}>
            <h2 style={{ fontSize: 48, fontWeight: 600 }}>总结</h2>
            <p style={{ fontSize: 28, marginTop: 20 }}>核心结论...</p>
          </div>
        </FullBleedLayout>
      );

    case "outro":
      return (
        <FullBleedLayout>
          <div style={{
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            alignItems: "center",
            height: "100%"
          }}>
            <h2 style={{ fontSize: 60, fontWeight: 700 }}>感谢观看</h2>
            <p style={{ fontSize: 36, color: "#FF6B6B", marginTop: 30 }}>
              一键三连 👍
            </p>
          </div>
        </FullBleedLayout>
      );

    default:
      // 通用 content section 渲染
      return (
        <PaddedLayout>
          <h2 style={{ fontSize: 48, fontWeight: 600, marginBottom: 20 }}>
            {section.name}
          </h2>
          <p style={{ fontSize: 24, color: "#666" }}>
            Section content goes here...
          </p>
        </PaddedLayout>
      );
  }
};

// 主视频组件
export const Video = () => {
  return (
    <AbsoluteFill style={{ backgroundColor: "#FFFFFF" }}>
      {/* 4K 缩放包装 */}
      <Scale4K>
        {/* 按 timing.json 生成 Sequence */}
        {timing.sections.map((section, index) => (
          <Sequence
            key={section.name}
            from={section.startFrame}
            durationInFrames={section.durationInFrames}
            name={section.name}
          >
            <SectionComponent section={section} />
          </Sequence>
        ))}
      </Scale4K>

      {/* 背景音乐 - 可选 */}
      {/* <Audio src={staticFile("bgm.mp3")} volume={0.1} /> */}

      {/* TTS 语音 */}
      <Audio src={staticFile("audio.mp3")} />
    </AbsoluteFill>
  );
};

export default Video;
