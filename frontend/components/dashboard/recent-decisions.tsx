"use client"

import { useRecentDecisions } from "@/lib/hooks"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"

function formatTime(timestamp: string) {
  return new Date(timestamp).toLocaleTimeString("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
  })
}

const typeColors: Record<string, string> = {
  deterministic: "bg-chart-2/10 text-chart-2 border-chart-2/20",
  ai_correction: "bg-primary/10 text-primary border-primary/20",
  guardrail: "bg-warning/10 text-warning border-warning/20",
  monitoring: "bg-chart-4/10 text-chart-4 border-chart-4/20",
}

const typeLabels: Record<string, string> = {
  deterministic: "Rule",
  ai_correction: "AI",
  guardrail: "Guardrail",
  monitoring: "Monitor",
}

const statusStyles: Record<string, string> = {
  applied: "text-success",
  blocked: "text-destructive",
  pending: "text-warning",
}

export function RecentDecisions() {
  const { data, isLoading } = useRecentDecisions()

  if (isLoading || !data) {
    return (
      <div className="rounded-xl border border-border bg-card p-5">
        <Skeleton className="mb-4 h-5 w-48" />
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="mb-3 h-12 w-full rounded-lg" />
        ))}
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <h3 className="mb-4 text-sm font-semibold text-card-foreground">Recent Pricing Decisions</h3>
      <div className="space-y-2">
        {data.map((decision) => (
          <div
            key={decision.id}
            className="flex items-center gap-3 rounded-lg border border-border/50 bg-secondary/30 p-3 transition-colors hover:bg-secondary/50"
          >
            <div className="hidden min-w-0 flex-1 sm:flex sm:items-center sm:gap-3">
              <Badge
                variant="outline"
                className={cn("shrink-0 text-[10px] uppercase tracking-wider", typeColors[decision.type])}
              >
                {typeLabels[decision.type]}
              </Badge>
              <span className="min-w-0 flex-1 truncate text-sm text-card-foreground">
                {decision.productName}
              </span>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span className="line-through">₹{decision.oldPrice}</span>
                <span className="text-card-foreground">₹{decision.newPrice}</span>
              </div>
              <span className={cn("text-xs font-medium", statusStyles[decision.status])}>
                {decision.status}
              </span>
              <span className="text-xs text-muted-foreground">{formatTime(decision.timestamp)}</span>
            </div>
            <div className="flex w-full flex-col gap-1 sm:hidden">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-card-foreground">{decision.productName}</span>
                <Badge
                  variant="outline"
                  className={cn("text-[10px] uppercase tracking-wider", typeColors[decision.type])}
                >
                  {typeLabels[decision.type]}
                </Badge>
              </div>
              <div className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <span className="line-through">₹{decision.oldPrice}</span>
                  <span className="text-card-foreground">₹{decision.newPrice}</span>
                </div>
                <span className={cn("font-medium", statusStyles[decision.status])}>
                  {decision.status}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
