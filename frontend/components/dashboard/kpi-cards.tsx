"use client"

import { Package, TrendingUp, DollarSign, Brain } from "lucide-react"
import { useKPIs } from "@/lib/hooks"
import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"

const kpiConfig = [
  {
    key: "activeProducts" as const,
    label: "Active Products",
    icon: Package,
    format: (v: number) => (v || 0).toLocaleString("en-IN"),
    deltaKey: "activeProductsDelta" as const,
    deltaFormat: (v: number) => `+${v || 0}`,
    deltaSuffix: " this week",
  },
  {
    key: "avgMargin" as const,
    label: "Avg Margin %",
    icon: TrendingUp,
    format: (v: number) => `${(v || 0).toFixed(1)}%`,
    deltaKey: "avgMarginDelta" as const,
    deltaFormat: (v: number) => `+${(v || 0).toFixed(1)}%`,
    deltaSuffix: " vs last week",
  },
  {
    key: "revenueToday" as const,
    label: "Revenue Today",
    icon: DollarSign,
    format: (v: number) => `₹${((v || 0) / 1000).toFixed(1)}K`,
    deltaKey: "revenueDelta" as const,
    deltaFormat: (v: number) => `+${(v || 0).toFixed(1)}%`,
    deltaSuffix: " vs yesterday",
  },
  // {
  //   key: "aiConfidence" as const,
  //   label: "AI Confidence",
  //   icon: Brain,
  //   format: (v: number) => `${(v || 0).toFixed(1)}%`,
  //   deltaKey: "confidenceDelta" as const,
  //   deltaFormat: (v: number) => `+${(v || 0).toFixed(1)}%`,
  //   deltaSuffix: " improvement",
  // },
]

export function KPICards() {
  const { data, isLoading } = useKPIs()

  const toNumberOrNull = (value: unknown): number | null => {
    if (typeof value !== "number" || Number.isNaN(value) || !Number.isFinite(value)) {
      return null
    }
    return value
  }

  if (isLoading || !data) {
    return (
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="rounded-xl border border-border bg-card p-5">
            <Skeleton className="mb-3 h-4 w-24" />
            <Skeleton className="mb-2 h-8 w-20" />
            <Skeleton className="h-3 w-32" />
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {kpiConfig.map((kpi) => {
        const value = toNumberOrNull(data[kpi.key])
        const delta = toNumberOrNull(data[kpi.deltaKey])
        return (
          <div
            key={kpi.key}
            className="group relative overflow-hidden rounded-xl border border-border bg-card p-5 transition-all duration-300 hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
            <div className="relative">
              <div className="mb-3 flex items-center justify-between">
                <span className="text-sm font-medium text-muted-foreground">{kpi.label}</span>
                <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10">
                  <kpi.icon className="h-4 w-4 text-primary" />
                </div>
              </div>
              <div className="mb-1 text-2xl font-bold tracking-tight text-card-foreground">
                {value === null ? "N/A" : kpi.format(value)}
              </div>
              {delta === null ? (
                <div className="text-xs text-muted-foreground">No baseline yet</div>
              ) : (
                <div className={cn("flex items-center gap-1 text-xs", delta >= 0 ? "text-success" : "text-destructive")}>
                  <span>{kpi.deltaFormat(delta)}</span>
                  <span className="text-muted-foreground">{kpi.deltaSuffix}</span>
                </div>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}