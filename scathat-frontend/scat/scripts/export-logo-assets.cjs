const { writeFileSync, mkdirSync } = require("node:fs")
const { join } = require("node:path")

function svgString(widthPx, heightPx) {
  return (
    `<?xml version="1.0" encoding="UTF-8"?>\n` +
    `<svg xmlns="http://www.w3.org/2000/svg" width="${widthPx}" height="${heightPx}" viewBox="0 0 ${widthPx} ${heightPx}">` +
    `<defs>` +
    `<linearGradient id="frame-g" x1="0" y1="0" x2="1" y2="1">` +
    `<stop offset="0%" stop-color="#10b981"/>` +
    `<stop offset="100%" stop-color="#06b6d4"/>` +
    `</linearGradient>` +
    `<radialGradient id="logo-g" cx="50%" cy="50%" r="60%">` +
    `<stop offset="0%" stop-color="#2dd4bf"/>` +
    `<stop offset="100%" stop-color="#22d3ee"/>` +
    `</radialGradient>` +
    `</defs>` +
    `<rect x="0" y="0" width="${widthPx}" height="${heightPx}" fill="#0f172a"/>` +
    `<rect x="300" y="300" width="${widthPx - 600}" height="${heightPx - 600}" rx="${Math.round(Math.min(widthPx, heightPx) * 0.04)}" fill="none" stroke="url(#frame-g)" stroke-width="600"/>` +
    `<circle cx="${widthPx / 2}" cy="${heightPx / 2 - Math.min(heightPx, widthPx) * 0.06}" r="${Math.round(Math.min(widthPx, heightPx) * 0.22)}" fill="url(#logo-g)"/>` +
    `<text x="${widthPx / 2}" y="${heightPx / 2 - Math.min(heightPx, widthPx) * 0.06 + Math.round(Math.min(widthPx, heightPx) * 0.22 * 0.28)}" text-anchor="middle" font-size="${Math.round(Math.min(widthPx, heightPx) * 0.22 * 0.9)}" font-weight="800" fill="#0f172a">S</text>` +
    `<text x="${widthPx / 2}" y="${heightPx / 2 + Math.min(heightPx, widthPx) * 0.22 + Math.min(heightPx, widthPx) * 0.08}" text-anchor="middle" font-size="${Math.round(Math.min(widthPx, heightPx) * 0.12)}" font-weight="800" fill="url(#frame-g)">Scathat</text>` +
    `</svg>`
  )
}

const outDir = join(process.cwd(), "public/brand")
mkdirSync(outDir, { recursive: true })
writeFileSync(join(outDir, "logo-framed-header.svg"), svgString(1920, 1920), "utf-8")
writeFileSync(join(outDir, "logo-framed-36in.svg"), svgString(10800, 10800), "utf-8")
writeFileSync(join(outDir, "logo-framed-8ft.svg"), svgString(14400, 14400), "utf-8")
console.log("Exported SVGs to public/brand")

