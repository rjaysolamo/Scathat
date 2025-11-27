"use client"

import { motion, useScroll, useTransform, useMotionValue, useMotionTemplate, useSpring } from "framer-motion"
import { useEffect, useState } from "react"

type AnimatedBackgroundProps = {
  accentRGB?: [number, number, number]
  secondaryRGB?: [number, number, number]
  strength?: number
  noiseAlpha?: number
  vignetteAlpha?: number
  enableVignette?: boolean
}

export function AnimatedBackground(props: AnimatedBackgroundProps = {}) {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(true)

  // Check for reduced motion preference
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setPrefersReducedMotion(mediaQuery.matches)
    
    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches)
    }
    
    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])

  // Only use motion hooks if not in reduced motion mode
  const { scrollY } = useScroll()
  const easedScroll = useSpring(scrollY, { stiffness: 220, damping: 28, mass: 0.8 })
  const topGradientY = useTransform(easedScroll, [0, 600], [0, -140])
  const heroGradientX = useTransform(easedScroll, [0, 600], [0, 90])
  const heroGradientY = useTransform(easedScroll, [0, 600], [0, -120])
  const middleGradientY = useTransform(easedScroll, [0, 1400], [0, 180])
  const bottomGradientX = useTransform(easedScroll, [400, 2000], [0, -120])

  const topY = useSpring(topGradientY, { stiffness: 160, damping: 28, mass: 1 })
  const heroX = useSpring(heroGradientX, { stiffness: 160, damping: 28, mass: 1 })
  const heroY = useSpring(heroGradientY, { stiffness: 160, damping: 28, mass: 1 })
  const middleY = useSpring(middleGradientY, { stiffness: 160, damping: 28, mass: 1 })
  const bottomX = useSpring(bottomGradientX, { stiffness: 160, damping: 28, mass: 1 })

  // Mouse movement tracking
  const mouseX = useMotionValue(0)
  const mouseY = useMotionValue(0)
  
  const handleMouseMove = (e: React.MouseEvent) => {
    if (prefersReducedMotion) return
    
    const { clientX, clientY } = e
    const centerX = typeof window !== 'undefined' ? window.innerWidth / 2 : 0
    const centerY = typeof window !== 'undefined' ? window.innerHeight / 2 : 0
    
    mouseX.set((clientX - centerX) / 20)
    mouseY.set((clientY - centerY) / 20)
  }

  const mouseGradientX = useTransform(mouseX, [-500, 500], [-24, 24])
  const mouseGradientY = useTransform(mouseY, [-500, 500], [-24, 24])

  const strength = props.strength ?? 1
  const accent: [number, number, number] = props.accentRGB ?? [0, 242, 139]
  const secondary: [number, number, number] = props.secondaryRGB ?? [0, 217, 126]
  const noiseAlpha = props.noiseAlpha ?? 0.006
  const vignetteAlpha = props.vignetteAlpha ?? 0.16
  const enableVignette = props.enableVignette ?? true

  const rgba = (rgb: [number, number, number], a: number) => `rgba(${rgb[0]},${rgb[1]},${rgb[2]},${a})`
  const topColor = rgba(accent, 0.03 * strength)
  const heroColor = rgba(accent, 0.04 * strength)
  const middleColor = rgba(secondary, 0.02 * strength)
  const bottomColor = rgba(accent, 0.025 * strength)
  const heroFocusColor = rgba(accent, 0.08 * strength)

  const sectionColor = useTransform(
    easedScroll,
    [0, 600, 1400, 2200],
    [
      rgba(accent, 0.035 * strength),
      rgba(accent, 0.045 * strength),
      rgba(secondary, 0.06 * strength),
      rgba(accent, 0.05 * strength)
    ]
  )

  const combinedHeroX = useMotionTemplate`calc(${mouseGradientX}px + ${heroX}px)`
  const combinedHeroY = useMotionTemplate`calc(${mouseGradientY}px + ${heroY}px)`

  return (
    <motion.div 
      className="fixed inset-0 -z-10 pointer-events-none overflow-hidden"
      onMouseMove={handleMouseMove}
      style={{ cursor: 'none' }}
    >
      <motion.div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[1200px] h-[800px] rounded-full blur-3xl"
        style={{ y: prefersReducedMotion ? 0 : topY, willChange: 'transform', backgroundColor: topColor }}
        animate={{
          opacity: [0.03, 0.05, 0.03],
          scale: [1, 1.05, 1]
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      <motion.div
        className="absolute top-1/4 right-1/5 w-[600px] h-[600px] rounded-full blur-3xl"
        style={{ 
          x: prefersReducedMotion ? 0 : heroX,
          y: prefersReducedMotion ? 0 : heroY,
          willChange: 'transform',
          backgroundColor: heroColor
        }}
        animate={{
          opacity: [0.04, 0.06, 0.04],
          scale: [1, 1.03, 1]
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 2
        }}
      />

      <motion.div
        className="absolute top-2/3 left-1/6 w-[500px] h-[500px] rounded-full blur-3xl"
        style={{ y: prefersReducedMotion ? 0 : middleY, willChange: 'transform', backgroundColor: middleColor }}
        animate={{
          opacity: [0.02, 0.04, 0.02],
          scale: [1, 1.02, 1]
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 4
        }}
      />

      <motion.div
        className="absolute bottom-1/4 right-1/5 w-[700px] h-[700px] rounded-full blur-3xl"
        style={{ x: prefersReducedMotion ? 0 : bottomX, willChange: 'transform', backgroundColor: bottomColor }}
        animate={{
          opacity: [0.025, 0.035, 0.025],
          scale: [1, 1.04, 1]
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "easeInOut",
          delay: 6
        }}
      />

      <motion.div
        className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[400px] rounded-full blur-3xl"
        style={{
          x: prefersReducedMotion ? 0 : combinedHeroX,
          y: prefersReducedMotion ? 0 : combinedHeroY,
          willChange: 'transform',
          backgroundColor: heroFocusColor
        }}
        animate={{
          opacity: [0.08, 0.12, 0.08],
          scale: [1, 1.1, 1]
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      <motion.div
        className="absolute inset-0"
        style={{
          backgroundColor: prefersReducedMotion ? 'transparent' : sectionColor
        }}
      />

      <motion.div
        className="absolute inset-0 mix-blend-soft-light"
        style={{
          opacity: noiseAlpha,
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`
        }}
        animate={{
          backgroundPosition: ['0% 0%', '100% 100%']
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "linear"
        }}
      />

      {enableVignette && (
        <motion.div
          className="absolute inset-0 pointer-events-none"
          style={{
            background: `radial-gradient(ellipse at center, rgba(0,0,0,0) 55%, rgba(0,0,0,${vignetteAlpha}) 100%)`
          }}
        />
      )}
    </motion.div>
  )
}
