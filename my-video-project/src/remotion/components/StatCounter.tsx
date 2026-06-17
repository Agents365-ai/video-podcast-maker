import React from "react";
import type { VideoProps } from "../Root";
import { useEntrance, useCounter } from "./animations";
import { Icon } from "./Icon";

export const StatCounter = ({
  props,
  items,
  delay = 0,
}: {
  props: VideoProps;
  items: { value: number; suffix?: string; label: string; icon?: string }[];
  delay?: number;
}) => {
  const v = props.orientation === "vertical";
  const iconAnim = props.iconAnimation === "none" ? "none" : "entrance";
  return (
    <div style={{
      display: "flex", gap: v ? 32 : 48, width: "100%",
      flexDirection: v ? "column" : "row", justifyContent: "center",
    }}>
      {items.map((item, i) => {
        const a = useEntrance(props.enableAnimations, delay + i * 8, "bouncy");
        const count = useCounter(item.value, delay + i * 8 + 5);
        return (
          <div key={i} style={{
            flex: v ? undefined : 1, textAlign: "center",
            padding: v ? "28px 36px" : "36px 24px",
            background: `linear-gradient(135deg, ${props.primaryColor}06, ${props.primaryColor}10)`,
            borderRadius: 24,
            boxShadow: `0 4px 16px ${props.primaryColor}10, 0 8px 32px rgba(0,0,0,0.04)`,
            border: `1px solid ${props.primaryColor}12`,
            opacity: a.opacity, transform: `translateY(${a.translateY}px) scale(${a.scale})`,
          }}>
            {item.icon && (
              <div style={{ marginBottom: 12 }}>
                <Icon name={item.icon} size={v ? 48 : 52} color={props.primaryColor} animate={iconAnim} delay={delay + i * 6} />
              </div>
            )}
            <div style={{
              fontSize: v ? 56 : 64, fontWeight: 800, color: props.primaryColor,
              letterSpacing: -2,
            }}>
              {count}{item.suffix || ""}
            </div>
            <div style={{
              fontSize: v ? 26 : 24, fontWeight: 500, color: props.textColor,
              marginTop: 8, opacity: 0.65,
            }}>
              {item.label}
            </div>
          </div>
        );
      })}
    </div>
  );
};
