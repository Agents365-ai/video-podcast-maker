import React from "react";
import type { VideoProps } from "../Root";
import { useEntrance } from "./animations";

export const QuoteBlock = ({
  props,
  quote,
  attribution,
  delay = 0,
}: {
  props: VideoProps;
  quote: string;
  attribution: string;
  delay?: number;
}) => {
  const anim = useEntrance(props.enableAnimations, delay);
  const attrAnim = useEntrance(props.enableAnimations, delay + 10);
  return (
    <div style={{
      width: "100%", textAlign: "center", padding: "40px 60px",
      opacity: anim.opacity, transform: `translateY(${anim.translateY}px) scale(${anim.scale})`,
      position: "relative",
    }}>
      {/* Background accent */}
      <div style={{
        position: "absolute", inset: 0, borderRadius: 24,
        background: `linear-gradient(135deg, ${props.primaryColor}06, ${props.accentColor}06)`,
        border: `1px solid ${props.primaryColor}10`,
      }} />
      {/* Left accent line */}
      <div style={{
        position: "absolute", left: 20, top: "15%", bottom: "15%", width: 4,
        background: `linear-gradient(180deg, ${props.primaryColor}, ${props.accentColor})`,
        borderRadius: 2,
      }} />
      {/* Opening quote mark */}
      <div style={{
        fontSize: 140, color: props.primaryColor, opacity: 0.15, lineHeight: 0.6,
        marginBottom: 16, fontFamily: "Georgia, serif",
      }}>
        &ldquo;
      </div>
      <p style={{
        fontSize: 40, fontWeight: 600, color: props.textColor,
        lineHeight: 1.6, fontStyle: "italic", position: "relative",
      }}>
        {quote}
      </p>
      <div style={{
        fontSize: 28, color: props.primaryColor, marginTop: 32, fontWeight: 500,
        opacity: attrAnim.opacity, transform: `translateY(${attrAnim.translateY}px)`,
      }}>
        &mdash; {attribution}
      </div>
    </div>
  );
};
