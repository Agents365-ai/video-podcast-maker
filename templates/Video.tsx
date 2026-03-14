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
// Layouts auto-adapt based on orientation (horizontal/vertical)
const SectionComponent = ({
  section,
  props,
}: {
  section: typeof timing.sections[0];
  props: VideoProps;
}) => {
  const { opacity, translateY, scale } = useEntrance(props.enableAnimations);
  const animStyle = { opacity, transform: `translateY(${translateY}px) scale(${scale})` };
  const v = props.orientation === "vertical";
  // Vertical uses more padding top/bottom, less left/right
  const sectionPadding = v ? "120px 60px" : "80px 100px";

  switch (section.name) {
    // Reference font sizes (1080p design space, horizontal):
    // Hero title: 72-120px/800wt, Section title: 72-80px/700-800wt
    // Subtitle: 30-40px, Card title: 34-38px, Body: 26-34px, Tags: 20-26px
    // Vertical: scale up body/subtitle by ~20%, titles stay similar

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
              padding: v ? "0 60px" : 0,
              ...animStyle,
            }}
          >
            <h1
              style={{
                fontSize: props.titleSize,
                fontWeight: 800,
                color: props.primaryColor,
                lineHeight: v ? 1.3 : 1.1,
              }}
            >
              视频标题
            </h1>
            <p
              style={{
                fontSize: props.subtitleSize,
                color: props.textColor,
                marginTop: v ? 32 : 20,
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
        <PaddedLayout bg={props.backgroundColor} orientation={props.orientation}>
          <div
            style={{
              position: "absolute",
              inset: 0,
              padding: sectionPadding,
              display: "flex",
              flexDirection: "column",
              ...animStyle,
            }}
          >
            <h2
              style={{
                fontSize: v ? 72 : 80,
                fontWeight: 700,
                marginBottom: 12,
                color: props.primaryColor,
              }}
            >
              今天的内容
            </h2>
            <p style={{ fontSize: v ? 34 : 30, color: "rgba(0,0,0,0.5)", marginBottom: v ? 48 : 40 }}>
              Section description here
            </p>
            <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: v ? 36 : 28, width: "100%", maxWidth: v ? undefined : 800 }}>
                {[
                  { icon: "💡", text: "要点一" },
                  { icon: "🎯", text: "要点二" },
                  { icon: "✅", text: "要点三" },
                ].map((item, i) => (
                  <div key={i} style={{
                    background: "rgba(0,0,0,0.02)", border: "1px solid rgba(0,0,0,0.08)",
                    borderRadius: 20, padding: v ? "40px 48px" : "32px 40px",
                    display: "flex", alignItems: "center", gap: 24,
                  }}>
                    <div style={{ fontSize: v ? 60 : 52 }}>{item.icon}</div>
                    <div style={{ fontSize: v ? 40 : 34, fontWeight: 600, color: props.textColor }}>{item.text}</div>
                  </div>
                ))}
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
              padding: sectionPadding,
              ...animStyle,
            }}
          >
            <div
              style={{
                background: `linear-gradient(135deg, ${props.primaryColor}10, ${props.accentColor}10)`,
                borderRadius: 28,
                padding: v ? "72px 60px" : "56px 72px",
                textAlign: "center",
                width: v ? "100%" : "auto",
              }}
            >
              <h2
                style={{
                  fontSize: v ? 60 : 52,
                  fontWeight: 700,
                  color: props.primaryColor,
                  marginBottom: 28,
                }}
              >
                总结
              </h2>
              <p
                style={{
                  fontSize: v ? 36 : 30,
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
                fontSize: v ? 72 : 80,
                fontWeight: 700,
                color: props.textColor,
                marginBottom: v ? 64 : 48,
              }}
            >
              感谢观看
            </h2>
            <div style={{ display: "flex", gap: v ? 56 : 40, flexDirection: v ? "column" : "row" }}>
              {[
                { icon: "👍", text: "点赞" },
                { icon: "⭐", text: "收藏" },
                { icon: "🔔", text: "关注" },
              ].map((item, i) => (
                <div key={i} style={{ textAlign: "center" }}>
                  <div style={{ fontSize: v ? 80 : 64 }}>{item.icon}</div>
                  <div style={{ fontSize: v ? 32 : 26, color: "rgba(0,0,0,0.5)", marginTop: 10 }}>{item.text}</div>
                </div>
              ))}
            </div>
            <p
              style={{
                fontSize: v ? 44 : 36,
                color: props.primaryColor,
                marginTop: v ? 64 : 48,
              }}
            >
              下期再见！
            </p>
          </div>
        </FullBleedLayout>
      );

    default:
      return (
        <PaddedLayout bg={props.backgroundColor} orientation={props.orientation}>
          <div
            style={{
              position: "absolute",
              inset: 0,
              padding: sectionPadding,
              display: "flex",
              flexDirection: "column",
              ...animStyle,
            }}
          >
            <h2
              style={{
                fontSize: v ? 72 : 80,
                fontWeight: 700,
                color: props.primaryColor,
              }}
            >
              {section.name}
            </h2>
            <p style={{ fontSize: v ? 34 : 30, color: "rgba(0,0,0,0.5)", marginTop: 12 }}>
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
                  lineHeight: v ? 1.8 : 1.5,
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
      <Scale4K orientation={props.orientation}>
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
