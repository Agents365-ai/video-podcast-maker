import type { VideoProps } from "../Root";
import { useEntrance } from "./animations";

export const ShortIntroCard = ({
  props,
  title,
  subtitle,
  delay = 0,
}: {
  props: VideoProps;
  title: string;
  subtitle?: string;
  delay?: number;
}) => {
  const a = useEntrance(props.enableAnimations, delay, "snappy");

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
        <div style={{
          fontSize: 72,
          fontWeight: 800,
          color: props.primaryColor,
          lineHeight: 1.2,
        }}>
          {title}
        </div>
        {subtitle && (
          <div style={{
            fontSize: 36,
            fontWeight: 500,
            color: props.textColor,
            opacity: 0.5,
            marginTop: 24,
            lineHeight: 1.4,
          }}>
            {subtitle}
          </div>
        )}
      </div>
    </div>
  );
};
