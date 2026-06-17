import React from "react";
import { useEntrance } from "./animations";
import type { TimingSection } from "./useTiming";

const SONG_FONT = '"Songti SC", "STSong", "Noto Serif SC", "Noto Serif CJK SC", serif';

export interface SlideProps {
  primaryColor: string;
  backgroundColor: string;
  textColor: string;
  accentColor: string;
  orientation: "horizontal" | "vertical";
  enableAnimations: boolean;
}

interface SlideLayoutProps {
  section: TimingSection;
  props: SlideProps;
}

const DecoLines = ({ props }: { props: SlideProps }) => (
  <>
    <div style={{ position: "absolute", top: 60, left: "8%", right: "8%", height: 1, background: `${props.primaryColor}16` }} />
    <div style={{ position: "absolute", bottom: 60, left: "8%", right: "8%", height: 1, background: `${props.primaryColor}16` }} />
  </>
);

const Seal = ({ text, props, size = 56 }: { text: string; props: SlideProps; size?: number }) => (
  <div style={{
    width: size, height: size,
    background: props.accentColor,
    display: "flex", alignItems: "center", justifyContent: "center",
    boxShadow: `0 4px 14px ${props.accentColor}35`,
    flexShrink: 0,
  }}>
    <span style={{ color: "#fff", fontFamily: SONG_FONT, fontSize: size * 0.45, fontWeight: 700 }}>{text}</span>
  </div>
);

const SlideContainer = ({
  children,
  props,
}: {
  children: React.ReactNode;
  props: SlideProps;
}) => {
  const v = props.orientation === "vertical";
  const { opacity, translateY, scale } = useEntrance(props.enableAnimations);
  return (
    <div style={{
      position: "absolute", inset: 0,
      background: `radial-gradient(circle at 50% 38%, ${props.primaryColor}0A, transparent 55%), ${props.backgroundColor}`,
      display: "flex", flexDirection: "column",
      justifyContent: "center", alignItems: "center",
      padding: v ? "120px 56px 160px" : "80px 120px 140px",
      opacity,
      transform: `translateY(${translateY}px) scale(${scale})`,
    }}>
      <DecoLines props={props} />
      {children}
    </div>
  );
};

const display = (section: TimingSection) => ({
  headline: section.headline || section.title || "",
  sub: section.sub || section.body || "",
  note: section.note || section.source || "",
});

// ── 开场 / 片头 ─────────────────────────────────────────
export const HeroSlide = ({ section, props }: SlideLayoutProps) => {
  const v = props.orientation === "vertical";
  const { headline, sub, note } = display(section);
  return (
    <SlideContainer props={props}>
      <div style={{ textAlign: "center", maxWidth: v ? "92%" : 900 }}>
        <Seal text="经" props={props} size={v ? 78 : 68} />
        <div style={{
          fontSize: v ? 28 : 24,
          color: props.accentColor,
          fontFamily: SONG_FONT,
          letterSpacing: 10,
          marginTop: v ? 36 : 28,
          marginBottom: v ? 20 : 16,
        }}>黄帝内经 · 上古天真论</div>
        <h1 style={{
          fontSize: v ? 80 : 96,
          fontWeight: 700,
          color: props.primaryColor,
          lineHeight: 1.3,
          fontFamily: SONG_FONT,
          letterSpacing: 8,
          marginBottom: v ? 28 : 24,
        }}>{headline}</h1>
        {sub && (
          <p style={{
            fontSize: v ? 42 : 36,
            color: props.textColor,
            opacity: 0.85,
            fontFamily: SONG_FONT,
            lineHeight: 1.6,
            marginBottom: v ? 16 : 12,
          }}>{sub}</p>
        )}
        {note && (
          <p style={{
            fontSize: v ? 32 : 28,
            color: props.textColor,
            opacity: 0.55,
            fontFamily: SONG_FONT,
          }}>{note}</p>
        )}
      </div>
    </SlideContainer>
  );
};

// ── 标题页（模块/章节） ──────────────────────────────────
export const TitleSlide = ({ section, props }: SlideLayoutProps) => {
  const v = props.orientation === "vertical";
  const { headline, sub, note } = display(section);
  return (
    <SlideContainer props={props}>
      <div style={{ textAlign: "center", maxWidth: v ? "88%" : 840 }}>
        <h2 style={{
          fontSize: v ? 64 : 72,
          fontWeight: 700,
          color: props.primaryColor,
          lineHeight: 1.35,
          fontFamily: SONG_FONT,
          letterSpacing: 6,
          marginBottom: v ? 32 : 24,
        }}>{headline}</h2>
        {sub && (
          <p style={{
            fontSize: v ? 34 : 30,
            color: props.textColor,
            opacity: 0.7,
            fontFamily: SONG_FONT,
            lineHeight: 1.7,
            marginBottom: v ? 12 : 10,
          }}>{sub}</p>
        )}
        {note && (
          <p style={{
            fontSize: v ? 28 : 24,
            color: props.accentColor,
            opacity: 0.8,
            fontFamily: SONG_FONT,
          }}>{note}</p>
        )}
      </div>
    </SlideContainer>
  );
};

// ── 提问页 ─────────────────────────────────────────────
export const QuestionSlide = ({ section, props }: SlideLayoutProps) => {
  const v = props.orientation === "vertical";
  const { headline, sub } = display(section);
  return (
    <SlideContainer props={props}>
      <div style={{ textAlign: "center", maxWidth: v ? "90%" : 860, position: "relative" }}>
        <div style={{
          position: "absolute",
          left: "50%", top: "50%",
          transform: "translate(-50%, -50%)",
          fontSize: v ? 320 : 280,
          color: props.accentColor,
          opacity: 0.08,
          fontFamily: SONG_FONT,
          fontWeight: 700,
          lineHeight: 1,
          pointerEvents: "none",
        }}>?</div>
        <h2 style={{
          fontSize: v ? 78 : 84,
          fontWeight: 700,
          color: props.primaryColor,
          lineHeight: 1.35,
          fontFamily: SONG_FONT,
          letterSpacing: 4,
          marginBottom: v ? 36 : 28,
        }}>{headline}</h2>
        {sub && (
          <p style={{
            fontSize: v ? 34 : 30,
            color: props.textColor,
            opacity: 0.7,
            fontFamily: SONG_FONT,
            lineHeight: 1.7,
          }}>{sub}</p>
        )}
      </div>
    </SlideContainer>
  );
};

// ── 原文引用页 ──────────────────────────────────────────
export const QuoteSlide = ({ section, props }: SlideLayoutProps) => {
  const v = props.orientation === "vertical";
  const { headline, sub, note } = display(section);
  return (
    <SlideContainer props={props}>
      <div style={{ textAlign: "center", maxWidth: v ? "88%" : 860 }}>
        <div style={{
          fontSize: v ? 120 : 100,
          color: props.accentColor,
          opacity: 0.18,
          fontFamily: SONG_FONT,
          lineHeight: 0.7,
          marginBottom: v ? 16 : 12,
        }}>“</div>
        <h2 style={{
          fontSize: v ? 52 : 48,
          fontWeight: 700,
          color: props.primaryColor,
          fontFamily: SONG_FONT,
          lineHeight: 1.55,
          letterSpacing: 4,
          marginBottom: v ? 28 : 22,
        }}>{headline}</h2>
        {sub && (
          <p style={{
            fontSize: v ? 32 : 28,
            color: props.textColor,
            opacity: 0.72,
            fontFamily: SONG_FONT,
            lineHeight: 1.8,
            marginBottom: v ? 24 : 18,
          }}>{sub}</p>
        )}
        {note && (
          <p style={{
            fontSize: v ? 26 : 22,
            color: props.accentColor,
            opacity: 0.75,
            fontFamily: SONG_FONT,
          }}>—— {note}</p>
        )}
      </div>
    </SlideContainer>
  );
};

// ── 核心概念页（大字 + 释义） ─────────────────────────────
export const TermSlide = ({ section, props }: SlideLayoutProps) => {
  const v = props.orientation === "vertical";
  const { headline, sub, note } = display(section);
  const chars = headline.length;
  const huge = chars <= 4 ? (v ? 132 : 120) : (v ? 96 : 88);
  return (
    <SlideContainer props={props}>
      <div style={{ textAlign: "center", maxWidth: v ? "92%" : 880, position: "relative" }}>
        <h2 style={{
          fontSize: huge,
          fontWeight: 700,
          color: props.primaryColor,
          fontFamily: SONG_FONT,
          lineHeight: 1.25,
          letterSpacing: 12,
          marginBottom: v ? 40 : 32,
        }}>{headline}</h2>
        {sub && (
          <p style={{
            fontSize: v ? 38 : 34,
            color: props.textColor,
            opacity: 0.8,
            fontFamily: SONG_FONT,
            lineHeight: 1.7,
            marginBottom: v ? 16 : 12,
          }}>{sub}</p>
        )}
        {note && (
          <p style={{
            fontSize: v ? 28 : 24,
            color: props.accentColor,
            opacity: 0.75,
            fontFamily: SONG_FONT,
          }}>{note}</p>
        )}
      </div>
    </SlideContainer>
  );
};

// ── 数字页 ─────────────────────────────────────────────
export const NumberSlide = ({ section, props }: SlideLayoutProps) => {
  const v = props.orientation === "vertical";
  const { headline, sub, note } = display(section);
  return (
    <SlideContainer props={props}>
      <div style={{ textAlign: "center", maxWidth: v ? "92%" : 900 }}>
        <div style={{
          fontSize: v ? 180 : 160,
          fontWeight: 700,
          color: props.primaryColor,
          fontFamily: SONG_FONT,
          lineHeight: 1.1,
          letterSpacing: 8,
          marginBottom: v ? 24 : 20,
        }}>{headline}</div>
        {sub && (
          <p style={{
            fontSize: v ? 44 : 40,
            color: props.textColor,
            opacity: 0.85,
            fontFamily: SONG_FONT,
            lineHeight: 1.6,
            marginBottom: v ? 16 : 12,
          }}>{sub}</p>
        )}
        {note && (
          <p style={{
            fontSize: v ? 28 : 24,
            color: props.accentColor,
            opacity: 0.7,
            fontFamily: SONG_FONT,
          }}>{note}</p>
        )}
      </div>
    </SlideContainer>
  );
};

// ── 古今对比页 ──────────────────────────────────────────
export const ContrastSlide = ({ section, props }: SlideLayoutProps) => {
  const v = props.orientation === "vertical";
  const { headline, sub } = display(section);
  const left = section.left || "上古";
  const right = section.right || "今时";
  return (
    <SlideContainer props={props}>
      <div style={{ width: v ? "92%" : 900, textAlign: "center" }}>
        <h2 style={{
          fontSize: v ? 48 : 44,
          fontWeight: 700,
          color: props.primaryColor,
          fontFamily: SONG_FONT,
          letterSpacing: 4,
          marginBottom: v ? 40 : 32,
        }}>{headline}</h2>
        <div style={{
          display: "flex",
          flexDirection: v ? "column" : "row",
          gap: v ? 24 : 28,
          marginBottom: v ? 32 : 28,
        }}>
          {[left, right].map((text, i) => (
            <div key={i} style={{
              flex: 1,
              background: i === 0 ? `${props.primaryColor}10` : `${props.accentColor}10`,
              border: `1px solid ${i === 0 ? props.primaryColor : props.accentColor}25`,
              borderRadius: 6,
              padding: v ? "32px 28px" : "36px 30px",
            }}>
              <div style={{
                fontSize: v ? 30 : 26,
                color: i === 0 ? props.primaryColor : props.accentColor,
                fontFamily: SONG_FONT,
                marginBottom: 12,
                opacity: 0.85,
              }}>{i === 0 ? "上古之人" : "今时之人"}</div>
              <div style={{
                fontSize: v ? 36 : 32,
                color: props.textColor,
                fontFamily: SONG_FONT,
                lineHeight: 1.6,
                fontWeight: 600,
              }}>{text}</div>
            </div>
          ))}
        </div>
        {sub && (
          <p style={{
            fontSize: v ? 30 : 26,
            color: props.textColor,
            opacity: 0.65,
            fontFamily: SONG_FONT,
          }}>{sub}</p>
        )}
      </div>
    </SlideContainer>
  );
};

// ── 列表页 ─────────────────────────────────────────────
export const ListSlide = ({ section, props }: SlideLayoutProps) => {
  const v = props.orientation === "vertical";
  const { headline } = display(section);
  const bullets = section.bullets && section.bullets.length > 0
    ? section.bullets
    : (section.body || "").split(/[，、；]/).map((s) => s.trim()).filter(Boolean);
  return (
    <SlideContainer props={props}>
      <div style={{ width: v ? "92%" : 900 }}>
        <h2 style={{
          fontSize: v ? 56 : 52,
          color: props.primaryColor,
          fontFamily: SONG_FONT,
          marginBottom: v ? 44 : 36,
          letterSpacing: 6,
          textAlign: "center",
        }}>{headline}</h2>
        <div style={{ display: "flex", flexDirection: "column", gap: v ? 22 : 18 }}>
          {bullets.slice(0, 4).map((clause, i) => (
            <div key={i} style={{
              display: "flex", alignItems: "center", gap: v ? 22 : 18,
              background: "rgba(255,255,255,0.55)",
              border: `1px solid ${props.primaryColor}12`,
              borderRadius: 4,
              padding: v ? "24px 28px" : "20px 24px",
            }}>
              <span style={{
                width: v ? 44 : 40,
                height: v ? 44 : 40,
                borderRadius: "50%",
                background: props.accentColor,
                color: "#fff",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontFamily: SONG_FONT,
                fontSize: v ? 24 : 22,
                flexShrink: 0,
              }}>{i + 1}</span>
              <span style={{
                fontSize: v ? 36 : 32,
                color: props.textColor,
                fontFamily: SONG_FONT,
                lineHeight: 1.5,
                fontWeight: 600,
              }}>{clause}</span>
            </div>
          ))}
        </div>
      </div>
    </SlideContainer>
  );
};

// ── 公式/四格页 ─────────────────────────────────────────
export const FormulaSlide = ({ section, props }: SlideLayoutProps) => {
  const v = props.orientation === "vertical";
  const { headline } = display(section);
  const bullets = section.bullets && section.bullets.length > 0
    ? section.bullets
    : (section.body || "").split(/[，、；]/).map((s) => s.trim()).filter(Boolean);
  const grid = bullets.slice(0, 4);
  return (
    <SlideContainer props={props}>
      <div style={{ width: v ? "92%" : 960 }}>
        <h2 style={{
          fontSize: v ? 52 : 48,
          color: props.primaryColor,
          fontFamily: SONG_FONT,
          marginBottom: v ? 40 : 32,
          letterSpacing: 5,
          textAlign: "center",
        }}>{headline}</h2>
        <div style={{
          display: "grid",
          gridTemplateColumns: v ? "1fr" : "1fr 1fr",
          gap: v ? 18 : 20,
        }}>
          {grid.map((phrase, i) => (
            <div key={i} style={{
              background: i % 2 === 0 ? `${props.primaryColor}08` : `${props.accentColor}08`,
              border: `1px solid ${i % 2 === 0 ? props.primaryColor : props.accentColor}18`,
              borderRadius: 6,
              padding: v ? "30px 24px" : "32px 28px",
              textAlign: "center",
            }}>
              <div style={{
                fontSize: v ? 42 : 38,
                color: i % 2 === 0 ? props.primaryColor : props.accentColor,
                fontFamily: SONG_FONT,
                fontWeight: 700,
                letterSpacing: 4,
                lineHeight: 1.4,
              }}>{phrase}</div>
            </div>
          ))}
        </div>
      </div>
    </SlideContainer>
  );
};

// ── 观点/结论页 ─────────────────────────────────────────
export const PrincipleSlide = ({ section, props }: SlideLayoutProps) => {
  const v = props.orientation === "vertical";
  const { headline, sub, note } = display(section);
  return (
    <SlideContainer props={props}>
      <div style={{ textAlign: "center", maxWidth: v ? "88%" : 840 }}>
        <h2 style={{
          fontSize: v ? 72 : 78,
          fontWeight: 700,
          color: props.primaryColor,
          fontFamily: SONG_FONT,
          lineHeight: 1.35,
          letterSpacing: 6,
          marginBottom: v ? 32 : 24,
        }}>{headline}</h2>
        {sub && (
          <p style={{
            fontSize: v ? 46 : 42,
            color: props.textColor,
            opacity: 0.88,
            fontFamily: SONG_FONT,
            lineHeight: 1.5,
            marginBottom: v ? 20 : 16,
          }}>{sub}</p>
        )}
        {note && (
          <p style={{
            fontSize: v ? 28 : 24,
            color: props.accentColor,
            opacity: 0.75,
            fontFamily: SONG_FONT,
          }}>{note}</p>
        )}
      </div>
    </SlideContainer>
  );
};

// ── 下期预告 ────────────────────────────────────────────
export const TeaserSlide = ({ section, props }: SlideLayoutProps) => {
  const v = props.orientation === "vertical";
  const { headline, sub, note } = display(section);
  return (
    <SlideContainer props={props}>
      <div style={{ textAlign: "center", maxWidth: v ? "90%" : 860 }}>
        <div style={{
          fontSize: v ? 30 : 26,
          color: props.accentColor,
          fontFamily: SONG_FONT,
          letterSpacing: 8,
          marginBottom: v ? 24 : 18,
        }}>{headline}</div>
        <h2 style={{
          fontSize: v ? 64 : 70,
          fontWeight: 700,
          color: props.primaryColor,
          fontFamily: SONG_FONT,
          lineHeight: 1.35,
          letterSpacing: 5,
          marginBottom: v ? 28 : 22,
        }}>{sub}</h2>
        {note && (
          <p style={{
            fontSize: v ? 36 : 32,
            color: props.textColor,
            opacity: 0.7,
            fontFamily: SONG_FONT,
          }}>{note}</p>
        )}
      </div>
    </SlideContainer>
  );
};

// ── 结束页 ─────────────────────────────────────────────
export const OutroSlide = ({ section, props }: SlideLayoutProps) => {
  const v = props.orientation === "vertical";
  const { headline, sub } = display(section);
  return (
    <SlideContainer props={props}>
      <div style={{ textAlign: "center", maxWidth: v ? "88%" : 820 }}>
        <Seal text="经" props={props} size={v ? 72 : 64} />
        <h2 style={{
          fontSize: v ? 76 : 88,
          fontWeight: 700,
          color: props.primaryColor,
          fontFamily: SONG_FONT,
          lineHeight: 1.35,
          letterSpacing: 8,
          marginTop: v ? 32 : 28,
          marginBottom: v ? 28 : 22,
        }}>{headline}</h2>
        {sub && (
          <p style={{
            fontSize: v ? 34 : 30,
            color: props.textColor,
            opacity: 0.7,
            fontFamily: SONG_FONT,
          }}>{sub}</p>
        )}
      </div>
    </SlideContainer>
  );
};

// Legacy fallbacks (kept for backward compatibility)
export const CenteredSlide = ({ section, props }: SlideLayoutProps) => {
  const v = props.orientation === "vertical";
  const { headline, sub } = display(section);
  return (
    <SlideContainer props={props}>
      <div style={{ textAlign: "center", maxWidth: v ? "88%" : 820 }}>
        <h2 style={{
          fontSize: v ? 56 : 48,
          fontWeight: 700,
          color: props.primaryColor,
          fontFamily: SONG_FONT,
          lineHeight: 1.45,
          letterSpacing: 3,
          marginBottom: v ? 36 : 28,
        }}>{headline}</h2>
        {sub && (
          <p style={{
            fontSize: v ? 34 : 30,
            color: props.textColor,
            opacity: 0.75,
            fontFamily: SONG_FONT,
            lineHeight: 1.85,
          }}>{sub}</p>
        )}
      </div>
    </SlideContainer>
  );
};

export const BulletsSlide = ListSlide;
export const SplitSlide = CenteredSlide;

export const renderSlide = (section: TimingSection, props: SlideProps) => {
  switch (section.layout) {
    case "hero": return <HeroSlide section={section} props={props} />;
    case "title": return <TitleSlide section={section} props={props} />;
    case "question": return <QuestionSlide section={section} props={props} />;
    case "quote": return <QuoteSlide section={section} props={props} />;
    case "term": return <TermSlide section={section} props={props} />;
    case "number": return <NumberSlide section={section} props={props} />;
    case "contrast": return <ContrastSlide section={section} props={props} />;
    case "list": return <ListSlide section={section} props={props} />;
    case "formula": return <FormulaSlide section={section} props={props} />;
    case "principle": return <PrincipleSlide section={section} props={props} />;
    case "teaser": return <TeaserSlide section={section} props={props} />;
    case "outro": return <OutroSlide section={section} props={props} />;
    case "bullets": return <BulletsSlide section={section} props={props} />;
    case "split": return <SplitSlide section={section} props={props} />;
    case "centered":
    default:
      return <CenteredSlide section={section} props={props} />;
  }
};
