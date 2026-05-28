import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  interpolate,
  Easing,
  Img,
  Audio,
  staticFile,
  spring,
} from "remotion";
import React, { useMemo } from "react";

// ─── BRAND COLORS ───
const C = {
  bg0: "#050b18",
  bg1: "#0a1628",
  bg2: "#0d1f3c",
  bg3: "#112a4a",
  accent: "#2563eb",
  accentBright: "#3b82f6",
  accentGlow: "#60a5fa",
  accentDim: "#1d4ed8",
  gold: "#f59e0b",
  green: "#22c55e",
  red: "#ef4444",
  text: "#ffffff",
  textDim: "#94a3b8",
  textMuted: "#64748b",
  cardBg: "rgba(15, 39, 68, 0.7)",
};

// ─── HELPERS ───
const FPS = 30;
const f = (s) => Math.round(s * FPS);

function useFadeIn(frame, delay = 0, dur = 15) {
  const rel = Math.max(0, frame - delay);
  return {
    opacity: interpolate(rel, [0, dur], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }),
  };
}

function useSlideIn(frame, delay = 0, dir = "up", px = 30, dur = 20) {
  const rel = Math.max(0, frame - delay);
  const progress = interpolate(rel, [0, dur], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.ease),
  });
  const x = dir === "left" ? interpolate(rel, [0, dur], [-px, 0]) : 0;
  const y = dir === "up" ? interpolate(rel, [0, dur], [px, 0]) : dir === "down" ? interpolate(rel, [0, dur], [-px, 0]) : 0;
  return {
    opacity: progress,
    transform: `translate(${x}px, ${y}px)`,
  };
}

function useScaleIn(frame, delay = 0, from = 0.85) {
  const rel = Math.max(0, frame - delay);
  const scale = interpolate(rel, [0, 25], [from, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.back),
  });
  const opacity = interpolate(rel, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
  });
  return { opacity, transform: `scale(${scale})` };
}

function useZoomIn(frame, delay = 0, from = 1.2) {
  const rel = Math.max(0, frame - delay);
  const scale = interpolate(rel, [0, 40], [from, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.ease),
  });
  return { transform: `scale(${scale})` };
}

const AccentLine = ({ frame, delay, width = 60, color = C.accentBright }) => {
  const anim = useFadeIn(frame, delay, 12);
  const w = interpolate(Math.max(0, frame - delay), [0, 18], [0, width], {
    extrapolateLeft: "clamp",
  });
  return (
    <div style={{ width: w, height: 2.5, borderRadius: 2, backgroundColor: color, opacity: anim.opacity, margin: "8px 0" }} />
  );
};

const CaptionLine = ({ text, frame, delay, size = 24, color = C.text, weight = "bold", align = "center", glow = false }) => {
  const anim = useSlideIn(frame, delay, "up", 25, 18);
  return (
    <div
      style={{
        opacity: anim.opacity,
        transform: anim.transform,
        fontSize: size,
        fontWeight: weight,
        color,
        textAlign: align,
        lineHeight: 1.3,
        textShadow: glow ? `0 0 20px ${color}44, 0 2px 12px rgba(0,0,0,0.6)` : "0 2px 12px rgba(0,0,0,0.6)",
        padding: "0 16px",
        maxWidth: "92%",
      }}
    >
      {text}
    </div>
  );
};

// ─── TICKER TAPE ───
const TickerData = [
  { pair: "EUR/USD", price: "1.08542", change: "+0.24%" },
  { pair: "GBP/USD", price: "1.3558", change: "+0.12%" },
  { pair: "BTC/USD", price: "91,410", change: "+1.45%" },
  { pair: "ETH/USD", price: "3,020.6", change: "+0.89%" },
  { pair: "XAU/USD", price: "4,350.4", change: "-0.32%" },
  { pair: "USD/JPY", price: "156.25", change: "-0.18%" },
];

const LiveTicker = ({ frame }) => {
  const scrollX = interpolate(frame, [0, 300], [0, -2200], { extrapolateRight: "loop" });
  return (
    <div
      style={{
        position: "absolute",
        top: 0,
        left: 0,
        right: 0,
        height: 32,
        backgroundColor: "rgba(5,11,24,0.85)",
        backdropFilter: "blur(8px)",
        display: "flex",
        alignItems: "center",
        overflow: "hidden",
        borderBottom: "1px solid rgba(59,130,246,0.15)",
        zIndex: 50,
      }}
    >
      <div
        style={{
          display: "flex",
          gap: 24,
          transform: `translateX(${scrollX}px)`,
          whiteSpace: "nowrap",
          padding: "0 10px",
        }}
      >
        {[...TickerData, ...TickerData, ...TickerData].map((t, i) => (
          <div key={i} style={{ display: "flex", gap: 6, alignItems: "center", fontSize: 11, color: C.textDim }}>
            <span style={{ color: C.accentBright, fontWeight: "bold" }}>{t.pair}</span>
            <span style={{ color: C.text }}>{t.price}</span>
            <span style={{ color: t.change.startsWith("+") ? C.green : C.red }}>{t.change}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// ─── STAT BADGE ───
const StatBadge = ({ label, value, frame, delay }) => {
  const anim = useFadeIn(frame, delay, 10);
  return (
    <div style={{ opacity: anim.opacity, display: "flex", flexDirection: "column", alignItems: "center", gap: 2 }}>
      <span style={{ fontSize: 10, color: C.textMuted, letterSpacing: 2, textTransform: "uppercase" }}>{label}</span>
      <span style={{ fontSize: 16, fontWeight: "bold", color: C.accentGlow }}>{value}</span>
    </div>
  );
};

// ─── SIGNAL CARD ───
const SignalCard = ({ frame, delay }) => {
  const anim = useScaleIn(frame, delay, 0.7);
  return (
    <div
      style={{
        opacity: anim.opacity,
        transform: anim.transform,
        backgroundColor: C.cardBg,
        borderRadius: 12,
        border: "1px solid rgba(59,130,246,0.25)",
        padding: "14px 18px",
        width: "85%",
        maxWidth: 320,
        display: "flex",
        flexDirection: "column",
        gap: 8,
        backdropFilter: "blur(6px)",
      }}
    >
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <div style={{ width: 18, height: 18, borderRadius: 4, backgroundColor: C.red, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 9, fontWeight: "bold", color: "#fff" }}>S</div>
          <span style={{ fontSize: 13, fontWeight: "bold", color: C.text }}>Crash 600 Index</span>
        </div>
        <div style={{ fontSize: 10, color: C.green, backgroundColor: "rgba(34,197,94,0.12)", padding: "2px 8px", borderRadius: 20, fontWeight: "bold" }}>ACTIVE</div>
      </div>
      {/* Signal details */}
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: C.textDim }}>
        <span>Entry: <span style={{ color: C.text }}>24,022.57</span></span>
        <span>SL: <span style={{ color: C.red }}>24,260.75</span></span>
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: C.textDim }}>
        <span>TP1: <span style={{ color: C.green }}>23,784.37 ✓</span></span>
        <span>TP2: <span style={{ color: C.textDim }}>23,546.16</span></span>
      </div>
      {/* Confidence bar */}
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        <span style={{ fontSize: 10, color: C.textMuted }}>Confidence</span>
        <div style={{ flex: 1, height: 4, backgroundColor: "rgba(255,255,255,0.08)", borderRadius: 2 }}>
          <div style={{ width: "75%", height: "100%", backgroundColor: C.accentBright, borderRadius: 2 }} />
        </div>
        <span style={{ fontSize: 11, color: C.accentGlow, fontWeight: "bold" }}>75%</span>
      </div>
      {/* TRENDAI */}
      <div style={{ display: "flex", gap: 6, fontSize: 10, color: C.textMuted }}>
        <span>5M: <span style={{ color: C.red }}>BEAR</span></span>
        <span>30M: <span style={{ color: C.green }}>BULL</span></span>
        <span>1H: <span style={{ color: C.textDim }}>NEUTRAL</span></span>
      </div>
    </div>
  );
};

// ─── FEATURE CARD ───
const FeatureCard = ({ icon, title, desc, frame, delay, accentColor = C.accentBright }) => {
  const anim = useSlideIn(frame, delay, "up", 25, 16);
  return (
    <div
      style={{
        opacity: anim.opacity,
        transform: anim.transform,
        backgroundColor: C.cardBg,
        borderRadius: 10,
        border: `1px solid ${accentColor}22`,
        padding: "10px 14px",
        width: "85%",
        maxWidth: 320,
        display: "flex",
        gap: 10,
        alignItems: "center",
        backdropFilter: "blur(4px)",
      }}
    >
      <div
        style={{
          width: 28,
          height: 28,
          borderRadius: 8,
          backgroundColor: `${accentColor}18`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 14,
          flexShrink: 0,
        }}
      >
        {icon}
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 1 }}>
        <span style={{ fontSize: 13, fontWeight: "bold", color: C.text }}>{title}</span>
        <span style={{ fontSize: 11, color: C.textDim }}>{desc}</span>
      </div>
    </div>
  );
};

// ─── IMAGE BACKGROUND ───
const ImageBg = ({ src, frame, startFrame, zoomFrom = 1.15, gradient = true }) => {
  const rel = Math.max(0, frame - startFrame);
  const opacity = interpolate(rel, [0, 15], [0, 1], { extrapolateLeft: "clamp" });
  const scale = interpolate(rel, [0, 45], [zoomFrom, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.ease),
  });

  return (
    <AbsoluteFill style={{ opacity }}>
      <Img
        src={staticFile(src)}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          transform: `scale(${scale})`,
        }}
      />
      {gradient && (
        <AbsoluteFill
          style={{
            background:
              "linear-gradient(180deg, rgba(10,22,40,0.1) 0%, rgba(10,22,40,0.6) 40%, rgba(5,11,24,0.92) 80%, rgba(5,11,24,1) 100%)",
          }}
        />
      )}
    </AbsoluteFill>
  );
};

// ─── MAIN COMPOSITION ───
export const SpatrevCompositionV2 = () => {
  const frame = useCurrentFrame();

  // ── SECTION TIMING (frames) ──
  const T = {
    hook: { start: f(0), end: f(4.5) },
    problem: { start: f(4), end: f(10.5) },
    solution: { start: f(10), end: f(16.5) },
    proof: { start: f(16), end: f(22) },
    features: { start: f(21.5), end: f(27.5) },
    cta: { start: f(27), end: f(30) },
  };

  return (
    <AbsoluteFill
      style={{
        backgroundColor: C.bg0,
        width: 591,
        height: 1280,
        overflow: "hidden",
        fontFamily: "Arial, Helvetica, sans-serif",
      }}
    >
      {/* Audio */}
      <Audio src={staticFile("spatrev_voiceover_v2.mp3")} />

      {/* Live ticker — always visible */}
      <LiveTicker frame={frame} />

      {/* ═══════ SECTION 1 — HOOK (0-4.5s) ═══════ */}
      <Sequence name="Hook" durationInFrames={T.problem.end}>
        <ImageBg src="img1_home.jpg" frame={frame} startFrame={0} zoomFrom={1.1} />

        {/* Spatrev logo wordmark */}
        <AbsoluteFill style={{ display: "flex", alignItems: "center", justifyContent: "center", paddingTop: 60 }}>
          <CaptionLine text="SPATREV" frame={frame} delay={f(0.3)} size={46} color={C.accentGlow} weight="bold" glow />
          <AccentLine frame={frame} delay={f(0.8)} width={80} />
        </AbsoluteFill>

        {/* Hero text */}
        <AbsoluteFill style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
          <CaptionLine
            text="SPOT THE SIGNAL"
            frame={frame}
            delay={f(1.2)}
            size={36}
            color={C.text}
            weight="bold"
          />
          <CaptionLine
            text="BEFORE THE MOVE"
            frame={frame}
            delay={f(2)}
            size={36}
            color={C.accentBright}
            weight="bold"
            glow
          />
        </AbsoluteFill>

        {/* Stats badges */}
        <div
          style={{
            position: "absolute",
            bottom: 40,
            left: 0,
            right: 0,
            display: "flex",
            justifyContent: "space-around",
            padding: "0 40px",
          }}
        >
          <StatBadge label="UPTIME" value="99.9%" frame={frame} delay={f(2.5)} />
          <StatBadge label="LATENCY" value="≤14MS" frame={frame} delay={f(2.8)} />
          <StatBadge label="PAIRS" value="ALL" frame={frame} delay={f(3.1)} />
        </div>
      </Sequence>

      {/* ═══════ SECTION 2 — PROBLEM (4-10.5s) ═══════ */}
      <Sequence name="Problem" from={f(3.5)} durationInFrames={f(8)}>
        <ImageBg src="img2_scanner.jpg" frame={frame} startFrame={f(3.5)} zoomFrom={1.08} />

        <AbsoluteFill
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
            gap: 6,
          }}
        >
          <CaptionLine
            text="MOST TRADERS"
            frame={frame}
            delay={f(0.5)}
            size={22}
            color={C.textDim}
          />
          <CaptionLine
            text="CAN'T KEEP UP"
            frame={frame}
            delay={f(1.2)}
            size={32}
            color={C.text}
            weight="bold"
          />
          <CaptionLine
            text="Signals appear. Entries form."
            frame={frame}
            delay={f(2.5)}
            size={20}
            color={C.textDim}
            weight="normal"
          />
          <CaptionLine
            text="And then — they're gone."
            frame={frame}
            delay={f(4.5)}
            size={22}
            color={C.red}
            weight="bold"
          />
        </AbsoluteFill>
      </Sequence>

      {/* ═══════ SECTION 3 — SOLUTION (10-16.5s) ═══════ */}
      <Sequence name="Solution" from={f(9.5)} durationInFrames={f(8)}>
        <ImageBg src="img2_scanner.jpg" frame={frame} startFrame={f(9.5)} zoomFrom={1.05} />

        <AbsoluteFill
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
            gap: 4,
          }}
        >
          <CaptionLine
            text="SPATREV"
            frame={frame}
            delay={f(0.3)}
            size={40}
            color={C.accentGlow}
            weight="bold"
            glow
          />
          <CaptionLine
            text="Changes Everything"
            frame={frame}
            delay={f(1.0)}
            size={22}
            color={C.text}
          />
          <AccentLine frame={frame} delay={f(1.5)} width={50} />
          <CaptionLine
            text="Veltrix AI scans every pair — live"
            frame={frame}
            delay={f(2.0)}
            size={18}
            color={C.textDim}
            weight="normal"
          />
          <CaptionLine
            text="Exact Entry • Stop Loss • Take Profit"
            frame={frame}
            delay={f(3.5)}
            size={18}
            color={C.accentGlow}
          />
          <div style={{ marginTop: 20 }}>
            <CaptionLine
              text="All Forex & Crypto • 24/7"
              frame={frame}
              delay={f(5.5)}
              size={16}
              color={C.gold}
              weight="normal"
            />
          </div>
        </AbsoluteFill>
      </Sequence>

      {/* ═══════ SECTION 4 — PROOF (16-22s) ═══════ */}
      <Sequence name="Proof" from={f(15.5)} durationInFrames={f(7.5)}>
        <ImageBg src="img3_signals.jpg" frame={frame} startFrame={f(15.5)} zoomFrom={1.06} />

        <AbsoluteFill
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
            gap: 12,
          }}
        >
          <CaptionLine
            text="PRECISION IN ACTION"
            frame={frame}
            delay={f(0.3)}
            size={20}
            color={C.accentGlow}
            weight="bold"
          />
          <AccentLine frame={frame} delay={f(0.8)} width={40} />

          {/* Animated signal card */}
          <SignalCard frame={frame} delay={f(1.2)} />

          <CaptionLine
            text="That's not luck. That's precision."
            frame={frame}
            delay={f(4)}
            size={18}
            color={C.textDim}
            weight="normal"
          />
        </AbsoluteFill>
      </Sequence>

      {/* ═══════ SECTION 5 — FEATURES (21.5-27.5s) ═══════ */}
      <Sequence name="Features" from={f(21)} durationInFrames={f(7.5)}>
        <ImageBg src="img4_features.jpg" frame={frame} startFrame={f(21)} zoomFrom={1.12} />

        <AbsoluteFill
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
            gap: 8,
          }}
        >
          <CaptionLine
            text="PREMIUM TIER"
            frame={frame}
            delay={f(0.3)}
            size={20}
            color={C.gold}
            weight="bold"
          />
          <AccentLine frame={frame} delay={f(0.8)} width={50} color={C.gold} />

          <div style={{ display: "flex", flexDirection: "column", gap: 6, alignItems: "center", marginTop: 4 }}>
            <FeatureCard icon="⚡" title="Precision Signal Suite" desc="Live BUY/SELL signals with exact levels" frame={frame} delay={f(1.2)} />
            <FeatureCard icon="📊" title="Market Intelligence" desc="AI-driven market reports & analysis" frame={frame} delay={f(2.0)} />
            <FeatureCard icon="🎓" title="The Academy" desc="Full trading & digital skills university" frame={frame} delay={f(2.8)} accentColor={C.gold} />
            <FeatureCard icon="🤝" title="30% Referral Rewards" desc="Earn on every referral you bring in" frame={frame} delay={f(3.6)} accentColor={C.green} />
          </div>
        </AbsoluteFill>
      </Sequence>

      {/* ═══════ SECTION 6 — CTA (27-30s) ═══════ */}
      <Sequence name="CTA" from={f(26.5)} durationInFrames={f(4)}>
        <AbsoluteFill
          style={{
            background: `radial-gradient(ellipse at 50% 40%, ${C.bg3} 0%, ${C.bg1} 50%, ${C.bg0} 100%)`,
          }}
        />
        {/* Glow orb */}
        <AbsoluteFill
          style={{
            background: "radial-gradient(circle at 50% 35%, rgba(59,130,246,0.15) 0%, transparent 50%)",
          }}
        />

        <AbsoluteFill
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
            gap: 12,
          }}
        >
          <CaptionLine
            text="SPOT THE SIGNAL"
            frame={frame}
            delay={f(0.3)}
            size={32}
            color={C.text}
            weight="bold"
          />
          <CaptionLine
            text="BEFORE THE MOVE"
            frame={frame}
            delay={f(0.8)}
            size={32}
            color={C.accentGlow}
            weight="bold"
            glow
          />

          <div style={{ height: 8 }} />

          {/* Animated CTA button */}
          <div
            style={{
              opacity: interpolate(Math.max(0, frame - f(1.5)), [0, 18], [0, 1]),
              transform: `translateY(${interpolate(Math.max(0, frame - f(1.5)), [0, 20], [30, 0], {
                extrapolateLeft: "clamp",
                easing: Easing.out(Easing.ease),
              })}px) scale(${interpolate(Math.max(0, frame - f(2)), [0, 40, 80], [1, 1.06, 1], {
                extrapolateLeft: "clamp",
                extrapolateRight: "loop",
                easing: Easing.sin,
              })})`,
              fontSize: 18,
              fontWeight: "bold",
              color: "#ffffff",
              backgroundColor: C.accent,
              padding: "16px 40px",
              borderRadius: 50,
              letterSpacing: 2,
              boxShadow: `0 4px 25px ${C.accent}66, 0 0 50px ${C.accent}33`,
              cursor: "pointer",
              textAlign: "center",
            }}
          >
            www.spatrev.com
          </div>

          <CaptionLine
            text="$20/mo • No hidden fees"
            frame={frame}
            delay={f(2)}
            size={13}
            color={C.textMuted}
            weight="normal"
          />
        </AbsoluteFill>
      </Sequence>
    </AbsoluteFill>
  );
};