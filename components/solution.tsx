"use client"
import { m } from "framer-motion"
import { fadeInUp, staggerContainer, staggerItem } from "@/lib/animations"
export function Solution() {
  return (
    <section id="solution" className="w-full px-4 py-20 sm:py-32 lg:py-40">
      <div className="mx-auto max-w-4xl space-y-12">
        <div className="text-center space-y-4">
          <m.h2 initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.2 }} variants={fadeInUp} className="text-3xl font-bold sm:text-4xl lg:text-5xl text-foreground">The Solution</m.h2>
          <m.p initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.2 }} variants={fadeInUp} className="text-lg text-muted-foreground">
            AI that analyzes smart contracts in real time and protects you before you sign
          </m.p>
        </div>

        <div className="space-y-6">
          <div className="rounded-lg border border-border bg-card/50 p-8 space-y-4">
            <m.h3 initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.2 }} variants={fadeInUp} className="text-xl font-bold text-accent">What Scathat does:</m.h3>
            <m.ul initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.2 }} variants={staggerContainer} className="space-y-3">
              <m.li variants={staggerItem} className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-primary flex-shrink-0"></span>
                <span className="text-foreground">Scans contracts instantly</span>
              </m.li>
              <m.li variants={staggerItem} className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-primary flex-shrink-0"></span>
                <span className="text-foreground">Detects risky patterns, rugpull logic, and hidden exploits</span>
              </m.li>
              <m.li variants={staggerItem} className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-primary flex-shrink-0"></span>
                <span className="text-foreground">Shows a simple Safe/Warning/Dangerous risk score</span>
              </m.li>
              <m.li variants={staggerItem} className="flex items-start gap-3">
                <span className="mt-1 h-2 w-2 rounded-full bg-primary flex-shrink-0"></span>
                <span className="text-foreground">Uses AgentKit to block unsafe transactions and limit approvals</span>
              </m.li>
            </m.ul>
          </div>

          <m.div initial="hidden" whileInView="visible" viewport={{ once: true, amount: 0.2 }} variants={staggerContainer} className="grid gap-4 md:grid-cols-3">
            <m.div variants={staggerItem} className="rounded-lg border border-border bg-card p-6 text-center space-y-2">
              <div className="text-sm text-muted-foreground">Target Users</div>
              <div className="font-bold text-foreground">Everyday Users</div>
              <p className="text-sm text-muted-foreground">Protection from scams and phishing</p>
            </m.div>
            <m.div variants={staggerItem} className="rounded-lg border border-border bg-card p-6 text-center space-y-2">
              <div className="text-sm text-muted-foreground">Target Users</div>
              <div className="font-bold text-foreground">Developers</div>
              <p className="text-sm text-muted-foreground">Fast AI security checks</p>
            </m.div>
            <m.div variants={staggerItem} className="rounded-lg border border-border bg-card p-6 text-center space-y-2">
              <div className="text-sm text-muted-foreground">Target Users</div>
              <div className="font-bold text-foreground">Wallets & dApps</div>
              <p className="text-sm text-muted-foreground">Plug-and-play safety layer</p>
            </m.div>
          </m.div>
        </div>
      </div>
    </section>
  )
}
