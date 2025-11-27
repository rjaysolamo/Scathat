"use client"
import { m } from "framer-motion"
import { fadeInUp, staggerContainer, slideLeft, slideRight } from "@/lib/animations"
import { Button } from "@/components/ui/button"

export function Download() {
  return (
    <section id="download" className="w-full px-4 py-20 sm:py-32 lg:py-40">
      <div className="mx-auto max-w-4xl space-y-12">
        <div className="text-center space-y-4">
          <m.h2 initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.2 }} variants={fadeInUp} className="text-3xl font-bold sm:text-4xl lg:text-5xl text-foreground">Download the Extension</m.h2>
          <m.p initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.2 }} variants={fadeInUp} className="text-lg text-muted-foreground">Get real-time protection as you browse Web3</m.p>
        </div>

        <m.div initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.2 }} variants={staggerContainer} className="grid gap-6 md:grid-cols-2">
          <m.div variants={slideLeft} className="rounded-lg border border-border bg-card p-8 space-y-6" style={{ boxShadow: "0 0 20px rgba(0, 242, 139, 0.15)" }}>
            <div className="h-32 rounded bg-muted flex items-center justify-center">
              <div className="text-muted-foreground text-center">
                <div className="text-3xl mb-2">Chrome</div>
                <p className="text-sm">Available on Chrome Web Store</p>
              </div>
            </div>
            <div className="space-y-2">
              <h3 className="font-bold text-foreground">Chrome Extension</h3>
              <p className="text-sm text-muted-foreground">
                Works seamlessly with your browser. Real-time warnings before you approve any transaction.
              </p>
            </div>
            <Button className="w-full">Download for Chrome</Button>
          </m.div>

          <m.div variants={slideRight} className="rounded-lg border border-border bg-card p-8 space-y-6">
            <div className="h-32 rounded bg-muted flex items-center justify-center">
              <div className="text-muted-foreground text-center">
                <div className="text-3xl mb-2">Web App</div>
                <p className="text-sm">Analyze any smart contract</p>
              </div>
            </div>
            <div className="space-y-2">
              <h3 className="font-bold text-foreground">Web App</h3>
              <p className="text-sm text-muted-foreground">
                Paste any contract address and get instant security analysis. No installation needed.
              </p>
            </div>
            <Button className="w-full bg-transparent" variant="outline">
              Launch Web App
            </Button>
          </m.div>
        </m.div>

        <div className="rounded-lg border border-border/50 bg-background p-6 space-y-3">
          <h4 className="font-bold text-foreground flex items-center gap-2">
            <svg className="w-5 h-5 text-primary" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            100% Free & Open Source
          </h4>
          <p className="text-sm text-muted-foreground">
            Built for the Base ecosystem. No fees, no premium tiers. Just security that works.
          </p>
        </div>
      </div>
    </section>
  )
}
