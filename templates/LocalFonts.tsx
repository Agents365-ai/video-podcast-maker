import { staticFile } from "remotion";

// Put font files in skills/video-podcast-maker/assets/fonts directory.
// These paths are resolved by Remotion staticFile() at render time.
const regularFont = staticFile("skills/video-podcast-maker/assets/fonts/SourceHanSansSC-Regular.otf");
const mediumFont = staticFile("skills/video-podcast-maker/assets/fonts/SourceHanSansSC-Medium.otf");
const boldFont = staticFile("skills/video-podcast-maker/assets/fonts/SourceHanSansSC-Bold.otf");

export const CJK_FONT_FAMILY =
  "'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'Source Han Sans SC Local', 'Source Han Sans SC', sans-serif";

export const LocalFonts = () => {
  return (
    <style>{`
      @font-face {
        font-family: 'Source Han Sans SC Local';
        src: url('${regularFont}') format('opentype');
        font-weight: 400;
        font-style: normal;
        font-display: swap;
      }
      @font-face {
        font-family: 'Source Han Sans SC Local';
        src: url('${mediumFont}') format('opentype');
        font-weight: 500 600;
        font-style: normal;
        font-display: swap;
      }
      @font-face {
        font-family: 'Source Han Sans SC Local';
        src: url('${boldFont}') format('opentype');
        font-weight: 700 900;
        font-style: normal;
        font-display: swap;
      }
    `}</style>
  );
};
