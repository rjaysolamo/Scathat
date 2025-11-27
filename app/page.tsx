"use client"

import { Header } from "@/components/header"
import { Hero } from "@/components/hero"
import { Problem } from "@/components/problem"
import { Solution } from "@/components/solution"
import { HowItWorks } from "@/components/how-it-works"
import { Download } from "@/components/download"
import { Dashboard } from "@/components/dashboard"
import { Footer } from "@/components/footer"
import { LazyMotion, domAnimation } from "framer-motion"
import AnimatedBackground from "@/components/animated-background"

export default function Home() {
  return (
    <LazyMotion features={domAnimation}>
      <main className="relative w-full overflow-hidden bg-background">
        <AnimatedBackground />
        <div className="relative z-10">
          <Header />
          <Hero />
          <Problem />
          <Solution />
          <HowItWorks />
          <Download />
          <Dashboard />
          <Footer />
        </div>
      </main>
    </LazyMotion>
  )
}
