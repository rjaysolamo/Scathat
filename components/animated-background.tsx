"use client"

import { useEffect } from "react"
import { motion, useTransform, useMotionValue, useReducedMotion } from "framer-motion"


export function AnimatedBackground() {
  const prefersReducedMotion = useReducedMotion()
  const scrollYMV = useMotionValue(0)

  const topY = useTransform(scrollYMV, [0, 1000], [0, -100])
  const heroX = useTransform(scrollYMV, [0, 1000], [0, 50])
  const heroY = useTransform(scrollYMV, [0, 1000], [0, -80])
  const middleY = useTransform(scrollYMV, [0, 2000], [0, 120])
  const bottomX = useTransform(scrollYMV, [1000, 3000], [0, -60])
  const heroGlowOpacity = useTransform(scrollYMV, [0, 600, 1200], [0.04, 0.08, 0.05])

  const sectionColor = useTransform(scrollYMV, [0, 800, 1600, 2400], [
    "rgba(0, 242, 139, 0.03)",
    "rgba(220, 38, 38, 0.02)",
    "rgba(0, 242, 139, 0.06)",
    "rgba(0, 217, 126, 0.04)",
  ])

  const mouseX = useMotionValue(0)
  const mouseY = useMotionValue(0)
  const gradientX = useTransform(mouseX, [0, typeof window !== "undefined" ? window.innerWidth : 1], [-20, 20])
  const gradientY = useTransform(mouseY, [0, typeof window !== "undefined" ? window.innerHeight : 1], [-20, 20])
  const heroCombinedX = useTransform([heroX, gradientX], ([a, b]) => a + b)
  const heroCombinedY = useTransform([heroY, gradientY], ([a, b]) => a + b)

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      mouseX.set(e.clientX)
      mouseY.set(e.clientY)
    }
    const onScroll = () => {
      scrollYMV.set(window.scrollY)
    }
    window.addEventListener("mousemove", onMove)
    window.addEventListener("scroll", onScroll, { passive: true })
    return () => window.removeEventListener("mousemove", onMove)
  }, [mouseX, mouseY, scrollYMV])

  const noise =
    "url('data:image/svg+xml;utf8,<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"800\" height=\"800\"><filter id=\"n\"><feTurbulence type=\"fractalNoise\" baseFrequency=\"0.9\" numOctaves=\"2\" stitchTiles=\"stitch\"/></filter><rect width=\"100%\" height=\"100%\" filter=\"url(%23n)\"/></svg>')"

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden">
      <motion.div
        className="absolute left-1/2 -translate-x-1/2 top-0 w-[1200px] h-[800px] rounded-full transform-gpu mix-blend-screen"
        style={{
          y: prefersReducedMotion ? 0 : topY,
          background: "radial-gradient(circle, rgba(0,242,139,0.12), rgba(0,242,139,0))",
          filter: "blur(100px)",
          willChange: "transform",
        }}
        animate={prefersReducedMotion ? undefined : { opacity: [0.03, 0.05, 0.03], scale: [1, 1.05, 1] }}
        transition={prefersReducedMotion ? undefined : { duration: 8, repeat: Infinity, ease: [0.25, 0.1, 0.25, 1], delay: 0 }}
      />

      <motion.div
        className="absolute right-[20%] top-[10%] w-[600px] h-[600px] rounded-full transform-gpu mix-blend-screen"
        style={{
          x: prefersReducedMotion ? 0 : heroCombinedX,
          y: prefersReducedMotion ? 0 : heroCombinedY,
          background: "radial-gradient(circle, rgba(0,242,139,0.16), rgba(0,242,139,0))",
          filter: "blur(120px)",
          willChange: "transform",
        }}
        animate={prefersReducedMotion ? undefined : { opacity: [0.03, 0.05, 0.03], scale: [1, 1.05, 1] }}
        transition={prefersReducedMotion ? undefined : { duration: 8, repeat: Infinity, ease: [0.25, 0.1, 0.25, 1], delay: 2 }}
      />

      <motion.div
        className="absolute left-[15%] top-1/2 -translate-y-1/2 w-[500px] h-[500px] rounded-full transform-gpu mix-blend-screen"
        style={{
          y: prefersReducedMotion ? 0 : middleY,
          background: "radial-gradient(circle, rgba(0,217,126,0.10), rgba(0,217,126,0))",
          filter: "blur(110px)",
          willChange: "transform",
        }}
        animate={prefersReducedMotion ? undefined : { opacity: [0.02, 0.04, 0.02], scale: [1, 1.04, 1] }}
        transition={prefersReducedMotion ? undefined : { duration: 9, repeat: Infinity, ease: [0.25, 0.1, 0.25, 1], delay: 4 }}
      />

      <motion.div
        className="absolute right-[20%] bottom-0 w-[700px] h-[700px] rounded-full transform-gpu mix-blend-screen"
        style={{
          x: prefersReducedMotion ? 0 : bottomX,
          background: "radial-gradient(circle, rgba(0,242,139,0.12), rgba(0,242,139,0))",
          filter: "blur(130px)",
          willChange: "transform",
        }}
        animate={prefersReducedMotion ? undefined : { opacity: [0.02, 0.045, 0.02], scale: [1, 1.06, 1] }}
        transition={prefersReducedMotion ? undefined : { duration: 10, repeat: Infinity, ease: [0.25, 0.1, 0.25, 1], delay: 6 }}
      />

      <motion.div
        className="absolute left-1/2 top-[20%] -translate-x-1/2 w-[800px] h-[400px] rounded-full transform-gpu mix-blend-screen"
        style={{
          opacity: prefersReducedMotion ? 0.04 : heroGlowOpacity,
          background: "radial-gradient(circle, rgba(0,242,139,0.25), rgba(0,242,139,0))",
          filter: "blur(140px)",
        }}
        animate={prefersReducedMotion ? undefined : { scale: [1, 1.04, 1] }}
        transition={prefersReducedMotion ? undefined : { duration: 8, repeat: Infinity, ease: [0.25, 0.1, 0.25, 1], delay: 3 }}
      />

      <motion.div
        className="absolute inset-0"
        style={{ backgroundColor: sectionColor }}
      />

      <motion.div
        className="absolute inset-0 opacity-[0.015] mix-blend-overlay"
        style={{ backgroundImage: noise, backgroundSize: "200% 200%" }}
        animate={prefersReducedMotion ? undefined : { backgroundPosition: ["0% 0%", "100% 100%"] }}
        transition={prefersReducedMotion ? undefined : { duration: 20, repeat: Infinity, ease: "linear" }}
      />

      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(closest-side at 50% 40%, rgba(10,10,10,0) 55%, rgba(10,10,10,0.5) 100%)",
          pointerEvents: "none",
        }}
      />
    </div>
  )
}

export default AnimatedBackground
