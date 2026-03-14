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
  // Vertical orientation forces single column for readability
  const v = props.orientation === "vertical";
  const cols = v ? 1 : columns;

  return (
    <div style={{
      display: "flex", flexWrap: "wrap", gap: v ? 24 : 28, width: "100%",
    }}>
      {items.map((item, i) => {
        const a = useEntrance(props.enableAnimations, delay + i * 5);
        return (
          <div key={i} style={{
            flex: `0 0 calc(${100 / cols}% - ${(v ? 24 : 28) * (cols - 1) / cols}px)`,
            background: "rgba(0,0,0,0.02)", border: "1px solid rgba(0,0,0,0.08)",
            borderRadius: 20, padding: v ? "32px 36px" : "36px 32px",
            textAlign: v ? "left" : "center",
            display: v ? "flex" : undefined, alignItems: v ? "center" : undefined, gap: v ? 24 : undefined,
            opacity: a.opacity, transform: `translateY(${a.translateY}px)`,
          }}>
            <div style={{ fontSize: v ? 48 : 56, marginBottom: v ? 0 : 16, flexShrink: 0 }}>{item.icon}</div>
            <div>
              <div style={{ fontSize: v ? 34 : 32, fontWeight: 700, color: props.primaryColor, marginBottom: 8 }}>
                {item.title}
              </div>
              <div style={{ fontSize: v ? 26 : 24, color: props.textColor, lineHeight: 1.5 }}>
                {item.description}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
};
