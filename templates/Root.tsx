/**
 * Remotion Root 组件模板 - 支持 Studio 可视化编辑
 *
 * 使用说明：
 * 1. 将此文件复制到项目的 src/ 目录
 * 2. 确保 Video.tsx 和 Thumbnail.tsx 已创建
 * 3. 确保 timing.json 已生成
 * 4. 运行 npx remotion studio 即可在右侧面板编辑样式
 */

import { Composition, Still } from "remotion";
import { z } from "zod";
import { Video } from "./Video";
import { Thumbnail } from "./Thumbnail";
import timing from "../public/timing.json";

// 【可视化编辑】: Zod Schema 定义可编辑属性
// Remotion Studio 会自动根据类型生成对应的编辑 UI
export const videoSchema = z.object({
  // 颜色设置
  primaryColor: z.string().describe("主色调（标题、强调元素）"),
  backgroundColor: z.string().describe("背景色"),
  textColor: z.string().describe("正文文字颜色"),
  accentColor: z.string().describe("强调色（CTA、高亮）"),

  // 字体大小
  titleSize: z.number().min(60).max(120).describe("标题字号"),
  subtitleSize: z.number().min(32).max(64).describe("副标题字号"),
  bodySize: z.number().min(20).max(40).describe("正文字号"),

  // 进度条设置
  showProgressBar: z.boolean().describe("显示底部进度条"),
  progressBarHeight: z.number().min(80).max(150).describe("进度条高度"),
  progressFontSize: z.number().min(40).max(80).describe("进度条文字大小"),
  progressActiveColor: z.string().describe("进度条激活颜色"),

  // 音频设置
  bgmVolume: z.number().min(0).max(0.3).step(0.01).describe("BGM 音量"),

  // 动画设置
  enableAnimations: z.boolean().describe("启用入场动画"),
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

  // 字体大小 (1080p 设计稿尺寸，4K 会自动 scale(2))
  titleSize: 80,
  subtitleSize: 48,
  bodySize: 28,

  // 进度条
  showProgressBar: true,
  progressBarHeight: 130,
  progressFontSize: 60,
  progressActiveColor: "#4f6ef7",

  // 音频
  bgmVolume: 0.05,

  // 动画
  enableAnimations: true,
};

// 视频 ID
const VIDEO_ID = "MyVideo";

export const RemotionRoot = () => {
  return (
    <>
      {/* 主视频 - 4K 分辨率，支持可视化编辑 */}
      <Composition
        id={VIDEO_ID}
        component={Video}
        durationInFrames={timing.total_frames}
        fps={30}
        width={3840}
        height={2160}
        schema={videoSchema}
        defaultProps={defaultVideoProps}
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
    </>
  );
};
