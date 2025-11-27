"use client"

import { DashboardLayout } from "@/web/components/dashboard/layout"
import { ScannerPanel } from "@/web/components/dashboard/scanner-panel"
import { ResultsDisplay } from "@/web/components/dashboard/results-display"
import { StatsOverview } from "@/web/components/dashboard/stats-overview"

export default function Dashboard() {
  return (
    <DashboardLayout>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <StatsOverview />

        <div className="lg:col-span-2">
          <ScannerPanel />
        </div>

        <div className="lg:col-span-3">
          <ResultsDisplay />
        </div>
      </div>
    </DashboardLayout>
  )
}
