import type { VideoProps } from "../Root";
import { useEntrance } from "./animations";
import { Icon } from "./Icon";

export const ShortCTACard = ({
  props,
  text = "关注看完整版",
  delay = 0,
}: {
  props: VideoProps;
  text?: string;
  delay?: number;
}) => {
  const a = useEntrance(props.enableAnimations, delay, "gentle");

  return (
    <div style={{
      width: "100%",
      height: "100%",
      background: props.backgroundColor,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "80px 60px",
      boxSizing: "border-box",
    }}>
      <div style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        textAlign: "center",
        opacity: a.opacity,
        transform: `translateY(${a.translateY}px) scale(${a.scale})`,
      }}>
        <Icon name="play-circle" size={80} color={props.primaryColor} animate="entrance" delay={delay} />
        <div style={{
          fontSize: 52,
          fontWeight: 700,
          color: props.primaryColor,
          marginTop: 28,
        }}>
          {text}
        </div>
      </div>
    </div>
  );
};
