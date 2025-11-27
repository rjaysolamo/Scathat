"use client"
import { useRef } from "react"
import { motion, useReducedMotion, useScroll, useTransform } from "framer-motion"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { fadeInUp, staggerContainer, staggerItem } from "@/lib/animations"

export function Hero() {
  const reduceMotion = useReducedMotion()
  const ref = useRef<HTMLDivElement | null>(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start end", "end start"] })
  const bgY = useTransform(scrollYProgress, [0, 1], [-20, 0])
  const accentY = useTransform(scrollYProgress, [0, 1], [-12, 12])
  return (
    <motion.section
      ref={ref}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, amount: 0.25 }}
      variants={staggerContainer}
      className="relative w-full px-4 py-20 sm:py-32 lg:py-40"
    >
      {/* Subtle parallax background */}
      <motion.div
        aria-hidden
        style={{ y: reduceMotion ? 0 : bgY, willChange: reduceMotion ? undefined : "transform" }}
        className="pointer-events-none absolute inset-0 -z-10"
      >
        <div className="absolute top-16 left-12 w-56 h-56 bg-accent/10 rounded-full blur-3xl" />
        <div className="absolute bottom-24 right-10 w-72 h-72 bg-primary/10 rounded-full blur-3xl" />
      </motion.div>
      <div className="mx-auto max-w-4xl space-y-8 text-center">
        <div className="space-y-4">
          <motion.h1
            variants={fadeInUp}
            transition={{ duration: 0.8, ease: [0.25, 0.1, 0.25, 1], delay: 0 }}
            className="text-balance text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl text-foreground"
          >
            Who will protect you...
            <motion.span
              variants={fadeInUp}
              transition={{ duration: 0.8, ease: [0.25, 0.1, 0.25, 1], delay: 0.15 }}
              style={{ y: reduceMotion ? 0 : accentY, willChange: reduceMotion ? undefined : "transform" }}
              className="block text-accent"
            >
              when no one sees?
            </motion.span>
          </motion.h1>
          <motion.p
            variants={fadeInUp}
            transition={{ duration: 0.8, ease: [0.25, 0.1, 0.25, 1], delay: 0.3 }}
            className="text-balance text-lg text-muted-foreground sm:text-xl"
          >
            Millions lost yearly to hacks, rugpulls, and malicious approvals. Scathat protects you with AI-powered
            real-time smart contract analysis.
          </motion.p>
        </div>

        <motion.div
          variants={fadeInUp}
          transition={{ duration: 0.8, ease: [0.25, 0.1, 0.25, 1], delay: 0.45 }}
          className="flex flex-col gap-4 sm:flex-row justify-center sm:gap-4"
          style={{ willChange: reduceMotion ? undefined : "transform, opacity" }}
        >
          <Link href="#download">
            <Button size="lg" className="px-8 transition-transform" style={{ transform: reduceMotion ? "none" : "scale(1)" }}>
              Download Extension
            </Button>
          </Link>
          <Button size="lg" variant="outline" className="px-8 bg-transparent transition-transform" style={{ transform: reduceMotion ? "none" : "scale(1)" }}>
            View Demo
          </Button>
        </motion.div>

        <motion.div
          variants={staggerContainer}
          transition={{ delayChildren: 0.6, staggerChildren: 0.05 }}
          className="pt-8 grid grid-cols-3 gap-4 sm:gap-8"
        >
          {["Instant", "AI-Powered", "Free"].map((label, idx) => (
            <motion.div key={label} variants={staggerItem} className="space-y-1">
              <div className="text-2xl font-bold text-accent sm:text-3xl">{label}</div>
              <div className="text-xs text-muted-foreground sm:text-sm">
                {idx === 0 ? "Real-time analysis" : idx === 1 ? "Venice.ai technology" : "Always protected"}
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </motion.section>
  ) 
}
