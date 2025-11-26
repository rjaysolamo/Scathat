import fs from "fs"
import sharp from "sharp"

const srcSvg = "public/textures/grass-hero.svg"
const outDir = "public/textures"
const outputs = [
  { file: `${outDir}/grass-hero.png`, width: 2048, height: 2048, alpha: false },
  { file: `${outDir}/grass-hero-transparent.png`, width: 2048, height: 2048, alpha: true },
  { file: `${outDir}/grass-hero-left.png`, width: 2048, height: 2048, alpha: false, flop: true },
]

if (!fs.existsSync(srcSvg)) {
  throw new Error(`Missing ${srcSvg}`)
}

async function run() {
  const svg = fs.readFileSync(srcSvg)
  for (const cfg of outputs) {
    let img = sharp(svg, { density: 144 }).resize(cfg.width, cfg.height, { fit: "fill" })
    if (cfg.flop) {
      img = img.flop()
    }
    if (!cfg.alpha) {
      img = img.flatten({ background: { r: 16, g: 33, b: 16 } })
    }
    await img.png({ compressionLevel: 9, quality: 100 }).toFile(cfg.file)
  }
  console.log("Generated:")
  for (const cfg of outputs) console.log(" -", cfg.file)
}

run().catch((e) => {
  console.error(e)
  process.exit(1)
})
