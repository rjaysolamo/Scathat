"use client"

/**
 * Pricing Page - Subscription Tiers
 * Display Scathat pricing plans: Free, Pro, and Enterprise
 */

import { Header } from "@/web/components/marketing/header"
import { PricingPlans } from "@/web/components/pricing/pricing-plans"
import { PricingComparison } from "@/web/components/pricing/pricing-comparison"
import { PricingFAQ } from "@/web/components/pricing/pricing-faq"
import { Footer } from "@/web/components/marketing/footer"

export default function PricingPage() {
  return (
    <main className="min-h-screen bg-(--background) text-(--foreground)">
      <Header />
      <PricingPlans />
      <PricingComparison />
      <PricingFAQ />
      <Footer />
    </main>
  )
}
