"use client"
import { motion } from "framer-motion"
import { staggerContainer, viewportConfig, sectionTitle, sectionDesc, howGridItem } from "@/lib/animations/variants"

export function HowItWorks() {
  const steps = [
    {
      number: "1",
      title: "Submit Contract",
      description: "User submits contract address via web app or extension",
    },
    {
      number: "2",
      title: "Fetch Data",
      description: "Backend fetches bytecode and source from Basescan",
    },
    {
      number: "3",
      title: "AI Analysis",
      description: "Python AI engine sends contract to for risk scoring",
    },
    {
      number: "4",
      title: "On-Chain",
      description: "Backend writes risk score to Base via smart contract",
    },
    {
      number: "5",
      title: "Results",
      description: "Dashboard shows Safe/Warning/Dangerous results",
    },
    {
      number: "6",
      title: "Protection",
      description: "AgentKit auto-pauses or blocks risky interactions",
    },
  ]

  return (
    <motion.section 
      id="how" 
      className="w-full px-4 py-20 sm:py-32 lg:py-40 border-t border-border bg-card/50"
      initial="hidden"
      whileInView="visible"
      viewport={viewportConfig}
      variants={staggerContainer}
    >
      <div className="mx-auto max-w-4xl space-y-12">
        <motion.div className="text-center space-y-4" variants={staggerContainer}>
          <motion.h2 className="text-3xl font-bold sm:text-4xl lg:text-5xl text-foreground" variants={sectionTitle}>How It Works</motion.h2>
          <motion.p className="text-lg text-muted-foreground" variants={sectionDesc}>The complete flow from contract submission to protection</motion.p>
        </motion.div>

        <motion.div 
          className="grid gap-4 md:grid-cols-2 lg:grid-cols-3" 
          variants={staggerContainer}
          viewport={viewportConfig}
        >
          {steps.map((step, index) => (
            <motion.div
              key={index}
              className="rounded-lg border border-border bg-background p-6 space-y-3 hover:border-accent/50 transition-colors group"
              variants={howGridItem}
              transition={{ delay: index * 0.1 }}
              whileHover={{ 
                scale: 1.03, 
                rotate: 2,
                transition: { duration: 0.2 }
              }}
            >
              <motion.div 
                className="flex h-10 w-10 items-center justify-center rounded-full bg-primary text-primary-foreground font-bold text-sm"
                initial={{ rotate: -180, opacity: 0 }}
                animate={{ rotate: 0, opacity: 1 }}
                transition={{ 
                  delay: index * 0.1 + 0.2,
                  duration: 0.6,
                  ease: [0.25, 0.1, 0.25, 1]
                }}
              >
                {step.number}
              </motion.div>
              <h3 className="font-bold text-foreground">{step.title}</h3>
              <p className="text-sm text-muted-foreground">{step.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </motion.section>
  )
}
