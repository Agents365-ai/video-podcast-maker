import type { VideoProps } from "../Root";
import { useEntrance } from "./animations";

export const FeatureGrid = ({
  props,
  items,
  columns = 3,
  delay = 0,
}: {
  props: VideoProps;
  items: { icon: string; title: string; description: string }[];
  columns?: 2 | 3;
  delay?: number;
}) => {
  const v = props.orientation === "vertical";
  const cols = v ? 1 : columns;

  return (
    <div style={{
      display: "flex", flexWrap: "wrap", gap: v ? 24 : 28, width: "100%",
    }}>
      {items.map((item, i) => {
        const a = useEntrance(props.enableAnimations, delay + i * 5, "snappy");
        return (
          <div key={i} style={{
            flex: `0 0 calc(${100 / cols}% - ${(v ? 24 : 28) * (cols - 1) / cols}px)`,
            background: `linear-gradient(135deg, rgba(255,255,255,0.9), ${props.primaryColor}06)`,
            border: `1px solid ${props.primaryColor}18`,
            borderRadius: 24,
            padding: v ? "32px 36px" : "36px 32px",
            textAlign: v ? "left" : "center",
            display: v ? "flex" : undefined, alignItems: v ? "center" : undefined, gap: v ? 24 : undefined,
            boxShadow: `0 2px 8px rgba(0,0,0,0.04), 0 8px 24px rgba(0,0,0,0.06)`,
            opacity: a.opacity, transform: `translateY(${a.translateY}px)`,
          }}>
            <div style={{
              fontSize: v ? 48 : 56, marginBottom: v ? 0 : 16, flexShrink: 0,
              filter: "drop-shadow(0 2px 4px rgba(0,0,0,0.1))",
            }}>
              {item.icon}
            </div>
            <div>
              <div style={{ fontSize: v ? 34 : 32, fontWeight: 700, color: props.primaryColor, marginBottom: 8 }}>
                {item.title}
              </div>
              <div style={{ fontSize: v ? 26 : 24, color: props.textColor, lineHeight: 1.5, opacity: 0.75 }}>
                {item.description}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
