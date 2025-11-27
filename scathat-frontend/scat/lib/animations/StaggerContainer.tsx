"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";
import { staggerContainer, viewportConfig, reducedMotionVariants } from "./variants";

interface StaggerContainerProps {
  children: ReactNode;
  className?: string;
  stagger?: number;
  delay?: number;
  id?: string;
}

export function StaggerContainer({ 
  children, 
  className = "", 
  stagger = 0.1,
  delay = 0.2,
  id 
}: StaggerContainerProps) {
  const customStagger = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: stagger,
        delayChildren: delay
      }
    }
  } as const;

  return (
    <motion.div
      id={id}
      className={className}
      initial="hidden"
      whileInView="visible"
      viewport={viewportConfig}
      variants={customStagger}
    >
      {children}
    </motion.div>
  );
}