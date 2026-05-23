import type { VideoProps } from "../Root";
import { useEntrance } from "./animations";
import { Icon } from "./Icon";

export const IconCard = ({
  props,
  icon,
  title,
  description,
  color,
  delay = 0,
}: {
  props: VideoProps;
  icon: string;
  title: string;
  description: string;
  color?: string;
  delay?: number;
}) => {
  const v = props.orientation === "vertical";
  const c = color || props.primaryColor;
  const a = useEntrance(props.enableAnimations, delay, "bouncy");
  const iconAnim = props.iconAnimation === "none" ? "none" : "entrance";

  return (
    <div style={{
      display: "flex", alignItems: "center", gap: v ? 28 : 32, width: "100%",
      padding: v ? "32px 36px" : "36px 44px",
      background: `linear-gradient(135deg, ${c}08, ${c}14)`,
      borderRadius: 24,
      border: `1px solid ${c}18`,
      boxShadow: `0 4px 16px ${c}10, 0 8px 24px rgba(0,0,0,0.04)`,
      opacity: a.opacity, transform: `translateY(${a.translateY}px) scale(${a.scale})`,
    }}>
      <div style={{
        flexShrink: 0,
        width: v ? 80 : 88, height: v ? 80 : 88,
        display: "flex", alignItems: "center", justifyContent: "center",
        background: `${c}12`, borderRadius: 20,
      }}>
        <Icon name={icon} size={v ? 48 : 56} color={c} animate={iconAnim} delay={delay} />
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: v ? 34 : 36, fontWeight: 700, color: c }}>
          {title}
        </div>
        <div style={{
          fontSize: v ? 26 : 24, color: props.textColor, marginTop: 8,
          lineHeight: 1.5, opacity: 0.75,
        }}>
          {description}
        </div>
      </div>
    </div>
  );
};
