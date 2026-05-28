import { useCurrentFrame, interpolate, spring, Easing } from "remotion";

/**
 * Animated text with multiple animation styles.
 * animation: "fade-slide" | "scale-fade" | "slide-up" | "typewriter"
 */
export const KineticText = ({
  text,
  fontSize = 36,
  color = "#ffffff",
  animation = "fade-slide",
  startFrame = 0,
  delay = 0,
  fontWeight = "normal",
  uppercase = false,
  letterSpacing = 2,
}) => {
  const frame = useCurrentFrame();
  const relativeFrame = Math.max(0, frame - startFrame - delay);
  const displayText = uppercase ? text.toUpperCase() : text;

  let opacity = 1;
  let transform = "none";
  let clip = null;

  switch (animation) {
    case "fade-slide": {
      opacity = interpolate(relativeFrame, [0, 20], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      const y = interpolate(relativeFrame, [0, 25], [40, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
        easing: Easing.out(Easing.ease),
      });
      transform = `translateY(${y}px)`;
      break;
    }
    case "scale-fade": {
      opacity = interpolate(relativeFrame, [0, 15], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      const scale = interpolate(relativeFrame, [0, 30], [0.8, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
        easing: Easing.out(Easing.ease),
      });
      transform = `scale(${scale})`;
      break;
    }
    case "slide-up": {
      opacity = interpolate(relativeFrame, [0, 20], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      });
      const slideY = interpolate(relativeFrame, [0, 25], [60, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
        easing: Easing.out(Easing.ease),
      });
      transform = `translateY(${slideY}px)`;
      break;
    }
    case "typewriter": {
      const charsToShow = Math.min(
        Math.floor(relativeFrame / 3),
        displayText.length
      );
      clip = { chars: charsToShow, full: displayText };
      break;
    }
  }

  return (
    <div
      style={{
        fontSize,
        color,
        fontWeight,
        letterSpacing,
        textAlign: "center",
        lineHeight: 1.3,
        opacity,
        transform,
        transition: "none",
        textShadow: "0 2px 10px rgba(0,0,0,0.5)",
        width: "100%",
      }}
    >
      {clip ? (
        <span>
          {clip.full.substring(0, clip.chars)}
          <span style={{ opacity: 0.4 }}>|</span>
        </span>
      ) : (
        displayText
      )}
    </div>
  );
};