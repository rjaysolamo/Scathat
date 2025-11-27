"use client"

import React from "react"

type LogoFramedProps = {
  widthPx?: number
  heightPx?: number
  borderInch?: number
  dpi?: number
  backgroundHex?: string
  frameGradientStart?: string
  frameGradientEnd?: string
  logoGradientStart?: string
  logoGradientEnd?: string
  decorative?: boolean
}

export function LogoFramed({
  widthPx = 3000,
  heightPx = 3000,
  borderInch = 2,
  dpi = 300,
  backgroundHex = "#0f172a",
  frameGradientStart = "#10b981",
  frameGradientEnd = "#06b6d4",
  logoGradientStart = "#2dd4bf",
  logoGradientEnd = "#22d3ee",
  decorative = true,
}: LogoFramedProps) {
  const borderPx = Math.max(1, Math.round(borderInch * dpi))
  const vbW = widthPx
  const vbH = heightPx
  const contentW = vbW - borderPx
  const contentH = vbH - borderPx
  const frameRadius = Math.round(Math.min(vbW, vbH) * 0.04)
  const logoCircleR = Math.round(Math.min(contentW, contentH) * 0.22)
  const logoCircleCx = vbW / 2
  const logoCircleCy = vbH / 2 - Math.min(vbH, vbW) * 0.06
  const wordmarkY = logoCircleCy + logoCircleR + Math.min(vbH, vbW) * 0.08

  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width={widthPx}
      height={heightPx}
      viewBox={`0 0 ${vbW} ${vbH}`}
    >
      <defs>
        <linearGradient id="frame-g" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor={frameGradientStart} />
          <stop offset="100%" stopColor={frameGradientEnd} />
        </linearGradient>
        <radialGradient id="logo-g" cx="50%" cy="50%" r="60%">
          <stop offset="0%" stopColor={logoGradientStart} />
          <stop offset="100%" stopColor={logoGradientEnd} />
        </radialGradient>
        <filter id="softGlow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation={Math.max(6, Math.round(Math.min(vbW, vbH) * 0.006))} result="blur" />
          <feMerge>
            <feMergeNode in="blur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>

      <rect x={0} y={0} width={vbW} height={vbH} fill={backgroundHex} />

      <rect
        x={borderPx / 2}
        y={borderPx / 2}
        width={vbW - borderPx}
        height={vbH - borderPx}
        rx={frameRadius}
        ry={frameRadius}
        fill="none"
        stroke="url(#frame-g)"
        strokeWidth={borderPx}
      />

      {decorative && (
        <g filter="url(#softGlow)">
          <circle cx={logoCircleCx} cy={logoCircleCy} r={logoCircleR * 1.08} fill={logoGradientStart} opacity={0.08} />
          <circle cx={logoCircleCx} cy={logoCircleCy} r={logoCircleR * 1.2} fill={logoGradientEnd} opacity={0.06} />
        </g>
      )}

      <circle cx={logoCircleCx} cy={logoCircleCy} r={logoCircleR} fill="url(#logo-g)" />

      <text
        x={logoCircleCx}
        y={logoCircleCy + Math.round(logoCircleR * 0.28)}
        textAnchor="middle"
        fontSize={Math.round(logoCircleR * 0.9)}
        fontWeight={800}
        fill="#0f172a"
      >
        S
      </text>

      <text
        x={vbW / 2}
        y={wordmarkY}
        textAnchor="middle"
        fontSize={Math.round(Math.min(vbW, vbH) * 0.12)}
        fontWeight={800}
        fill="url(#frame-g)"
      >
        Scathat
      </text>
    </svg>
  )
}

