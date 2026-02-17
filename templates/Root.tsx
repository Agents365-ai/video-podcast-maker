/**
 * Remotion Root 组件模板
 *
 * 使用说明：
 * 1. 将此文件复制到项目的 src/ 目录
 * 2. 确保 Video.tsx 和 Thumbnail.tsx 已创建
 * 3. 确保 timing.json 已生成
 */

import { Composition, Still } from "remotion";
import { Video } from "./Video";
import { Thumbnail } from "./Thumbnail";
import timing from "../public/timing.json";

// 【自定义点】: 修改视频 ID 和名称
const VIDEO_ID = "MyVideo";

export const RemotionRoot = () => {
  return (
    <>
      {/* 主视频 - 4K 分辨率 */}
      <Composition
        id={VIDEO_ID}
        component={Video}
        durationInFrames={timing.totalFrames}
        fps={30}
        width={3840}
        height={2160}
      />

      {/* 16:9 缩略图 - B站/YouTube 封面 */}
      <Still
        id="Thumbnail16x9"
        component={Thumbnail}
        width={1920}
        height={1080}
        defaultProps={{ aspectRatio: "16:9" }}
      />

      {/* 4:3 缩略图 - 部分平台需要 */}
      <Still
        id="Thumbnail4x3"
        component={Thumbnail}
        width={1600}
        height={1200}
        defaultProps={{ aspectRatio: "4:3" }}
      />

      {/* 1:1 缩略图 - 社交媒体分享 */}
      <Still
        id="Thumbnail1x1"
        component={Thumbnail}
        width={1080}
        height={1080}
        defaultProps={{ aspectRatio: "1:1" }}
      />
    </>
  );
};
