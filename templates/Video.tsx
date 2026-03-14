/**
 * Remotion Video Component Template - with Studio visual editing support
 *
 * Usage:
 * 1. Copy this file and components/ directory to your project src/
 * 2. Modify SectionComponent cases to match your sections
 * 3. Ensure timing.json and podcast_audio.wav are generated
 * 4. Use Remotion Studio right panel to adjust styles in real-time
 *
 * Available components (import from "./components"):
 *   ComparisonCard, Timeline, CodeBlock, QuoteBlock, FeatureGrid, DataBar
 */

import React from "react";
import { Audio, staticFile, AbsoluteFill } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import timing from "../public/timing.json";
import type { VideoProps } from "./Root";

import {
  Scale4K,
  FullBleedLayout,
  PaddedLayout,
  useEntrance,
  getPresentation,
  ChapterProgressBar,
} from "./components";

// Section renderer - customize your section visuals here
const SectionComponent = ({
  section,
  props,
}: {
  section: typeof timing.sections[0];
  props: VideoProps;
}) => {
  const { opacity, translateY, scale } = useEntrance(props.enableAnimations);
  const animStyle = { opacity, transform: `translateY(${translateY}px) scale(${scale})` };

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

// Main video component - receives editable props from Studio
export const Video = (props: VideoProps) => {
  const sections = timing.sections;
  const transitionFrames = props.transitionDuration;
  const transitionCount = Math.max(0, sections.length - 1);

  // Compensate for transition overlap: add lost frames to first section
  // so TransitionSeries total matches timing.total_frames for audio sync
  const compensatedSections = sections.map((s, i) => ({
    ...s,
    duration_frames: i === 0
      ? s.duration_frames + transitionCount * transitionFrames
      : s.duration_frames,
  }));

  return (
    <AbsoluteFill style={{ backgroundColor: props.backgroundColor }}>
      <Scale4K>
        <TransitionSeries>
          {compensatedSections.map((section, i) => (
            <React.Fragment key={section.name}>
              <TransitionSeries.Sequence durationInFrames={section.duration_frames}>
                <SectionComponent section={section} props={props} />
              </TransitionSeries.Sequence>
              {i < sections.length - 1 && transitionFrames > 0 && props.transitionType !== "none" && (
                <TransitionSeries.Transition
                  presentation={getPresentation(props.transitionType)}
                  timing={linearTiming({ durationInFrames: transitionFrames })}
                />
              )}
            </React.Fragment>
          ))}
        </TransitionSeries>
      </Scale4K>

      {/* Progress bar - outside scale(2) wrapper, renders at native 4K */}
      <ChapterProgressBar props={props} chapters={timing.sections} />

      {/* BGM with configurable volume */}
      {props.bgmVolume > 0 && (
        <Audio src={staticFile("bgm.mp3")} volume={props.bgmVolume} />
      )}

      {/* TTS audio */}
      <Audio src={staticFile("podcast_audio.wav")} />
    </AbsoluteFill>
  );
};

export default Video;
