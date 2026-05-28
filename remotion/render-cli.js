/**
 * Remotion Ad Builder Render CLI
 * 
 * Usage: node render-cli.js <config.yaml> [output.mp4]
 * 
 * Reads the same YAML config format as the old MoviePy ad_from_config.py
 * and renders using Remotion instead.
 */

const path = require("path");
const fs = require("fs");
const yaml = require("js-yaml");
const { bundle } = require("@remotion/bundler");
const { renderMedia, selectComposition } = require("@remotion/renderer");

// ─── Config mapping ───
const PRESET_DIMENSIONS = {
  square: { width: 1080, height: 1080, id: "AdSquare" },
  story: { width: 1080, height: 1920, id: "AdStory" },
  landscape: { width: 1920, height: 1080, id: "AdLandscape" },
  spatrev: { width: 591, height: 1280, id: "SpatrevPromo" },
};

function resolveConfig(rawConfig) {
  const ad = rawConfig.ad || rawConfig;
  const presetName = (ad.preset || "square").toLowerCase();
  const preset = PRESET_DIMENSIONS[presetName] || PRESET_DIMENSIONS.square;

  // Resolve image paths relative to the config file's directory
  const configDir = rawConfig.__fileDir || process.cwd();
  const images = (ad.images || [])
    .filter((img) => typeof img === "string" && img.trim())
    .map((img) => path.resolve(configDir, img));

  return {
    compositionId: preset.id,
    width: preset.width,
    height: preset.height,
    inputProps: {
      headline: ad.headline || "",
      body: Array.isArray(ad.body) ? ad.body : [ad.body].filter(Boolean),
      cta: ad.cta || "",
      images,
      backgroundColor: ad.background_color || ad.backgroundColor || "#1a1a2e",
      textColor: ad.text_color || ad.textColor || "#ffffff",
      accentColor: ad.accent_color || ad.accentColor || "#e94560",
      videoLengthSeconds: ad.duration || ad.video_length_seconds || 30,
    },
    fps: 30,
    durationInFrames: (ad.duration || 30) * 30,
  };
}

// ─── Main ───
async function main() {
  const args = process.argv.slice(2);
  if (args.length < 1) {
    console.error("Usage: node render-cli.js <config.yaml> [output.mp4]");
    process.exit(1);
  }

  const configPath = path.resolve(args[0]);
  const outputPath = args[1]
    ? path.resolve(args[1])
    : path.resolve(
        path.dirname(configPath),
        "..",
        "output",
        `ad_${Date.now()}.mp4`
      );

  // Ensure output dir exists
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });

  // Read config
  const rawYaml = fs.readFileSync(configPath, "utf-8");
  const rawConfig = yaml.load(rawYaml);
  rawConfig.__fileDir = path.dirname(configPath);

  const resolved = resolveConfig(rawConfig);
  console.log("🎬 Remotion Ad Render");
  console.log(`   Composition: ${resolved.compositionId}`);
  console.log(`   Resolution:  ${resolved.width}x${resolved.height}`);
  console.log(`   Duration:    ${resolved.durationInFrames / resolved.fps}s`);
  console.log(`   Config:      ${resolved.inputProps.headline || "(no headline)"}`);
  console.log(`   Images:      ${resolved.inputProps.images.length}`);
  console.log(`   Output:      ${outputPath}`);

  // Bundle the Remotion project
  console.log("\n📦 Bundling Remotion project...");
  const bundleLocation = await bundle({
    entryPoint: path.resolve(__dirname, "src", "index.js"),
    webpackOverride: (config) => config,
  });

  // Select composition
  console.log("🔍 Selecting composition...");
  const composition = await selectComposition({
    serveUrl: bundleLocation,
    id: resolved.compositionId,
    inputProps: resolved.inputProps,
  });

  // Override duration from config
  composition.durationInFrames = resolved.durationInFrames;

  // Also override dimensions if different from default
  if (resolved.width && resolved.height) {
    composition.width = resolved.width;
    composition.height = resolved.height;
  }

  // Render
  console.log("🎥 Rendering video...");
  console.time("Render time");

  await renderMedia({
    composition,
    serveUrl: bundleLocation,
    codec: "h264",
    outputLocation: outputPath,
    inputProps: resolved.inputProps,
    chromiumOptions: {
      gl: "angle",
      executable: "/usr/bin/google-chrome-stable",
      headless: true,
    },
    imageFormat: "jpeg",
    timeoutInMilliseconds: 120000,
  });

  console.timeEnd("Render time");

  const sizeMB = (fs.statSync(outputPath).size / (1024 * 1024)).toFixed(1);
  console.log(`\n✅ Ad rendered successfully!`);
  console.log(`   File:   ${outputPath}`);
  console.log(`   Size:   ${sizeMB} MB`);
}

main().catch((err) => {
  console.error("❌ Render failed:", err.message);
  console.error(err.stack);
  process.exit(1);
});