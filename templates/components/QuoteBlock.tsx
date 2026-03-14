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
    }}>
      <div style={{
        fontSize: 120, color: props.primaryColor, opacity: 0.2, lineHeight: 0.6, marginBottom: 20,
      }}>
        &ldquo;
      </div>
      <p style={{
        fontSize: 40, fontWeight: 600, color: props.textColor,
        lineHeight: 1.6, fontStyle: "italic",
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
