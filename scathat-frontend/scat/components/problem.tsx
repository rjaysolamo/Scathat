"use client"
import { motion } from "framer-motion"
import { fadeInUp, staggerContainer, scaleIn, viewportConfig, problemCardItem } from "@/lib/animations/variants"

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
      <motion.div 
        className="mx-auto max-w-4xl space-y-12"
        initial="hidden"
        whileInView="visible"
        viewport={viewportConfig}
        variants={staggerContainer}
      >
        <motion.div className="text-center space-y-4" variants={fadeInUp}>
          <h2 className="text-3xl font-bold sm:text-4xl lg:text-5xl text-foreground">The Problem</h2>
          <motion.p 
            className="text-lg text-muted-foreground"
            variants={fadeInUp}
            transition={{ delay: 0.1 }}
          >
            Millions lost yearly to hacks, rugpulls, and malicious approvals
          </motion.p>
        </motion.div>

        <motion.div 
          className="grid gap-4 md:grid-cols-2"
          variants={staggerContainer}
          viewport={{ ...viewportConfig, amount: 0.25 }}
        >
          {problems.map((problem, index) => (
            <motion.div
              key={index}
              className="flex gap-4 rounded-lg border border-border/50 bg-background p-6 hover:border-border transition-colors"
              variants={problemCardItem}
              transition={{ 
                delay: index * 0.1,
                ease: [0.25, 0.1, 0.25, 1]
              }}
              whileHover={{ 
                scale: 1.02,
                transition: { duration: 0.2 }
              }}
            >
              <div className="flex-shrink-0">
                <div className="flex h-8 w-8 items-center justify-center rounded bg-destructive text-destructive-foreground font-bold">
                  {index + 1}
                </div>
              </div>
              <p className="text-muted-foreground">{problem}</p>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>
    </section>
  )
}
