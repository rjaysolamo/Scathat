"use client"

import { Header } from "@/web/components/marketing/header"
import { HeroScanner } from "@/web/components/marketing/hero-scanner"
import { StatsDashboard } from "@/web/components/marketing/stats-dashboard"
import { SupportedNetworks } from "@/web/components/marketing/supported-networks"
import { Features } from "@/web/components/marketing/features"
import { SecuritySection } from "@/web/components/marketing/security-section"
import { Footer } from "@/web/components/marketing/footer"

export default function Home() {
  return (
    <main className="min-h-screen bg-(--background) text-(--foreground)">
      <Header />
      <HeroScanner />
      <StatsDashboard />
      <SupportedNetworks />
      <SecuritySection />
      <Features />
      <Footer />
    </main>
  )
}
