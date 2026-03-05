"use client"

import { KPICards } from "@/components/dashboard/kpi-cards"
import { RevenueChart } from "@/components/dashboard/revenue-chart"
import { RecentDecisions } from "@/components/dashboard/recent-decisions"
import { AlertsPanel } from "@/components/dashboard/alerts-panel"
import { ConnectionBanner } from "@/components/connection-banner"

export default function DashboardPage() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-6 lg:px-8">
      <ConnectionBanner />
      <div className="mb-6 mt-4">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">Dashboard</h1>
        <p className="text-sm text-muted-foreground">Real-time pricing intelligence overview</p>
      </div>

      <div className="flex flex-col gap-6">
        <KPICards />

        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <RevenueChart />
          </div>
          <div>
            <AlertsPanel />
          </div>
        </div>

        <RecentDecisions />
      </div>
    </div>
  )
}
