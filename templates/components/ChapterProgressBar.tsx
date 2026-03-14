import React from "react";
import { useCurrentFrame } from "remotion";
import type { VideoProps } from "../Root";
import timing from "../../public/timing.json";

export const ChapterProgressBar = ({
  props,
  chapters,
}: {
  props: VideoProps;
  chapters: typeof timing.sections;
}) => {
  const frame = useCurrentFrame();
  const totalFrames = timing.total_frames;
  const progress = frame / totalFrames;

  if (!props.showProgressBar) return null;

  return (
    <div
      style={{
        position: "absolute",
        bottom: 0,
        left: 0,
        right: 0,
        height: props.progressBarHeight,
        background: "#fff",
        borderTop: "2px solid #e5e7eb",
        display: "flex",
        alignItems: "center",
        padding: "0 60px",
        gap: 20,
        fontFamily: "PingFang SC, Microsoft YaHei, sans-serif",
      }}
    >
      {chapters.map((ch) => {
        const chStart = ch.start_frame / totalFrames;
        const chEnd = (ch.start_frame + ch.duration_frames) / totalFrames;
        const isActive = progress >= chStart && progress < chEnd;
        const isPast = progress >= chEnd;
        const chProgress = isActive ? (progress - chStart) / (chEnd - chStart) : isPast ? 1 : 0;

        return (
          <div
            key={ch.name}
            style={{
              flex: ch.duration_frames,
              height: 76,
              borderRadius: 38,
              position: "relative",
              overflow: "hidden",
              background: isActive ? props.progressActiveColor : isPast ? "#f3f4f6" : "#f9fafb",
              border: isActive ? "none" : "2px solid #e5e7eb",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {isActive && (
              <div
                style={{
                  position: "absolute",
                  left: 0,
                  top: 0,
                  bottom: 0,
                  width: `${chProgress * 100}%`,
                  background: "rgba(255,255,255,0.25)",
                  borderRadius: 38,
                }}
              />
            )}
            <span
              style={{
                position: "relative",
                zIndex: 1,
                color: isActive ? "#fff" : isPast ? "#374151" : "#9ca3af",
                fontSize: props.progressFontSize,
                fontWeight: isActive ? 700 : 500,
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
                padding: "0 20px",
              }}
            >
              {ch.label || ch.name}
            </span>
          </div>
        );
      })}
      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          right: 0,
          height: 5,
          background: "#e5e7eb",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${progress * 100}%`,
            background: props.progressActiveColor,
          }}
        />
      </div>
    </div>
  );
};
