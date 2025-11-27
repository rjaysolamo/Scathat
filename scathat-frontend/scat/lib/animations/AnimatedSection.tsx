"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";
import { fadeInUp, viewportConfig, reducedMotionVariants } from "./variants";

interface AnimatedSectionProps {
  children: ReactNode;
  className?: string;
  variants?: any;
  delay?: number;
  id?: string;
}

export function AnimatedSection({ 
  children, 
  className = "", 
  variants = fadeInUp,
  delay = 0,
  id 
}: AnimatedSectionProps) {
  return (
    <motion.section
      id={id}
      className={className}
      initial="hidden"
      whileInView="visible"
      viewport={viewportConfig}
      transition={{ 
        delay,
        ease: [0.25, 0.1, 0.25, 1]
      }}
      variants={variants}
    >
      {children}
    </motion.section>
  );
}
