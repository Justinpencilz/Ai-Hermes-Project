import { interpolate, useCurrentFrame, spring, Easing } from "remotion";

/**
 * Animated CTA (Call To Action) button.
 * Slides up + pulses to draw attention.
 */
export const CTAButton = ({
  text = "Learn More →",
  backgroundColor = "#e94560",
  textColor = "#ffffff",
  startFrame = 0,
  fontSize = 24,
  paddingHorizontal = 40,
  paddingVertical = 18,
}) => {
  const frame = useCurrentFrame();
  const relativeFrame = Math.max(0, frame - startFrame);

  // Slide up
  const y = interpolate(relativeFrame, [0, 25], [80, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.ease),
  });

  const opacity = interpolate(relativeFrame, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Pulse effect after settling
  const pulse = interpolate(
    Math.max(0, relativeFrame - 30),
    [0, 40, 80],
    [1, 1.08, 1],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "loop",
      easing: Easing.sin,
    }
  );

  // Glow effect
  const glowOpacity = interpolate(
    Math.max(0, relativeFrame - 20),
    [0, 30],
    [0, 0.3],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "loop",
    }
  );

  return (
    <div
      style={{
        transform: `translateY(${y}px) scale(${pulse})`,
        opacity,
        display: "inline-block",
      }}
    >
      <div
        style={{
          backgroundColor,
          color: textColor,
          fontSize,
          fontWeight: "bold",
          padding: `${paddingVertical}px ${paddingHorizontal}px`,
          borderRadius: 50,
          letterSpacing: 1,
          cursor: "pointer",
          boxShadow: `0 4px 15px ${backgroundColor}88, 0 0 30px ${backgroundColor}44`,
          textAlign: "center",
          whiteSpace: "nowrap",
        }}
      >
        {text}
      </div>
    </div>
  );
};