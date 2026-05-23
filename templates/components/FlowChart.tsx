import React from "react";
import type { VideoProps } from "../Root";
import { useEntrance, useDrawOn, staggerDelay } from "./animations";
import { Icon } from "./Icon";

// Arrow connector — centered SVG with proper viewBox
const ArrowConnector = ({
  vertical, color, enabled, delay,
}: {
  vertical: boolean; color: string; enabled: boolean; delay: number;
}) => {
  // Horizontal: 56 wide × 24 tall, arrow centered at y=12
  // Vertical: 24 wide × 48 tall, arrow centered at x=12
  const w = vertical ? 24 : 56;
  const h = vertical ? 48 : 24;
  const cx = w / 2;
  const cy = h / 2;

  const linePath = vertical
    ? `M ${cx} 2 L ${cx} ${h - 10}`
    : `M 2 ${cy} L ${w - 10} ${cy}`;
  const headPath = vertical
    ? `M ${cx - 6} ${h - 14} L ${cx} ${h - 6} L ${cx + 6} ${h - 14}`
    : `M ${w - 14} ${cy - 6} L ${w - 6} ${cy} L ${w - 14} ${cy + 6}`;

  const line = useDrawOn(linePath, enabled, delay, 18, "snappy");
  const head = useDrawOn(headPath, enabled, delay + 10, 10, "snappy");

  return (
    <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{ overflow: "visible" }}>
      <path
        d={linePath}
        fill="none"
        stroke={color}
        strokeWidth={2.5}
        strokeOpacity={0.5}
        strokeLinecap="round"
        strokeDasharray={line.strokeDasharray}
        strokeDashoffset={line.strokeDashoffset}
      />
      <path
        d={headPath}
        fill="none"
        stroke={color}
        strokeWidth={2.5}
        strokeOpacity={0.5}
        strokeLinecap="round"
        strokeLinejoin="round"
        strokeDasharray={head.strokeDasharray}
        strokeDashoffset={head.strokeDashoffset}
      />
    </svg>
  );
};

const FlowStep = ({
  index,
  step,
  props,
  delay,
  vertical,
  iconAnim,
  gapSize,
  isLast,
}: {
  index: number;
  step: { label: string; description?: string; icon?: string };
  props: VideoProps;
  delay: number;
  vertical: boolean;
  iconAnim: "none" | "entrance";
  gapSize: number;
  isLast: boolean;
}) => {
  const a = useEntrance(props.enableAnimations, staggerDelay(index, delay, 10), "snappy");
  return (
    <React.Fragment>
      <div style={{
        flex: 1, textAlign: "center",
        padding: vertical ? "28px 32px" : "32px 20px",
        background: `linear-gradient(135deg, ${props.primaryColor}08, ${props.primaryColor}14)`,
        borderRadius: 20,
        boxShadow: `0 2px 8px rgba(0,0,0,0.04), 0 4px 16px ${props.primaryColor}08`,
        border: `1px solid ${props.primaryColor}15`,
        opacity: a.opacity, transform: `translateY(${a.translateY}px)`,
        minWidth: 0,
        position: "relative",
        zIndex: 1,
      }}>
        {step.icon && (
          <div style={{ marginBottom: 12 }}>
            <Icon name={step.icon} size={vertical ? 44 : 48} color={props.primaryColor} animate={iconAnim} delay={staggerDelay(index, delay, 10)} />
          </div>
        )}
        <div style={{
          fontSize: vertical ? 42 : 40, fontWeight: 700, color: props.primaryColor,
        }}>
          {step.label}
        </div>
        {step.description && (
          <div style={{
            fontSize: vertical ? 34 : 32, color: props.textColor, marginTop: 8,
            opacity: 0.65, lineHeight: 1.4,
          }}>
            {step.description}
          </div>
        )}
      </div>
      {!isLast && (
        <div style={{
          width: vertical ? 24 : gapSize,
          height: vertical ? gapSize : 24,
          flexShrink: 0,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}>
          <ArrowConnector
            vertical={vertical}
            color={props.primaryColor}
            enabled={props.enableAnimations}
            delay={staggerDelay(index, delay + 5, 10)}
          />
        </div>
      )}
    </React.Fragment>
  );
};

export const FlowChart = ({
  props,
  steps,
  delay = 0,
}: {
  props: VideoProps;
  steps: { label: string; description?: string; icon?: string }[];
  delay?: number;
}) => {
  const v = props.orientation === "vertical";
  const iconAnim = props.iconAnimation === "none" ? "none" as const : "entrance" as const;
  const gapSize = v ? 48 : 56;
  const stepCount = steps.length;

  return (
    <div style={{
      display: "flex", alignItems: "center", width: "100%",
      flexDirection: v ? "column" : "row", gap: 0,
      position: "relative",
    }}>
      {steps.map((step, i) => (
        <FlowStep
          key={i}
          index={i}
          step={step}
          props={props}
          delay={delay}
          vertical={v}
          iconAnim={iconAnim}
          gapSize={gapSize}
          isLast={i === stepCount - 1}
        />
      ))}
    </div>
  );
};
