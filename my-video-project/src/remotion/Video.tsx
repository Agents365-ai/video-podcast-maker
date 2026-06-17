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
  ComparisonCard,
  FlowChart,
  CenteredShowcase,
  FeatureGrid,
} from "./components";
import type { TimingSection } from "./components";

// 宋韵美学字体
const SONG_FONT = '"Songti SC", "STSong", "Noto Serif SC", serif';

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
    // Reference font sizes (1080p design space, horizontal):
    // Hero title: 72-120px/800wt, Section title: 72-80px/700-800wt
    // Subtitle: 30-40px, Card title: 34-38px, Body: 26-34px, Tags: 20-26px
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

    // --- Custom sections for "why-people-get-sick" (宋韵美学风格) ---

    case "hook":
      return (
        <FullBleedLayout bg={props.backgroundColor}>
          {/* 淡墨山影背景 */}
          <div style={{
            position: "absolute", inset: 0,
            background: `radial-gradient(ellipse at 30% 20%, ${props.primaryColor}08 0%, transparent 55%), radial-gradient(ellipse at 70% 80%, ${props.accentColor}06 0%, transparent 50%)`,
          }} />
          {/* 顶部装饰线 */}
          <div style={{ position: "absolute", top: 80, left: "10%", right: "10%", height: 1, background: `${props.primaryColor}20` }} />
          <div style={{ position: "absolute", bottom: 80, left: "10%", right: "10%", height: 1, background: `${props.primaryColor}20` }} />

          <div style={{ position: "absolute", inset: 0, padding: sectionPadding, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", ...animStyle }}>
            {/* 印章 */}
            <div style={{
              width: v ? 72 : 64, height: v ? 72 : 64,
              background: props.accentColor,
              display: "flex", alignItems: "center", justifyContent: "center",
              marginBottom: v ? 36 : 28,
              boxShadow: `0 4px 12px ${props.accentColor}30`,
            }}>
              <span style={{ color: "#fff", fontFamily: SONG_FONT, fontSize: v ? 32 : 28, fontWeight: 700 }}>问</span>
            </div>

            <h2 style={{
              fontSize: v ? 64 : 80,
              fontWeight: 700,
              color: props.primaryColor,
              textAlign: "center",
              lineHeight: 1.4,
              marginBottom: v ? 48 : 40,
              fontFamily: SONG_FONT,
              letterSpacing: 4,
            }}>
              同样的生活习惯
              <br />
              为何有人病，有人不病？
            </h2>

            <div style={{ display: "flex", flexDirection: v ? "column" : "row", gap: v ? 24 : 40, width: "100%", maxWidth: v ? undefined : 900, alignItems: "center" }}>
              {/* 左侧：无恙 */}
              <div style={{
                flex: 1, width: v ? "100%" : undefined,
                background: "rgba(255,255,255,0.6)",
                border: `1px solid ${props.primaryColor}20`,
                borderRadius: 4,
                padding: v ? "32px 36px" : "36px 40px",
                textAlign: "center",
              }}>
                <div style={{ fontSize: v ? 36 : 40, fontFamily: SONG_FONT, color: "#6b8e6b", marginBottom: 16 }}>无恙之人</div>
                {["熬夜后只是困一点", "吃冷饮后安然无恙", "照样精神饱满"].map((t, i) => (
                  <div key={i} style={{ fontSize: v ? 28 : 26, color: props.textColor, opacity: 0.8, padding: "10px 0", borderTop: i > 0 ? `1px dashed ${props.primaryColor}15` : "none" }}>{t}</div>
                ))}
              </div>

              <div style={{ fontSize: v ? 36 : 40, fontFamily: SONG_FONT, color: props.accentColor, opacity: 0.8 }}>VS</div>

              {/* 右侧：有恙 */}
              <div style={{
                flex: 1, width: v ? "100%" : undefined,
                background: "rgba(255,255,255,0.6)",
                border: `1px solid ${props.accentColor}35`,
                borderRadius: 4,
                padding: v ? "32px 36px" : "36px 40px",
                textAlign: "center",
              }}>
                <div style={{ fontSize: v ? 36 : 40, fontFamily: SONG_FONT, color: props.accentColor, marginBottom: 16 }}>易病之人</div>
                {["熬夜后感冒了", "吃冷饮后肚子疼", "身体频频亮红灯"].map((t, i) => (
                  <div key={i} style={{ fontSize: v ? 28 : 26, color: props.textColor, opacity: 0.8, padding: "10px 0", borderTop: i > 0 ? `1px dashed ${props.accentColor}20` : "none" }}>{t}</div>
                ))}
              </div>
            </div>
          </div>
        </FullBleedLayout>
      );

    case "modern":
      return (
        <FullBleedLayout bg={props.backgroundColor}>
          <div style={{ position: "absolute", inset: 0, background: `radial-gradient(ellipse at 80% 10%, ${props.primaryColor}06 0%, transparent 50%)` }} />
          <div style={{ position: "absolute", top: 80, left: "10%", right: "10%", height: 1, background: `${props.primaryColor}20` }} />
          <div style={{ position: "absolute", bottom: 80, left: "10%", right: "10%", height: 1, background: `${props.primaryColor}20` }} />

          <div style={{ position: "absolute", inset: 0, padding: sectionPadding, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", ...animStyle }}>
            <div style={{ fontSize: v ? 28 : 26, color: props.accentColor, fontFamily: SONG_FONT, letterSpacing: 6, marginBottom: v ? 16 : 12 }}>现代医学</div>
            <h2 style={{
              fontSize: v ? 52 : 64,
              fontWeight: 700,
              color: props.primaryColor,
              textAlign: "center",
              lineHeight: 1.35,
              marginBottom: v ? 44 : 40,
              fontFamily: SONG_FONT,
              letterSpacing: 3,
            }}>
              慢性病，是身体长期失衡的结果
            </h2>

            <div style={{ display: "flex", flexDirection: "column", gap: v ? 20 : 18, width: "100%", maxWidth: v ? undefined : 820 }}>
              {[
                { num: "壹", title: "长期失衡", desc: "熬夜、压力、饮食紊乱" },
                { num: "贰", title: "代谢紊乱", desc: "糖脂代谢异常" },
                { num: "叁", title: "慢性炎症", desc: "身体长期处于低度发炎" },
                { num: "肆", title: "修复跟不上", desc: "自愈能力逐渐下降" },
                { num: "伍", title: "病慢慢出来", desc: "慢性病逐渐形成" },
              ].map((item, i) => {
                const a = useEntrance(props.enableAnimations, i * 5, "snappy");
                return (
                  <div key={i} style={{
                    display: "flex", alignItems: "center", gap: v ? 24 : 28,
                    background: "rgba(255,255,255,0.55)",
                    border: `1px solid ${props.primaryColor}18`,
                    borderRadius: 4,
                    padding: v ? "22px 28px" : "20px 32px",
                    opacity: a.opacity, transform: `translateY(${a.translateY}px) scale(${a.scale})`,
                  }}>
                    <div style={{
                      width: v ? 44 : 40, height: v ? 44 : 40,
                      border: `1px solid ${props.accentColor}`,
                      color: props.accentColor,
                      display: "flex", alignItems: "center", justifyContent: "center",
                      fontFamily: SONG_FONT, fontSize: v ? 22 : 20, flexShrink: 0,
                    }}>{item.num}</div>
                    <div style={{ flex: 1 }}>
                      <span style={{ fontSize: v ? 34 : 32, fontFamily: SONG_FONT, color: props.primaryColor, marginRight: 16 }}>{item.title}</span>
                      <span style={{ fontSize: v ? 26 : 24, color: props.textColor, opacity: 0.65 }}>{item.desc}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </FullBleedLayout>
      );

    case "huangdi":
      return (
        <FullBleedLayout bg={props.backgroundColor}>
          <div style={{ position: "absolute", inset: 0, background: `radial-gradient(ellipse at 50% 50%, ${props.accentColor}08 0%, transparent 60%)` }} />
          <div style={{ position: "absolute", top: 80, left: "10%", right: "10%", height: 1, background: `${props.primaryColor}20` }} />
          <div style={{ position: "absolute", bottom: 80, left: "10%", right: "10%", height: 1, background: `${props.primaryColor}20` }} />

          <div style={{ position: "absolute", inset: 0, padding: sectionPadding, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", textAlign: "center", ...animStyle }}>
            <div style={{ fontSize: 80, marginBottom: v ? 32 : 24 }}>☯️</div>
            <h2 style={{
              fontSize: v ? 68 : 84,
              fontWeight: 700,
              color: props.primaryColor,
              lineHeight: 1.4,
              marginBottom: v ? 36 : 28,
              fontFamily: SONG_FONT,
              letterSpacing: 6,
            }}>
              正气存内，邪不可干
            </h2>
            <p style={{
              fontSize: v ? 32 : 28,
              color: props.textColor,
              lineHeight: 1.9,
              opacity: 0.75,
              maxWidth: v ? "90%" : 800,
              fontFamily: SONG_FONT,
              letterSpacing: 2,
            }}>
              《黄帝内经》用另一套语言解释：阴阳失调、正气不足。
              <br />
              身体底子好的人，外面的邪气就不容易伤到他。
            </p>
            {/* 印章落款 */}
            <div style={{
              marginTop: v ? 48 : 40,
              padding: "10px 18px",
              border: `2px solid ${props.accentColor}`,
              color: props.accentColor,
              fontFamily: SONG_FONT,
              fontSize: v ? 26 : 22,
              letterSpacing: 4,
            }}>
              黄帝内经
            </div>
          </div>
        </FullBleedLayout>
      );

    case "conclusion":
      return (
        <FullBleedLayout bg={props.backgroundColor}>
          <div style={{ position: "absolute", inset: 0, background: `radial-gradient(ellipse at 20% 90%, ${props.primaryColor}06 0%, transparent 45%), radial-gradient(ellipse at 80% 10%, ${props.accentColor}06 0%, transparent 45%)` }} />
          <div style={{ position: "absolute", top: 80, left: "10%", right: "10%", height: 1, background: `${props.primaryColor}20` }} />
          <div style={{ position: "absolute", bottom: 80, left: "10%", right: "10%", height: 1, background: `${props.primaryColor}20` }} />

          <div style={{ position: "absolute", inset: 0, padding: sectionPadding, display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center", ...animStyle }}>
            <div style={{ fontSize: v ? 28 : 26, color: props.accentColor, fontFamily: SONG_FONT, letterSpacing: 6, marginBottom: v ? 16 : 12 }}>结语</div>
            <h2 style={{
              fontSize: v ? 52 : 64,
              fontWeight: 700,
              color: props.primaryColor,
              textAlign: "center",
              lineHeight: 1.4,
              marginBottom: v ? 44 : 40,
              fontFamily: SONG_FONT,
              letterSpacing: 4,
            }}>
              健康，是把身体放回平衡里
            </h2>

            <div style={{ display: "grid", gridTemplateColumns: v ? "1fr" : "1fr 1fr", gap: v ? 22 : 24, width: "100%", maxWidth: v ? undefined : 900 }}>
              {[
                { icon: "🍚", title: "好好吃饭", desc: "规律饮食，减少代谢负担" },
                { icon: "🌙", title: "好好睡觉", desc: "让身体每晚自我修复" },
                { icon: "🚶", title: "适当运动", desc: "活络气血，提升正气" },
                { icon: "🍃", title: "少透支自己", desc: "不过劳、不熬夜、不焦虑" },
              ].map((item, i) => {
                const a = useEntrance(props.enableAnimations, i * 5, "snappy");
                return (
                  <div key={i} style={{
                    display: "flex", alignItems: "center", gap: v ? 24 : 28,
                    background: "rgba(255,255,255,0.55)",
                    border: `1px solid ${props.primaryColor}18`,
                    borderRadius: 4,
                    padding: v ? "26px 32px" : "28px 36px",
                    opacity: a.opacity, transform: `translateY(${a.translateY}px) scale(${a.scale})`,
                  }}>
                    <div style={{ fontSize: v ? 48 : 44, flexShrink: 0 }}>{item.icon}</div>
                    <div>
                      <div style={{ fontSize: v ? 36 : 34, fontFamily: SONG_FONT, color: props.primaryColor, marginBottom: 6 }}>{item.title}</div>
                      <div style={{ fontSize: v ? 26 : 24, color: props.textColor, opacity: 0.65 }}>{item.desc}</div>
                    </div>
                  </div>
                );
              })}
            </div>
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
                  presentation={getPresentation(props.transitionType) as any}
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
