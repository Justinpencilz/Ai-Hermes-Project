import { AbsoluteFill, Sequence, useCurrentFrame, useVideoConfig, interpolate, spring, Easing, Img, Audio, continueRender, delayRender } from "remotion";
import { useEffect, useState } from "react";
import { KineticText } from "./components/KineticText";
import { ImageOverlay } from "./components/ImageOverlay";
import { CTAButton } from "./components/CTAButton";

// Helper: hex color to RGBA with opacity
const hexToRgba = (hex, opacity = 1) => {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
};

export const AdComposition = ({
  headline = "Headline",
  body = [],
  cta = "",
  images = [],
  backgroundColor = "#1a1a2e",
  textColor = "#ffffff",
  accentColor = "#e94560",
  videoLengthSeconds = 30,
}) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const totalFrames = fps * videoLengthSeconds;
  const isVertical = height > width;

  // === TIMING (in frames) ===
  const INTRO_DURATION = fps * 2;       // 2s intro animation
  const HEADLINE_DURATION = fps * 4;     // 4s headline visible + animation
  const BODY_START = INTRO_DURATION + HEADLINE_DURATION - fps * 1; // overlap headline
  const BODY_LINE_DELAY = 15;            // frames between body lines
  const BODY_DURATION = fps * 6;         // 6s body text section
  const IMAGE_START = BODY_START + fps * 2;
  const IMAGE_DURATION = fps * 8;        // 8s images section
  const CTA_DURATION = fps * 4;          // 4s CTA at end

  // Background gradient that subtly animates
  const bgShift = interpolate(frame, [0, totalFrames], [0, 30], {
    extrapolateRight: "clamp",
  });

  // === MAIN LAYOUT ===
  const padding = isVertical ? 60 : 80;
  const contentWidth = width - padding * 2;

  const animatedBgColor = hexToRgba(backgroundColor, 1);

  // Image fade-in after headline
  const showImage = frame >= IMAGE_START;
  const imageOpacity = interpolate(
    frame,
    [IMAGE_START, IMAGE_START + 15],
    [0, 1],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );

  return (
    <AbsoluteFill
      style={{
        backgroundColor: animatedBgColor,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding,
        overflow: "hidden",
      }}
    >
      {/* Decorative background elements */}
      <div
        style={{
          position: "absolute",
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          opacity: 0.15,
          background: `radial-gradient(circle at 50% 50%, ${hexToRgba(accentColor, 0.4)} 0%, transparent 70%)`,
        }}
      />

      {/* === INTRO SECTION === */}
      <Sequence name="Intro" durationInFrames={INTRO_DURATION}>
        <AbsoluteFill
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <KineticText
            text="FEATURED"
            fontSize={Math.min(width * 0.08, 48)}
            color={accentColor}
            animation="fade-slide"
            startFrame={0}
            letterSpacing={8}
            uppercase
          />
        </AbsoluteFill>
      </Sequence>

      {/* === HEADLINE SECTION === */}
      <Sequence
        name="Headline"
        from={INTRO_DURATION - 10}
        durationInFrames={HEADLINE_DURATION + 10}
      >
        <AbsoluteFill
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            padding: isVertical ? "0 40px" : "0 120px",
          }}
        >
          <KineticText
            text={headline}
            fontSize={Math.min(width * 0.09, isVertical ? 64 : 72)}
            color={textColor}
            animation="scale-fade"
            startFrame={Math.max(0, frame - INTRO_DURATION + 10)}
            fontWeight="bold"
          />
        </AbsoluteFill>
      </Sequence>

      {/* === BODY TEXT SECTION === */}
      {body.length > 0 && (
        <Sequence name="Body" from={BODY_START} durationInFrames={BODY_DURATION}>
          <AbsoluteFill
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              gap: 8,
              padding: isVertical ? "0 40px" : "0 160px",
            }}
          >
            {body.map((line, i) => (
              <KineticText
                key={i}
                text={line}
                fontSize={Math.min(width * 0.045, isVertical ? 32 : 36)}
                color={textColor}
                animation="slide-up"
                startFrame={i * BODY_LINE_DELAY}
                delay={i * 3}
              />
            ))}
          </AbsoluteFill>
        </Sequence>
      )}

      {/* === IMAGE SECTION === */}
      {images.length > 0 && (
        <Sequence name="Images" from={IMAGE_START} durationInFrames={IMAGE_DURATION}>
          <AbsoluteFill
            style={{
              display: "flex",
              flexDirection: "row",
              flexWrap: "wrap",
              alignItems: "center",
              justifyContent: "center",
              gap: 12,
              padding: isVertical ? "0 20px" : "0 60px",
            }}
          >
            {images.map((img, i) => (
              <ImageOverlay
                key={i}
                src={img}
                index={i}
                totalImages={images.length}
                startFrame={i * 20}
                containerWidth={contentWidth}
                isVertical={isVertical}
              />
            ))}
          </AbsoluteFill>
        </Sequence>
      )}

      {/* === CTA SECTION === */}
      {cta && (
        <Sequence
          name="CTA"
          from={totalFrames - CTA_DURATION - fps}
          durationInFrames={CTA_DURATION + fps}
        >
          <AbsoluteFill
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "flex-end",
              paddingBottom: isVertical ? 80 : 60,
            }}
          >
            <CTAButton
              text={cta}
              backgroundColor={accentColor}
              textColor="#ffffff"
              startFrame={0}
              fontSize={Math.min(width * 0.04, 28)}
            />
          </AbsoluteFill>
        </Sequence>
      )}
    </AbsoluteFill>
  );
};