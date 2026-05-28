import { Img, interpolate, useCurrentFrame, spring, Easing } from "remotion";

/**
 * Image overlay with fade-in + scale animation.
 * Images are centered and sized to fit within the container.
 */
export const ImageOverlay = ({
  src,
  index = 0,
  totalImages = 1,
  startFrame = 0,
  containerWidth = 800,
  isVertical = false,
}) => {
  const frame = useCurrentFrame();
  const relativeFrame = Math.max(0, frame - startFrame);

  // Calculate image size based on count
  const cols = Math.min(totalImages, isVertical ? 2 : 3);
  const maxImgWidth = Math.floor((containerWidth - (cols - 1) * 12) / cols);
  const imgSize = Math.min(maxImgWidth, isVertical ? 300 : 280);

  // Fade + scale in
  const opacity = interpolate(relativeFrame, [0, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const scale = interpolate(relativeFrame, [0, 25], [0.85, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.ease),
  });

  // Subtle breathing animation after settling
  const breathe = interpolate(
    Math.max(0, relativeFrame - 30),
    [0, 60],
    [1, 1.03],
    {
      extrapolateLeft: "clamp",
      extrapolateRight: "loop",
      easing: Easing.sin,
    }
  );

  return (
    <div
      style={{
        width: imgSize,
        height: imgSize * 0.75,
        borderRadius: 12,
        overflow: "hidden",
        opacity,
        transform: `scale(${scale * breathe * 0.95})`,
        boxShadow: "0 4px 20px rgba(0,0,0,0.3)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        backgroundColor: "#222",
      }}
    >
      <Img
        src={src}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
        }}
      />
    </div>
  );
};