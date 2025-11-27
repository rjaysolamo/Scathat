// Server Component for route configs; inner content uses client components
export const dynamic = "force-dynamic"
export const revalidate = 0
import { Header } from "@/components/header"
import { Hero } from "@/components/hero"
import { Problem } from "@/components/problem"
import { SupportedChains } from "@/components/supported-chains"
import { Solution } from "@/components/solution"
import { HowItWorks } from "@/components/how-it-works"
import { Download } from "@/components/download"
import { Dashboard } from "@/components/dashboard"
import { Footer } from "@/components/footer"
import { AnimatedBackground } from "@/components/AnimatedBackground"
import { Analytics } from "@vercel/analytics/next"

export default function Home() {
  return (
    <>
      <AnimatedBackground />
      <main className="w-full overflow-hidden bg-background">
        <Header />
        <Hero />
        <SupportedChains />
        <Problem />
        <Solution />
        <HowItWorks />
        <Download />
        <Dashboard />
        <Footer />
        <Analytics />
      </main>
    </>
  )
}
