/**
 * Remotion Video Component Template - with Studio visual editing support
 *
 * Usage:
 * 1. Copy this file and components/ directory to your project src/
 * 2. Modify SectionComponent cases to match your sections
 * 3. Ensure timing.json and podcast_audio.wav are in the --public-dir directory
 * 4. Use Remotion Studio right panel to adjust styles in real-time
 *
 * Available components (import from "./components"):
 *   ComparisonCard, Timeline, CodeBlock, QuoteBlock, FeatureGrid, DataBar, StatCounter, FlowChart, IconCard
 *
 * LOCALIZATION CONTRACT (read before customizing per video):
 *   Every visible string below is a zh-CN starter — title, subtitle, section
 *   labels, outro CTA ("点赞" / "收藏" / "关注" / "下期再见！"), placeholder
 *   bullet text, etc. When `user_prefs.global.language === "en-US"` (or any
 *   non-Chinese language) the agent MUST replace ALL literal strings with the
 *   target-language equivalent before rendering. Do not ship a video where
 *   Chinese leaks into a non-Chinese composition.
 */

import React from "react";
import { Audio, staticFile, AbsoluteFill } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import type { VideoProps } from "./Root";

import {
  Scale4K,
  FullBleedLayout,
  PaddedLayout,
  useEntrance,
  getPresentation,
  ChapterProgressBar,
  Subtitles,
  IconCard,
  Icon,
  useTiming,
} from "./components";
import type { TimingSection } from "./components";

// Section renderer - customize your section visuals here
// Layouts auto-adapt based on orientation (horizontal/vertical)
const SectionComponent = ({
  section,
  props,
}: {
  section: TimingSection;
  props: VideoProps;
}) => {
  const { opacity, translateY, scale } = useEntrance(props.enableAnimations);
  const animStyle = { opacity, transform: `translateY(${translateY}px) scale(${scale})` };
  const v = props.orientation === "vertical";
  // Vertical uses more padding top/bottom, less left/right
  // Bottom padding reserves space for burned-in subtitles (100px safe zone)
  const sectionPadding = v ? "120px 60px 160px" : "60px 100px 120px";

  switch (section.name) {
    // Reference font sizes (1080p design space, horizontal) — see
    // references/design-guide.md minimums (hero ≥84, section ≥72,
    // card title ≥40, body ≥32, any text ≥24):
    // Hero title: 84-120px/800wt, Section title: 72-80px/700-800wt
    // Subtitle: 30-40px, Card title: 40-48px, Body: 32-40px, Tags: 24-28px
    // Vertical: scale up body/subtitle by ~20%, titles stay similar

    case "hero":
      return (
        <FullBleedLayout bg={props.backgroundColor}>
          {/* Decorative radial gradient */}
          <div style={{
            position: "absolute", inset: 0,
            background: `radial-gradient(ellipse at 50% 40%, ${props.primaryColor}12 0%, transparent 70%)`,
          }} />
          {/* Decorative circle */}
          <div style={{
            position: "absolute", top: -120, right: -80,
            width: 400, height: 400, borderRadius: "50%",
            background: `${props.primaryColor}08`,
          }} />
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
                textShadow: `0 2px 16px ${props.primaryColor}15`,
              }}
            >
              视频标题
            </h1>
            <p
              style={{
                fontSize: props.subtitleSize,
                color: props.textColor,
                marginTop: v ? 32 : 20,
                opacity: 0.6,
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
        <PaddedLayout bg="#fafafa" orientation={props.orientation}>
          <div
            style={{
              position: "absolute",
              inset: 0,
              padding: sectionPadding,
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              ...animStyle,
            }}
          >
            <h2
              style={{
                fontSize: v ? 72 : 80,
                fontWeight: 700,
                marginBottom: 12,
                color: props.primaryColor,
                textAlign: "center",
              }}
            >
              今天的内容
            </h2>
            <p style={{ fontSize: v ? 34 : 30, color: props.textColor, opacity: 0.5, marginBottom: v ? 24 : 20, textAlign: "center" }}>
              Section description here
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: v ? 24 : 20, width: "100%", maxWidth: v ? undefined : 900 }}>
              {[
                { icon: "lightbulb", title: "要点一", description: "说明文字" },
                { icon: "target", title: "要点二", description: "说明文字" },
                { icon: "check-circle", title: "要点三", description: "说明文字" },
              ].map((item, i) => (
                <IconCard key={i} props={props} icon={item.icon} title={item.title} description={item.description} delay={i * 6} />
              ))}
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
                border: `1px solid ${props.primaryColor}20`,
                boxShadow: `0 4px 24px ${props.primaryColor}12, 0 8px 48px rgba(0,0,0,0.04)`,
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
                  fontSize: v ? 36 : 32,
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
                { icon: "thumbs-up", text: "点赞" },
                { icon: "star", text: "收藏" },
                { icon: "bell", text: "关注" },
              ].map((item, i) => (
                <div key={i} style={{ textAlign: "center" }}>
                  <Icon name={item.icon} size={v ? 80 : 64} color={props.accentColor} animate="bounce" delay={i * 10} />
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
              justifyContent: "center",
              ...animStyle,
            }}
          >
            <h2
              style={{
                fontSize: v ? 72 : 80,
                fontWeight: 700,
                color: props.primaryColor,
                textAlign: "center",
              }}
            >
              {section.name}
            </h2>
            <p style={{ fontSize: v ? 34 : 30, color: props.textColor, opacity: 0.5, marginTop: 12, marginBottom: 20, textAlign: "center" }}>
              Section description here
            </p>
            <div style={{
              background: `linear-gradient(135deg, ${props.primaryColor}06, ${props.accentColor}06)`,
              borderRadius: 24, padding: v ? "40px 44px" : "40px 56px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.03), 0 8px 32px rgba(0,0,0,0.05)",
              border: `1px solid ${props.primaryColor}10`,
              width: "100%",
            }}>
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
  const timing = useTiming();
  const sections = timing.sections;
  const transitionFrames = props.transitionDuration;
  const transitionCount = Math.max(0, sections.length - 1);
  const effectiveTransitionFrames =
    props.transitionType !== "none" && transitionFrames > 0 ? transitionFrames : 0;

  // Audio-master-clock: TransitionSeries renders sum(sections) - (N-1)*transitionFrames.
  // Scale every section proportionally so the rendered total equals timing.total_frames,
  // instead of stuffing all overlap frames into the first section (which desyncs it).
  const originalTotal = sections.reduce((sum, s) => sum + s.duration_frames, 0);
  const targetTotal = timing.total_frames + transitionCount * effectiveTransitionFrames;
  const scaleFactor = originalTotal > 0 ? targetTotal / originalTotal : 1;

  const compensatedSections = sections.map((s) => ({
    ...s,
    duration_frames: Math.max(15, Math.round(s.duration_frames * scaleFactor)),
  }));

  // Absorb rounding error into the last section so the total matches exactly.
  const scaledTotal = compensatedSections.reduce((sum, s) => sum + s.duration_frames, 0);
  const diff = targetTotal - scaledTotal;
  if (compensatedSections.length > 0) {
    const last = compensatedSections[compensatedSections.length - 1];
    last.duration_frames = Math.max(15, last.duration_frames + diff);
  }

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

      {/* Subtitles - outside scale(2), renders at native 4K, no FFmpeg needed */}
      <Subtitles src={staticFile("podcast_audio.srt")} />

      {/* BGM with configurable volume.
          Default `bgmVolume = 0` (off) — Step 11 mixes BGM via FFmpeg.
          Set this > 0 in Studio only if you intend to skip Step 11. */}
      {props.bgmVolume > 0 && (
        <Audio src={staticFile("bgm.mp3")} volume={props.bgmVolume} />
      )}

      {/* TTS audio */}
      <Audio src={staticFile("podcast_audio.wav")} />
    </AbsoluteFill>
  );
};

export default Video;
