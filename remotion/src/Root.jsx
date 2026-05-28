import { Composition } from "remotion";
import { AdComposition } from "./AdComposition";
import { SpatrevComposition } from "./SpatrevComposition";
import { SpatrevCompositionV2 } from "./SpatrevCompositionV2";

const FPS = 30;
const DEFAULT_DURATION = 30;

export const RemotionRoot = () => {
  return (
    <>
      {/* Original ad compositions */}
      <Composition
        id="AdSquare"
        component={AdComposition}
        durationInFrames={DEFAULT_DURATION * FPS}
        fps={FPS}
        width={1080}
        height={1080}
        defaultProps={{
          headline: "Your Headline Here",
          body: ["Line 1", "Line 2"],
          cta: "Learn More →",
          images: [],
          backgroundColor: "#1a1a2e",
          textColor: "#ffffff",
          accentColor: "#e94560",
          videoLengthSeconds: DEFAULT_DURATION,
        }}
        calculateMetadata={({ props }) => {
          const dur = (props.videoLengthSeconds || DEFAULT_DURATION) * FPS;
          return { durationInFrames: dur };
        }}
      />
      <Composition
        id="AdStory"
        component={AdComposition}
        durationInFrames={DEFAULT_DURATION * FPS}
        fps={FPS}
        width={1080}
        height={1920}
        defaultProps={{
          headline: "Your Headline Here",
          body: ["Line 1", "Line 2"],
          cta: "Learn More →",
          images: [],
          backgroundColor: "#1a1a2e",
          textColor: "#ffffff",
          accentColor: "#e94560",
          videoLengthSeconds: DEFAULT_DURATION,
        }}
        calculateMetadata={({ props }) => {
          const dur = (props.videoLengthSeconds || DEFAULT_DURATION) * FPS;
          return { durationInFrames: dur };
        }}
      />
      <Composition
        id="AdLandscape"
        component={AdComposition}
        durationInFrames={DEFAULT_DURATION * FPS}
        fps={FPS}
        width={1920}
        height={1080}
        defaultProps={{
          headline: "Your Headline Here",
          body: ["Line 1", "Line 2"],
          cta: "Learn More →",
          images: [],
          backgroundColor: "#1a1a2e",
          textColor: "#ffffff",
          accentColor: "#e94560",
          videoLengthSeconds: DEFAULT_DURATION,
        }}
        calculateMetadata={({ props }) => {
          const dur = (props.videoLengthSeconds || DEFAULT_DURATION) * FPS;
          return { durationInFrames: dur };
        }}
      />

      {/* Spatrev platform promo — v1 */}
      <Composition
        id="SpatrevPromo"
        component={SpatrevComposition}
        durationInFrames={30 * FPS}
        fps={FPS}
        width={591}
        height={1280}
      />

      {/* Spatrev platform promo — v2 (dynamic motion) */}
      <Composition
        id="SpatrevPromoV2"
        component={SpatrevCompositionV2}
        durationInFrames={30 * FPS}
        fps={FPS}
        width={591}
        height={1280}
      />
    </>
  );
};