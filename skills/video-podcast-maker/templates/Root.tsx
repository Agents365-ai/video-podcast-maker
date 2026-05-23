/**
 * Remotion Root component template — multi-video registration pattern.
 *
 * Per-video setup (workflow Step 9 copies this template into your project):
 *
 * 1. Copy this file as `Root.tsx` (one per project, edit each time you add a video).
 * 2. For each video named `{video-name}`, copy `Video.tsx` as `{PascalCase}Video.tsx`
 *    (e.g. `reference-manager-comparison` → `ReferenceManagerComparisonVideo.tsx`).
 * 3. Import the per-video component: `import { Video as MyTopicVideo } from "./MyTopicVideo";`
 * 4. Register it with a UNIQUE composition id matching the PascalCase name:
 *      <Composition id="MyTopic" component={MyTopicVideo} ... />
 *    DO NOT reuse `id="MyVideo"` across videos — Remotion requires unique ids and
 *    multiple `videos/{name}/` directories must each map to a distinct id so
 *    `--public-dir videos/{name}/` selects the right composition.
 * 5. Each video brings its own timing.json/podcast_audio.wav under videos/{name}/.
 *
 * The example below is a SINGLE-VIDEO scaffold. Replace `MyVideo` /
 * `./Video` with your first video's PascalCase id + filename, and add more
 * `<Composition>` entries (each with its own id + import) as you add videos.
 */

import { Composition, Still } from "remotion";
import type { CalculateMetadataFunction } from "remotion";
import { z } from "zod";
import { Video } from "./Video";
import { Thumbnail } from "./Thumbnail";
import { fetchTimingData } from "./components";

// 【可视化编辑】: Zod Schema 定义可编辑属性
// Remotion Studio 会自动根据类型生成对应的编辑 UI
export const videoSchema = z.object({
  // 颜色设置
  primaryColor: z.string().describe("主色调（标题、强调元素）"),
  backgroundColor: z.string().describe("背景色"),
  textColor: z.string().describe("正文文字颜色"),
  accentColor: z.string().describe("强调色（CTA、高亮）"),

  // 字体大小 (1080p design space, auto scale(2) to 4K)
  titleSize: z.number().min(72).max(120).describe("标题字号 (hero/section title)"),
  subtitleSize: z.number().min(30).max(68).describe("副标题字号"),
  bodySize: z.number().min(24).max(40).describe("正文字号"),

  // 进度条设置 (native 4K, outside scale(2))
  showProgressBar: z.boolean().describe("显示底部进度条"),
  progressBarHeight: z.number().min(80).max(150).describe("进度条高度"),
  progressFontSize: z.number().min(28).max(60).describe("进度条文字大小"),
  progressActiveColor: z.string().describe("进度条激活颜色"),

  // 音频设置
  bgmVolume: z.number().min(0).max(0.3).step(0.01).describe("BGM 音量"),

  // 动画设置
  enableAnimations: z.boolean().describe("启用入场动画"),

  // 转场设置
  transitionType: z.enum(["fade", "slide", "wipe", "none"]).describe("章节转场效果"),
  transitionDuration: z.number().min(0).max(30).describe("转场时长(帧数, 30帧=1秒)"),

  // 方向设置
  orientation: z.enum(["horizontal", "vertical"]).describe("视频方向: horizontal(16:9) / vertical(9:16)"),

  // 图标设置
  iconStyle: z.enum(["lucide", "emoji", "mixed"]).describe("图标风格: lucide(SVG) / emoji / mixed"),
  iconAnimation: z.enum(["entrance", "none"]).describe("图标动画: entrance / none"),
});

// 类型导出，供 Video.tsx 使用
export type VideoProps = z.infer<typeof videoSchema>;

// 【可视化编辑】: 默认值 - Studio 会显示这些作为初始值
export const defaultVideoProps: VideoProps = {
  // 颜色 - DeepSeek 蓝色系
  primaryColor: "#4f6ef7",
  backgroundColor: "#ffffff",
  textColor: "#1a1a1a",
  accentColor: "#FF6B6B",

  // 字体大小 (1080p design space, auto scale(2) to 4K)
  // Reference: PluginComparison hero=72, Superpowers hero=120, section=80
  titleSize: 80,
  subtitleSize: 40,
  bodySize: 28,

  // 进度条 (native 4K, matches Superpowers reference)
  showProgressBar: true,
  progressBarHeight: 130,
  progressFontSize: 38,
  progressActiveColor: "#4f6ef7",

  // 音频 — default OFF so Step 11 (FFmpeg) is the single BGM source.
  // Enabling this in Studio (e.g. 0.05) layers BGM inside the render; in that
  // case skip Step 11 to avoid double-BGM. See references/workflow-production.md
  // → "BGM source single-write rule" for details.
  bgmVolume: 0,

  // 动画
  enableAnimations: true,

  // 转场
  transitionType: "fade",
  transitionDuration: 15,

  // 方向
  orientation: "horizontal",

  // 图标
  iconStyle: "lucide",
  iconAnimation: "entrance",
};

// Composition id for THIS video.
// IMPORTANT: change this to your video's PascalCase name (e.g. "ReferenceManagerComparison")
// when you copy this file into a real project. Each video registered below
// MUST have a unique id — `--public-dir videos/{name}/` selects assets, the
// `id` selects the composition that consumes them.
const VIDEO_ID = "MyVideo";

// Dynamic duration from timing.json (loaded at render time via --public-dir)
const calculateVideoMetadata: CalculateMetadataFunction<VideoProps> = async ({
  props,
}) => {
  const timing = await fetchTimingData();
  return { durationInFrames: timing.total_frames, props };
};

export const RemotionRoot = () => {
  return (
    <>
      {/* 主视频 - 4K 分辨率，支持可视化编辑 */}
      <Composition
        id={VIDEO_ID}
        component={Video}
        durationInFrames={300}
        calculateMetadata={calculateVideoMetadata}
        fps={30}
        width={3840}
        height={2160}
        schema={videoSchema}
        defaultProps={defaultVideoProps}
      />

      {/* Vertical video - 9:16 for B站竖屏/短视频 */}
      <Composition
        id="MyVideoVertical"
        component={Video}
        durationInFrames={300}
        calculateMetadata={calculateVideoMetadata}
        fps={30}
        width={2160}
        height={3840}
        schema={videoSchema}
        defaultProps={{
          ...defaultVideoProps,
          orientation: "vertical",
          showProgressBar: false,
          titleSize: 96,
          subtitleSize: 48,
          bodySize: 36,
        }}
      />

      {/* 16:9 缩略图 - B站/YouTube 封面 */}
      <Still
        id="Thumbnail16x9"
        component={Thumbnail}
        width={1920}
        height={1080}
        defaultProps={{ aspectRatio: "16:9" }}
      />

      {/* 4:3 缩略图 - B站推荐流/动态 */}
      <Still
        id="Thumbnail4x3"
        component={Thumbnail}
        width={1200}
        height={900}
        defaultProps={{ aspectRatio: "4:3" }}
      />

      {/* 3:4 缩略图 - 小红书封面 */}
      <Still
        id="Thumbnail3x4"
        component={Thumbnail}
        width={1080}
        height={1440}
        defaultProps={{ aspectRatio: "3:4" }}
      />

      {/* 9:16 缩略图 - 竖屏封面 */}
      <Still
        id="Thumbnail9x16"
        component={Thumbnail}
        width={1080}
        height={1920}
        defaultProps={{ aspectRatio: "9:16" }}
      />
    </>
  );
};
