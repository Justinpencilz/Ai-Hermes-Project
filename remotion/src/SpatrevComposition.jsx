import {
  AbsoluteFill,
  Sequence,
  useCurrentFrame,
  interpolate,
  spring,
  Easing,
  Img,
  Audio,
  staticFile,
} from "remotion";
import React from "react";

// ─── Colors ───
const C = {
  bg: "#0a1628",
  bg2: "#0d1f3c",
  card: "#0f2744",
  accent: "#3b82f6",
  accentLight: "#60a5fa",
  gold: "#f59e0b",
  text: "#ffffff",
  textDim: "#94a3b8",
  textMuted: "#64748b",
};

// ─── Script timing (seconds → frames @ 30fps) ───
const FPS = 30;
const S = {
  hook: { start: 0, end: 3 },
  problem: { start: 4, end: 10 },
  solution: { start: 11, end: 18 },
  proof: { start: 19, end: 24 },
  features: { start: 25, end: 28 },
  cta: { start: 29, end: 30 },
};

const f = (sec) => Math.round(sec * FPS);
const TOTAL = f(30);

// ─── Helper: animated fade+slide ───
function useFadeSlide(frame, delay = 0, duration = 20, slidePx = 30) {
  const rel = Math.max(0, frame - delay);
  return {
    opacity: interpolate(rel, [0, duration], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
    }),
    transform: `translateY(${interpolate(rel, [0, duration], [slidePx, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.out(Easing.ease),
    })}px)`,
  };
}

// ─── Caption line ───
const Caption = ({ text, frame, delay, size = 28, color = C.text, weight = "bold", align = "center" }) => {
  const anim = useFadeSlide(frame, delay, 18, 20);
  return (
    <div
      style={{
        opacity: anim.opacity,
        transform: anim.transform,
        fontSize: size,
        fontWeight: weight,
        color,
        textAlign: align,
        lineHeight: 1.4,
        textShadow: "0 2px 12px rgba(0,0,0,0.6)",
        padding: "0 20px",
        maxWidth: "90%",
      }}
    >
      {text}
    </div>
  );
};

// ─── Subtle accent line ───
const AccentLine = ({ frame, delay }) => {
  const anim = useFadeSlide(frame, delay, 15, 0);
  const w = interpolate(Math.max(0, frame - delay), [0, 20], [0, 80], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <div
      style={{
        width: w,
        height: 3,
        borderRadius: 2,
        backgroundColor: C.accent,
        opacity: anim.opacity,
        margin: "8px 0",
      }}
    />
  );
};

// ─── Image frame with zoom effect ───
const ImageFrame = ({ src, frame, startFrame, overlay = true }) => {
  const rel = Math.max(0, frame - startFrame);
  const opacity = interpolate(rel, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const scale = interpolate(rel, [0, 30], [1.15, 1], {
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
      {overlay && (
        <AbsoluteFill
          style={{
            background:
              "linear-gradient(180deg, rgba(10,22,40,0.05) 0%, rgba(10,22,40,0.7) 50%, rgba(10,22,40,0.95) 100%)",
          }}
        />
      )}
    </AbsoluteFill>
  );
};

// ─── Feature bullet point ───
const FeatureBullet = ({ text, frame, delay, icon = "◆" }) => {
  const anim = useFadeSlide(frame, delay, 15, 15);
  return (
    <div
      style={{
        opacity: anim.opacity,
        transform: anim.transform,
        display: "flex",
        alignItems: "center",
        gap: 10,
        fontSize: 18,
        color: C.text,
        fontWeight: "500",
        padding: "6px 16px",
        backgroundColor: "rgba(59,130,246,0.08)",
        borderRadius: 8,
        borderLeft: `3px solid ${C.accent}`,
        width: "100%",
        maxWidth: 340,
      }}
    >
      <span style={{ color: C.accentLight, fontSize: 14 }}>{icon}</span>
      <span>{text}</span>
    </div>
  );
};

// ─── CTA Button ───
const CTASection = ({ frame, startFrame }) => {
  const anim = useFadeSlide(frame, startFrame, 20, 40);
  const pulse = interpolate(
    Math.max(0, frame - startFrame - 20),
    [0, 30, 60],
    [1, 1.06, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "loop", easing: Easing.sin }
  );

  return (
    <AbsoluteFill
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 16,
        opacity: anim.opacity,
        transform: anim.transform,
      }}
    >
      <div
        style={{
          fontSize: 40,
          fontWeight: "bold",
          color: C.text,
          textShadow: "0 2px 15px rgba(0,0,0,0.5)",
          textAlign: "center",
        }}
      >
        Join SPATREV
      </div>
      <div
        style={{
          fontSize: 14,
          color: C.textDim,
          letterSpacing: 3,
          textTransform: "uppercase",
          marginBottom: 8,
        }}
      >
        Spot the signal — before the move
      </div>
      <div
        style={{
          transform: `scale(${pulse})`,
          fontSize: 20,
          fontWeight: "bold",
          color: "#ffffff",
          backgroundColor: C.accent,
          padding: "14px 36px",
          borderRadius: 50,
          letterSpacing: 1,
          boxShadow: `0 4px 20px ${C.accent}66, 0 0 40px ${C.accent}33`,
          cursor: "pointer",
        }}
      >
        www.spatrev.com
      </div>
    </AbsoluteFill>
  );
};

// ─── Main Composition ───
export const SpatrevComposition = () => {
  const frame = useCurrentFrame();

  return (
    <AbsoluteFill
      style={{
        backgroundColor: C.bg,
        width: 591,
        height: 1280,
        overflow: "hidden",
        fontFamily: "Arial, Helvetica, sans-serif",
      }}
    >
      {/* Audio */}
      <Audio src={staticFile("spatrev_voiceover.mp3")} />

      {/* === SECTION 1: HOOK (0-3s) === */}
      <Sequence name="Hook" durationInFrames={f(4)}>
        <ImageFrame src="img1_home.jpg" frame={frame} startFrame={0} />
        <AbsoluteFill
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
            padding: "0 30px",
          }}
        >
          <Caption
            text="THE MARKET IS MOVING"
            frame={frame}
            delay={5}
            size={34}
            color={C.accentLight}
            weight="bold"
          />
          <AccentLine frame={frame} delay={20} />
          <Caption
            text='"…and most traders are missing it."'
            frame={frame}
            delay={25}
            size={22}
            color={C.textDim}
            weight="normal"
          />
        </AbsoluteFill>
      </Sequence>

      {/* === SECTION 2: PROBLEM (4-10s) === */}
      <Sequence name="Problem" from={f(3)} durationInFrames={f(8)}>
        <ImageFrame src="img1_home.jpg" frame={frame} startFrame={f(3)} />
        <AbsoluteFill
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
            padding: "0 24px",
            gap: 8,
          }}
        >
          <Caption
            text="Every second you wait,"
            frame={frame}
            delay={f(0) + 5}
            size={24}
            color={C.text}
          />
          <Caption
            text="signals are forming."
            frame={frame}
            delay={f(0) + 25}
            size={24}
            color={C.accentLight}
          />
          <Caption
            text="Entries are opening."
            frame={frame}
            delay={f(0) + 50}
            size={24}
            color={C.accentLight}
          />
          <Caption
            text="And closing — without you."
            frame={frame}
            delay={f(0) + 80}
            size={26}
            color="#ef4444"
            weight="bold"
          />
        </AbsoluteFill>
      </Sequence>

      {/* === SECTION 3: SOLUTION (11-18s) === */}
      <Sequence name="Solution" from={f(10)} durationInFrames={f(9)}>
        <ImageFrame src="img2_scanner.jpg" frame={frame} startFrame={f(10)} />
        <AbsoluteFill
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
            padding: "0 24px",
            gap: 6,
          }}
        >
          <Caption
            text="SPATREV"
            frame={frame}
            delay={f(0) + 5}
            size={40}
            color={C.accentLight}
            weight="bold"
          />
          <AccentLine frame={frame} delay={25} />
          <Caption
            text="Powered by Veltrix AI"
            frame={frame}
            delay={f(0) + 30}
            size={20}
            color={C.gold}
          />
          <Caption
            text="Scans every Forex & Crypto pair"
            frame={frame}
            delay={f(0) + 55}
            size={20}
            color={C.text}
          />
          <Caption
            text="Live • 24/7 • Precision Entries"
            frame={frame}
            delay={f(0) + 85}
            size={18}
            color={C.textMuted}
          />
        </AbsoluteFill>
      </Sequence>

      {/* === SECTION 4: PROOF (19-24s) === */}
      <Sequence name="Proof" from={f(18)} durationInFrames={f(7)}>
        <ImageFrame src="img3_signals.jpg" frame={frame} startFrame={f(18)} />
        <AbsoluteFill
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
            padding: "0 24px",
            gap: 6,
          }}
        >
          <Caption
            text="Crash 600 Index"
            frame={frame}
            delay={f(0) + 5}
            size={28}
            color={C.gold}
            weight="bold"
          />
          <Caption
            text="Sell at 24,022"
            frame={frame}
            delay={f(0) + 25}
            size={24}
            color={C.text}
          />
          <Caption
            text="Take Profit One — Hit ✅"
            frame={frame}
            delay={f(0) + 55}
            size={24}
            color={C.accentLight}
            weight="bold"
          />
          <Caption
            text="That's not luck. That's precision."
            frame={frame}
            delay={f(0) + 85}
            size={20}
            color={C.textDim}
            weight="normal"
          />
        </AbsoluteFill>
      </Sequence>

      {/* === SECTION 5: FEATURES (25-28s) === */}
      <Sequence name="Features" from={f(24)} durationInFrames={f(5)}>
        <ImageFrame src="img4_features.jpg" frame={frame} startFrame={f(24)} />
        <AbsoluteFill
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
            padding: "0 20px",
            gap: 8,
          }}
        >
          <Caption
            text="WHAT YOU GET"
            frame={frame}
            delay={f(0) + 5}
            size={22}
            color={C.accentLight}
            weight="bold"
          />
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: 8,
              marginTop: 10,
              width: "100%",
              alignItems: "center",
            }}
          >
            <FeatureBullet
              text="AI analyzing the market for you"
              frame={frame}
              delay={f(0) + 20}
            />
            <FeatureBullet
              text="Daily signal alerts on your phone"
              frame={frame}
              delay={f(0) + 35}
            />
            <FeatureBullet
              text="Full university: trading & digital skills"
              frame={frame}
              delay={f(0) + 50}
            />
            <FeatureBullet
              text="Up to 30% rewards for referrals"
              frame={frame}
              delay={f(0) + 65}
            />
          </div>
        </AbsoluteFill>
      </Sequence>

      {/* === SECTION 6: CTA (29-30s) === */}
      <Sequence name="CTA" from={f(28)} durationInFrames={f(3)}>
        <AbsoluteFill
          style={{
            background: `radial-gradient(circle at 50% 50%, ${C.bg2} 0%, ${C.bg} 100%)`,
          }}
        />
        <AbsoluteFill
          style={{
            background:
              "radial-gradient(circle at 50% 40%, rgba(59,130,246,0.12) 0%, transparent 60%)",
          }}
        />
        <CTASection frame={frame} startFrame={f(0)} />
      </Sequence>
    </AbsoluteFill>
  );
};