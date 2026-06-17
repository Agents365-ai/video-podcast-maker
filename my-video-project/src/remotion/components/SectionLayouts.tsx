/**
 * SectionLayouts — pre-built section layouts for visual variety
 *
 * These are higher-level layouts that combine backgrounds, animations,
 * and content placement. The agent picks one per section and fills in content.
 *
 * Each layout is theme-aware (uses props.primaryColor etc.) and
 * orientation-aware (adapts for 16:9 / 9:16).
 */

import { AbsoluteFill } from "remotion";
import { useEntrance, staggerDelay } from "./animations";
import { MovingGradient, FloatingShapes, GlowOrb, GridPattern, AccentLine } from "./AnimatedBackground";
import { Icon } from "./Icon";

// Common prop types
interface LayoutProps {
  primaryColor: string;
  accentColor: string;
  textColor: string;
  backgroundColor: string;
  enableAnimations: boolean;
  orientation?: "horizontal" | "vertical";
}

// ---------------------------------------------------------------------------
// 1. SplitLayout — content left, visual right (or stacked on vertical)
// Best for: feature highlight, product showcase, explanation + diagram
// ---------------------------------------------------------------------------
export const SplitLayout = ({
  props,
  title,
  description,
  rightContent,
  accent = "left",
}: {
  props: LayoutProps;
  title: string;
  description: string;
  rightContent: React.ReactNode;
  accent?: "left" | "right";
}) => {
  const v = props.orientation === "vertical";
  const anim = useEntrance(props.enableAnimations);
  const animR = useEntrance(props.enableAnimations, 12);

  return (
    <AbsoluteFill style={{ backgroundColor: props.backgroundColor }}>
      <MovingGradient color1={props.primaryColor} color2={props.accentColor} opacity={0.06} />
      <FloatingShapes color={props.primaryColor} count={3} opacity={0.04} shape="ring" />
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: v ? "column" : accent === "left" ? "row" : "row-reverse",
          alignItems: "center",
          padding: v ? "80px 60px" : "60px 80px",
          gap: v ? 40 : 60,
        }}
      >
        {/* Text side */}
        <div
          style={{
            flex: 1,
            opacity: anim.opacity,
            transform: `translateY(${anim.translateY}px) scale(${anim.scale})`,
          }}
        >
          <div
            style={{
              width: 60,
              height: 4,
              borderRadius: 2,
              background: props.primaryColor,
              marginBottom: 24,
            }}
          />
          <h2
            style={{
              fontSize: v ? 64 : 72,
              fontWeight: 800,
              color: props.primaryColor,
              lineHeight: 1.15,
              marginBottom: 20,
            }}
          >
            {title}
          </h2>
          <p
            style={{
              fontSize: v ? 32 : 30,
              color: props.textColor,
              lineHeight: 1.7,
              opacity: 0.75,
            }}
          >
            {description}
          </p>
        </div>
        {/* Visual side */}
        <div
          style={{
            flex: v ? undefined : 1,
            width: v ? "100%" : undefined,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            opacity: animR.opacity,
            transform: `translateY(${animR.translateY}px) scale(${animR.scale})`,
          }}
        >
          {rightContent}
        </div>
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// 2. StatHighlight — full-bleed big number with context
// Best for: key metric, percentage, count, impact statement
// ---------------------------------------------------------------------------
export const StatHighlight = ({
  props,
  value,
  unit = "",
  label,
  description,
}: {
  props: LayoutProps;
  value: string;
  unit?: string;
  label: string;
  description?: string;
}) => {
  const anim = useEntrance(props.enableAnimations, 0, "bouncy");

  return (
    <AbsoluteFill style={{ backgroundColor: props.backgroundColor }}>
      <GlowOrb color={props.primaryColor} size={600} opacity={0.1} blur={100} />
      <GridPattern color={props.primaryColor} opacity={0.03} variant="dots" />
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          opacity: anim.opacity,
          transform: `translateY(${anim.translateY}px) scale(${anim.scale})`,
        }}
      >
        <div style={{ display: "flex", alignItems: "baseline", gap: 8 }}>
          <span
            style={{
              fontSize: 160,
              fontWeight: 900,
              color: props.primaryColor,
              lineHeight: 1,
              letterSpacing: -4,
            }}
          >
            {value}
          </span>
          {unit && (
            <span style={{ fontSize: 48, fontWeight: 600, color: props.primaryColor, opacity: 0.7 }}>
              {unit}
            </span>
          )}
        </div>
        <p
          style={{
            fontSize: 40,
            fontWeight: 700,
            color: props.textColor,
            marginTop: 16,
          }}
        >
          {label}
        </p>
        {description && (
          <p
            style={{
              fontSize: 28,
              color: props.textColor,
              opacity: 0.5,
              marginTop: 12,
              maxWidth: 700,
              textAlign: "center",
            }}
          >
            {description}
          </p>
        )}
      </div>
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// 3. ZigzagCards — alternating left/right cards
// Best for: feature list, pros/cons, step-by-step explanation
// ---------------------------------------------------------------------------
export const ZigzagCards = ({
  props,
  title,
  items,
}: {
  props: LayoutProps;
  title: string;
  items: Array<{ icon: string; title: string; description: string; color?: string }>;
}) => {
  const v = props.orientation === "vertical";
  const titleAnim = useEntrance(props.enableAnimations);
  const colors = ["#4f6ef7", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899"];

  return (
    <AbsoluteFill style={{ backgroundColor: props.backgroundColor }}>
      <FloatingShapes color={props.primaryColor} count={4} opacity={0.04} />
      <div
        style={{
          position: "absolute",
          inset: 0,
          padding: v ? "60px 50px" : "50px 80px",
          display: "flex",
          flexDirection: "column",
        }}
      >
        <h2
          style={{
            fontSize: v ? 60 : 72,
            fontWeight: 800,
            color: props.primaryColor,
            marginBottom: v ? 32 : 28,
            opacity: titleAnim.opacity,
            transform: `translateY(${titleAnim.translateY}px)`,
          }}
        >
          {title}
        </h2>
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: "column",
            justifyContent: "center",
            gap: v ? 20 : 16,
          }}
        >
          {items.map((item, i) => (
            <ZigzagCard
              key={i}
              index={i}
              item={item}
              color={item.color || colors[i % colors.length]}
              props={props}
              alignRight={!v && i % 2 === 1}
            />
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const ZigzagCard = ({
  index,
  item,
  color,
  props,
  alignRight,
}: {
  index: number;
  item: { icon: string; title: string; description: string };
  color: string;
  props: LayoutProps;
  alignRight: boolean;
}) => {
  const anim = useEntrance(props.enableAnimations, staggerDelay(index, 8));
  const v = props.orientation === "vertical";

  return (
    <div
      style={{
        display: "flex",
        flexDirection: alignRight ? "row-reverse" : "row",
        alignItems: "center",
        gap: 24,
        background: `linear-gradient(135deg, ${color}08, ${color}04)`,
        borderRadius: 20,
        padding: v ? "24px 28px" : "20px 32px",
        borderLeft: alignRight ? "none" : `4px solid ${color}`,
        borderRight: alignRight ? `4px solid ${color}` : "none",
        boxShadow: `0 4px 20px ${color}10`,
        maxWidth: v ? "100%" : "75%",
        marginLeft: alignRight ? "auto" : 0,
        opacity: anim.opacity,
        transform: `translateY(${anim.translateY}px) scale(${anim.scale})`,
      }}
    >
      <Icon name={item.icon} size={v ? 48 : 44} color={color} />
      <div style={{ flex: 1 }}>
        <div style={{ fontSize: v ? 32 : 30, fontWeight: 700, color: props.textColor }}>{item.title}</div>
        <div style={{ fontSize: v ? 24 : 22, color: props.textColor, opacity: 0.6, marginTop: 4 }}>
          {item.description}
        </div>
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// 4. CenteredShowcase — centered content with decorative side elements
// Best for: key quote, main thesis, important conclusion
// ---------------------------------------------------------------------------
export const CenteredShowcase = ({
  props,
  icon,
  title,
  body,
}: {
  props: LayoutProps;
  icon?: string;
  title: string;
  body: string;
}) => {
  const anim = useEntrance(props.enableAnimations, 0, "snappy");

  return (
    <AbsoluteFill style={{ backgroundColor: props.backgroundColor }}>
      <GlowOrb color={props.primaryColor} size={500} x="20%" y="50%" opacity={0.08} blur={100} />
      <GlowOrb color={props.accentColor} size={400} x="80%" y="50%" opacity={0.06} blur={80} />
      <AccentLine color={props.primaryColor} width={200} position="top" delay={5} />
      <div
        style={{
          position: "absolute",
          inset: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "60px 100px",
          textAlign: "center",
          opacity: anim.opacity,
          transform: `translateY(${anim.translateY}px) scale(${anim.scale})`,
        }}
      >
        {icon && (
          <Icon name={icon} size={72} color={props.primaryColor} animate="entrance" />
        )}
        <h2
          style={{
            fontSize: 72,
            fontWeight: 800,
            color: props.primaryColor,
            marginTop: icon ? 24 : 0,
            marginBottom: 24,
            lineHeight: 1.2,
            maxWidth: 1200,
          }}
        >
          {title}
        </h2>
        <p
          style={{
            fontSize: 32,
            color: props.textColor,
            lineHeight: 1.7,
            opacity: 0.7,
            maxWidth: 1000,
          }}
        >
          {body}
        </p>
      </div>
      <AccentLine color={props.accentColor} width={160} position="bottom" delay={15} />
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------------------
// 5. MetricsRow — dashboard-style stat cards in a row
// Best for: comparison numbers, KPIs, benchmark results
// ---------------------------------------------------------------------------
export const MetricsRow = ({
  props,
  title,
  metrics,
}: {
  props: LayoutProps;
  title?: string;
  metrics: Array<{ value: string; label: string; icon?: string; color?: string }>;
}) => {
  const v = props.orientation === "vertical";
  const titleAnim = useEntrance(props.enableAnimations);
  const colors = ["#4f6ef7", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6"];

  return (
    <AbsoluteFill style={{ backgroundColor: props.backgroundColor }}>
      <MovingGradient color1={props.primaryColor} color2={props.accentColor} opacity={0.05} speed={0.2} />
      <div
        style={{
          position: "absolute",
          inset: 0,
          padding: v ? "60px 50px" : "60px 80px",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
        }}
      >
        {title && (
          <h2
            style={{
              fontSize: v ? 56 : 64,
              fontWeight: 800,
              color: props.primaryColor,
              marginBottom: v ? 40 : 48,
              textAlign: "center",
              opacity: titleAnim.opacity,
              transform: `translateY(${titleAnim.translateY}px)`,
            }}
          >
            {title}
          </h2>
        )}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: v
              ? metrics.length <= 2 ? "1fr" : "1fr 1fr"
              : `repeat(${Math.min(metrics.length, 4)}, 1fr)`,
            gap: v ? 20 : 28,
          }}
        >
          {metrics.map((m, i) => (
            <MetricCard
              key={i}
              index={i}
              metric={m}
              color={m.color || colors[i % colors.length]}
              props={props}
              vertical={v}
            />
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const MetricCard = ({
  index,
  metric,
  color,
  props,
  vertical,
}: {
  index: number;
  metric: { value: string; label: string; icon?: string; color?: string };
  color: string;
  props: LayoutProps;
  vertical: boolean;
}) => {
  const anim = useEntrance(props.enableAnimations, staggerDelay(index, 6, 8));
  return (
    <div
      style={{
        background: `linear-gradient(135deg, ${color}10, ${color}06)`,
        borderRadius: 24,
        padding: vertical ? "28px 24px" : "36px 32px",
        textAlign: "center",
        border: `2px solid ${color}20`,
        boxShadow: `0 8px 32px ${color}12`,
        opacity: anim.opacity,
        transform: `translateY(${anim.translateY}px) scale(${anim.scale})`,
      }}
    >
      {metric.icon && <Icon name={metric.icon} size={40} color={color} />}
      <div
        style={{
          fontSize: vertical ? 48 : 56,
          fontWeight: 900,
          color,
          marginTop: metric.icon ? 12 : 0,
          lineHeight: 1,
        }}
      >
        {metric.value}
      </div>
      <div
        style={{
          fontSize: vertical ? 22 : 24,
          color: props.textColor,
          opacity: 0.6,
          marginTop: 10,
          fontWeight: 500,
        }}
      >
        {metric.label}
      </div>
    </div>
  );
};

// ---------------------------------------------------------------------------
// 6. StepProgress — numbered steps with active highlight
// Best for: workflow, tutorial steps, process explanation
// ---------------------------------------------------------------------------
export const StepProgress = ({
  props,
  title,
  steps,
  activeStep,
}: {
  props: LayoutProps;
  title?: string;
  steps: Array<{ label: string; description?: string }>;
  activeStep?: number; // 0-based, highlight this step
}) => {
  const v = props.orientation === "vertical";
  const titleAnim = useEntrance(props.enableAnimations);
  const colors = ["#4f6ef7", "#8b5cf6", "#22c55e", "#f59e0b", "#ec4899", "#06b6d4"];

  return (
    <AbsoluteFill style={{ backgroundColor: props.backgroundColor }}>
      <GridPattern color={props.primaryColor} opacity={0.025} variant="dots" spacing={50} />
      <div
        style={{
          position: "absolute",
          inset: 0,
          padding: v ? "60px 50px" : "50px 80px",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {title && (
          <h2
            style={{
              fontSize: v ? 56 : 64,
              fontWeight: 800,
              color: props.primaryColor,
              marginBottom: v ? 36 : 40,
              opacity: titleAnim.opacity,
              transform: `translateY(${titleAnim.translateY}px)`,
            }}
          >
            {title}
          </h2>
        )}
        <div
          style={{
            flex: 1,
            display: "flex",
            flexDirection: v ? "column" : "row",
            alignItems: v ? "stretch" : "center",
            justifyContent: "center",
            gap: v ? 16 : 12,
          }}
        >
          {steps.map((step, i) => (
            <StepCard
              key={i}
              index={i}
              step={step}
              color={colors[i % colors.length]}
              isActive={activeStep === i}
              props={props}
              vertical={v}
            />
          ))}
        </div>
      </div>
    </AbsoluteFill>
  );
};

const StepCard = ({
  index,
  step,
  color,
  isActive,
  props,
  vertical,
}: {
  index: number;
  step: { label: string; description?: string };
  color: string;
  isActive: boolean;
  props: LayoutProps;
  vertical: boolean;
}) => {
  const anim = useEntrance(props.enableAnimations, staggerDelay(index, 6, 8));
  return (
    <div
      style={{
        flex: vertical ? undefined : 1,
        display: "flex",
        flexDirection: vertical ? "row" : "column",
        alignItems: "center",
        gap: vertical ? 20 : 12,
        background: isActive
          ? `linear-gradient(135deg, ${color}18, ${color}08)`
          : `${color}04`,
        borderRadius: 20,
        padding: vertical ? "20px 24px" : "28px 16px",
        border: `2px solid ${isActive ? color : `${color}15`}`,
        boxShadow: isActive ? `0 8px 32px ${color}20` : "none",
        opacity: anim.opacity,
        transform: `translateY(${anim.translateY}px) scale(${anim.scale * (isActive ? 1.02 : 1)})`,
      }}
    >
      <div
        style={{
          width: vertical ? 44 : 48,
          height: vertical ? 44 : 48,
          borderRadius: "50%",
          background: isActive ? color : `${color}20`,
          color: isActive ? "#fff" : color,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: vertical ? 22 : 24,
          fontWeight: 800,
          flexShrink: 0,
        }}
      >
        {index + 1}
      </div>
      <div style={{ textAlign: vertical ? "left" : "center" }}>
        <div
          style={{
            fontSize: vertical ? 26 : 24,
            fontWeight: 700,
            color: isActive ? color : props.textColor,
          }}
        >
          {step.label}
        </div>
        {step.description && (
          <div
            style={{
              fontSize: vertical ? 20 : 18,
              color: props.textColor,
              opacity: 0.5,
              marginTop: 4,
            }}
          >
            {step.description}
          </div>
        )}
      </div>
    </div>
  );
};
