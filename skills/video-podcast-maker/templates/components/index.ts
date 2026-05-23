// Layouts
export { Scale4K, FullBleedLayout, PaddedLayout } from "./layouts";

// Animations
export {
  useEntrance, useExit, useCounter, useBarFill, getPresentation,
  useFloat, usePulse, useGradientShift, useOpacityWave,
  useTextReveal, useCharReveal, staggerDelay,
  useDrawOn, useStaggeredDrawOn,
} from "./animations";

// Animated backgrounds
export {
  MovingGradient, FloatingShapes, GridPattern, GlowOrb, AccentLine,
} from "./AnimatedBackground";

// Section layout presets
export {
  SplitLayout, StatHighlight, ZigzagCards,
  CenteredShowcase, MetricsRow, StepProgress,
} from "./SectionLayouts";

// Content components
export { ComparisonCard } from "./ComparisonCard";
export { Timeline } from "./Timeline";
export { CodeBlock } from "./CodeBlock";
export { QuoteBlock } from "./QuoteBlock";
export { FeatureGrid } from "./FeatureGrid";
export { DataBar } from "./DataBar";
export { StatCounter } from "./StatCounter";
export { FlowChart } from "./FlowChart";
export { IconCard } from "./IconCard";
export { ChapterProgressBar } from "./ChapterProgressBar";
export { MediaSection, MediaGrid } from "./MediaSection";
export { DiagramReveal } from "./DiagramReveal";
export type { DiagramNode, DiagramEdge } from "./DiagramReveal";
export { AudioWaveform } from "./AudioWaveform";
export { LottieAnimation } from "./LottieAnimation";
export { DataTable } from "./DataTable";
export { ErrorBoundary } from "./ErrorBoundary";
export { Icon } from "./Icon";
export { getLucideIcon, isEmoji } from "./iconMap";
export { ShortIntroCard } from "./ShortIntroCard";
export { ShortCTACard } from "./ShortCTACard";

// Subtitles (renders SRT directly in Remotion — no FFmpeg re-encode needed)
export { Subtitles } from "./Subtitles";

// Timing data (runtime loading via staticFile, supports --public-dir)
export { useTiming, fetchTimingData } from "./useTiming";
export type { TimingData, TimingSection } from "./useTiming";
