"use client"
import { LazyMotion, domAnimation, m } from "framer-motion"
import { fadeInUp, staggerContainer, staggerItem, scaleIn } from "@/lib/animations"

export function Problem() {
  const problems = [
    "Users cannot read or understand smart contracts",
    "Builders move fast and skip security",
    "Wallets warn users too late",
    "Auditing tools are slow, expensive, and reactive",
    "People only realize they were hacked after pressing confirm",
  ]

  return (
    <section id="problem" className="w-full px-4 py-20 sm:py-32 lg:py-40 border-t border-border bg-card/50">
      <div className="mx-auto max-w-4xl space-y-12">
        <div className="text-center space-y-4">
          <m.h2
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            variants={fadeInUp}
            className="text-3xl font-bold sm:text-4xl lg:text-5xl text-foreground"
          >
            The Problem
          </m.h2>
          <m.p
            initial="hidden"
            whileInView="visible"
            viewport={{ once: true, amount: 0.2 }}
            variants={fadeInUp}
            className="text-lg text-muted-foreground"
          >
            Millions lost yearly to hacks, rugpulls, and malicious approvals
          </m.p>
        </div>

        <m.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, amount: 0.2 }}
          variants={staggerContainer}
          className="grid gap-4 md:grid-cols-2"
        >
          {problems.map((problem, index) => (
            <m.div
              key={index}
              variants={scaleIn}
              className="flex gap-4 rounded-lg border border-border/50 bg-background p-6 hover:border-border transition-colors"
            >
              <div className="flex-shrink-0">
                <div className="flex h-8 w-8 items-center justify-center rounded bg-destructive text-destructive-foreground font-bold">
                  {index + 1}
                </div>
              </div>
              <p className="text-muted-foreground">{problem}</p>
            </m.div>
          ))}
        </m.div>
      </div>
    </section>
  )
}
