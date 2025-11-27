// Local ambient type declarations for framer-motion
// Purpose: Provide fallback typings to satisfy TypeScript in this workspace
// without changing component logic. If upstream types resolve later, this file
// can be removed.

declare module "framer-motion" {
  import * as React from "react"

  // Core motion components
  export const motion: any
  export const m: any

  // LazyMotion provider and features
  export const LazyMotion: React.ComponentType<{ features: any; children?: React.ReactNode }>
  export const domAnimation: any

  // Hooks
  export function useReducedMotion(): boolean
  export function useScroll(options?: any): { scrollY: any; scrollYProgress: any }
  export function useTransform(value: any, input: any, output: any): any
  export function useMotionValue<T = number>(initial: T): any
}
