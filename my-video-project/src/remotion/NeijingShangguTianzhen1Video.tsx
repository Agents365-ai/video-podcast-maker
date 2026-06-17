/**
 * 《黄帝内经》导读第1讲：我们能活多久？——《上古天真论》上
 * 宋韵美学 · 9:16 竖屏 ·  granular slide pacing (~10s per slide)
 */

import React from "react";
import { Audio, staticFile, AbsoluteFill } from "remotion";
import { TransitionSeries, linearTiming } from "@remotion/transitions";
import type { VideoProps } from "./Root";

import {
  Scale4K,
  getPresentation,
  ChapterProgressBar,
  Subtitles,
  useTiming,
  renderSlide,
} from "./components";
import type { TimingSection } from "./components";

// Slide renderer wrapper
const SlideComponent = ({
  section,
  props,
}: {
  section: TimingSection;
  props: VideoProps;
}) => {
  const slideProps = {
    primaryColor: props.primaryColor,
    backgroundColor: props.backgroundColor,
    textColor: props.textColor,
    accentColor: props.accentColor,
    orientation: props.orientation,
    enableAnimations: props.enableAnimations,
  };
  return renderSlide(section, slideProps);
};

export const NeijingShangguTianzhen1Video = (props: VideoProps) => {
  const timing = useTiming();
  const sections = timing.sections;
  const transitionFrames = props.transitionDuration;

  // TransitionSeries overlaps adjacent sequences by the transition duration,
  // so the overall timeline is: sum(section durations) - totalTransitionFrames.
  // Scale each section up so the final timeline matches the audio length.
  const originalTotal = sections.reduce((sum, s) => sum + s.duration_frames, 0);
  const transitionCount = Math.max(0, sections.length - 1);
  const totalTransitionFrames = transitionCount * transitionFrames;
  const targetSequenceTotal = originalTotal + totalTransitionFrames;
  const scaleFactor =
    originalTotal > 0 ? targetSequenceTotal / originalTotal : 1;

  const compensatedSections = sections.map((s) => ({
    ...s,
    duration_frames: Math.max(30, Math.round(s.duration_frames * scaleFactor)),
  }));

  // Fix rounding drift so the timeline is exact.
  const scaledTotal = compensatedSections.reduce(
    (sum, s) => sum + s.duration_frames,
    0
  );
  const drift = targetSequenceTotal - scaledTotal;
  if (compensatedSections.length > 0) {
    const last = compensatedSections[compensatedSections.length - 1];
    last.duration_frames = Math.max(
      30,
      last.duration_frames + drift
    );
  }

  return (
    <AbsoluteFill style={{ backgroundColor: props.backgroundColor }}>
      <Scale4K orientation={props.orientation}>
        <TransitionSeries>
          {compensatedSections.map((section, i) => (
            <React.Fragment key={section.name}>
              <TransitionSeries.Sequence durationInFrames={section.duration_frames}>
                <SlideComponent section={section} props={props} />
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

      <ChapterProgressBar props={props} chapters={timing.sections} />
      <Subtitles src={staticFile("podcast_audio.srt")} />

      {props.bgmVolume > 0 && (
        <Audio src={staticFile("bgm.mp3")} volume={props.bgmVolume} />
      )}

      <Audio src={staticFile("podcast_audio.wav")} />
    </AbsoluteFill>
  );
};

export default NeijingShangguTianzhen1Video;
