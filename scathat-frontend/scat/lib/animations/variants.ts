import type { Variants } from "framer-motion"

const easeBrand: [number, number, number, number] = [0.25, 0.4, 0.25, 1]

export const fadeInUp: Variants = {
  hidden: { 
    opacity: 0, 
    y: 40,
    transition: {
      duration: 0.6,
      ease: easeBrand
    }
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.8,
      ease: easeBrand
    }
  }
};

export const fadeIn: Variants = {
  hidden: { 
    opacity: 0,
    transition: {
      duration: 0.6,
      ease: easeBrand
    }
  },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.8,
      ease: easeBrand
    }
  }
};

export const scaleIn: Variants = {
  hidden: { 
    opacity: 0,
    scale: 0.95,
    transition: {
      duration: 0.6,
      ease: easeBrand
    }
  },
  visible: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.7,
      ease: easeBrand
    }
  }
};

export const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2
    }
  }
};

export const heroStagger: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.15,
      delayChildren: 0.1
    }
  }
};

export const gridStagger: Variants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1,
      staggerDirection: 1
    }
  }
};

export const slideInLeft: Variants = {
  hidden: { 
    opacity: 0,
    x: -40,
    transition: {
      duration: 0.7,
      ease: easeBrand
    }
  },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.8,
      ease: easeBrand
    }
  }
};

export const slideInRight: Variants = {
  hidden: { 
    opacity: 0,
    x: 40,
    transition: {
      duration: 0.7,
      ease: easeBrand
    }
  },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.8,
      ease: easeBrand
    }
  }
};

export const rotateIn: Variants = {
  hidden: { 
    opacity: 0,
    rotate: -180,
    transition: {
      duration: 0.6,
      ease: easeBrand
    }
  },
  visible: {
    opacity: 1,
    rotate: 0,
    transition: {
      duration: 0.8,
      ease: easeBrand
    }
  }
};

// Viewport configuration for scroll-triggered animations
export const viewportConfig = {
  once: true,
  amount: 0.2,
  margin: "-50px"
};

// How It Works specific variants
export const howItWorksCard: Variants = {
  hidden: { 
    opacity: 0,
    scale: 0.9,
    rotate: -15,
    transition: {
      duration: 0.6,
      ease: easeBrand
    }
  },
  visible: {
    opacity: 1,
    scale: 1,
    rotate: 0,
    transition: {
      duration: 0.8,
      ease: easeBrand
    }
  }
};

// Reduced motion variants for accessibility
export const reducedMotionVariants: Variants = {
  hidden: { opacity: 0 },
  visible: { 
    opacity: 1,
    transition: { duration: 0.3 }
  }
};

export const heroItem: Variants = {
  hidden: {
    opacity: 0,
    y: 20,
    transition: { duration: 0.7, ease: easeBrand }
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.7, ease: easeBrand }
  }
};

export const sectionTitle: Variants = {
  hidden: {
    opacity: 0,
    y: 30,
    transition: { duration: 0.6, ease: easeBrand }
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: easeBrand }
  }
};

export const sectionDesc: Variants = {
  hidden: {
    opacity: 0,
    y: 30,
    transition: { duration: 0.6, ease: easeBrand }
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: easeBrand }
  }
};

export const problemCardItem: Variants = {
  hidden: {
    opacity: 0,
    y: 25,
    transition: { duration: 0.5, ease: easeBrand }
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: easeBrand }
  }
};

export const howGridItem: Variants = {
  hidden: {
    opacity: 0,
    y: 20,
    transition: { duration: 0.5, ease: easeBrand }
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: easeBrand }
  }
};
