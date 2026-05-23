import { Img, staticFile } from "remotion";
import type { VideoProps } from "../Root";
import { useEntrance } from "./animations";

export const MediaSection = ({
  props,
  src,
  alt = "",
  caption,
  layout = "full",
  borderColor,
  delay = 0,
}: {
  props: VideoProps;
  src: string;
  alt?: string;
  caption?: string;
  layout?: "full" | "card" | "side-by-side";
  borderColor?: string;
  delay?: number;
}) => {
  const v = props.orientation === "vertical";
  const c = borderColor || props.primaryColor;
  const a = useEntrance(props.enableAnimations, delay, "gentle");

  const imgSrc = src.startsWith("http") ? src : staticFile(src);

  if (layout === "full") {
    return (
      <div style={{
        display: "flex", flexDirection: "column", alignItems: "center",
        width: "100%", gap: 16,
        opacity: a.opacity, transform: `translateY(${a.translateY}px) scale(${a.scale})`,
      }}>
        <div style={{
          width: "100%", borderRadius: 24, overflow: "hidden",
          border: `3px solid ${c}30`,
          boxShadow: `0 8px 32px ${c}15, 0 16px 48px rgba(0,0,0,0.08)`,
        }}>
          <Img src={imgSrc} alt={alt} style={{ width: "100%", display: "block" }} />
        </div>
        {caption && (
          <div style={{
            fontSize: v ? 24 : 26, color: props.textColor, opacity: 0.6,
            textAlign: "center", lineHeight: 1.5,
          }}>
            {caption}
          </div>
        )}
      </div>
    );
  }

  if (layout === "card") {
    return (
      <div style={{
        display: "flex", flexDirection: "column", gap: 16,
        padding: v ? "28px 32px" : "32px 40px",
        background: `linear-gradient(135deg, ${c}06, ${c}10)`,
        borderRadius: 28, border: `2px solid ${c}18`,
        boxShadow: `0 8px 24px ${c}10, 0 4px 12px rgba(0,0,0,0.04)`,
        opacity: a.opacity, transform: `translateY(${a.translateY}px) scale(${a.scale})`,
      }}>
        <div style={{ borderRadius: 20, overflow: "hidden" }}>
          <Img src={imgSrc} alt={alt} style={{ width: "100%", display: "block" }} />
        </div>
        {caption && (
          <div style={{
            fontSize: v ? 26 : 28, fontWeight: 600, color: c,
            textAlign: "center", lineHeight: 1.5,
          }}>
            {caption}
          </div>
        )}
      </div>
    );
  }

  // side-by-side: not used standalone, see MediaGrid below
  return null;
};

export const MediaGrid = ({
  props,
  items,
  columns = 2,
  delay = 0,
}: {
  props: VideoProps;
  items: { src: string; alt?: string; caption?: string; borderColor?: string }[];
  columns?: 2 | 3;
  delay?: number;
}) => {
  const v = props.orientation === "vertical";

  return (
    <div style={{
      display: "grid",
      gridTemplateColumns: v ? "1fr" : `repeat(${columns}, 1fr)`,
      gap: v ? 24 : 32,
      width: "100%",
    }}>
      {items.map((item, i) => (
        <MediaSection
          key={i}
          props={props}
          src={item.src}
          alt={item.alt}
          caption={item.caption}
          layout="card"
          borderColor={item.borderColor}
          delay={delay + i * 5}
        />
      ))}
    </div>
  );
};
