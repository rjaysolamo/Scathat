// Reusable Framer Motion variants for scroll-triggered animations
// Easing consistent with Motion's signature style
export const easeCubic = [0.25, 0.1, 0.25, 1] as const

// Fade in + slide up for section headers
export const fadeInUp = {
  hidden: { opacity: 0, y: 40 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.8, ease: easeCubic },
  },
} as const

// Container that staggers its children
export const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.2 },
  },
} as const

// Generic item fade + slide up
export const staggerItem = {
  hidden: { opacity: 0, y: 30 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: easeCubic },
  },
} as const

// Slight scale-in with lift for emphasis (e.g., problem cards)
export const scaleIn = {
  hidden: { opacity: 0, y: 30, scale: 0.95 },
  visible: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: { duration: 0.6, ease: easeCubic },
  },
} as const

// Slide from left
export const slideLeft = {
  hidden: { opacity: 0, x: 30 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.7, ease: easeCubic },
  },
} as const

// Slide from right
export const slideRight = {
  hidden: { opacity: 0, x: -30 },
  visible: {
    opacity: 1,
    x: 0,
    transition: { duration: 0.7, ease: easeCubic },
  },
} as const

