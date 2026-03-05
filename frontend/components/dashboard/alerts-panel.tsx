"use client"

import { AlertTriangle, AlertCircle, Info } from "lucide-react"
import { useAlerts } from "@/lib/hooks"
import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"

const alertConfig = {
  warning: {
    icon: AlertTriangle,
    className: "border-warning/20 bg-warning/5",
    iconClass: "text-warning",
  },
  error: {
    icon: AlertCircle,
    className: "border-destructive/20 bg-destructive/5",
    iconClass: "text-destructive",
  },
  info: {
    icon: Info,
    className: "border-primary/20 bg-primary/5",
    iconClass: "text-primary",
  },
}

function formatTimeAgo(timestamp: string) {
  const diff = Date.now() - new Date(timestamp).getTime()
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const minutes = Math.floor(diff / (1000 * 60))
  if (hours > 0) return `${hours}h ago`
  return `${minutes}m ago`
}

export function AlertsPanel() {
  const { data, isLoading } = useAlerts()

  if (isLoading || !data) {
    return (
      <div className="rounded-xl border border-border bg-card p-5">
        <Skeleton className="mb-4 h-5 w-24" />
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="mb-2 h-16 w-full rounded-lg" />
        ))}
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-card-foreground">Alerts</h3>
        <span className="text-xs text-muted-foreground">{data.length} active</span>
      </div>
      <div className="space-y-2">
        {data.map((alert) => {
          const config = alertConfig[alert.type]
          const Icon = config.icon
          return (
            <div
              key={alert.id}
              className={cn(
                "flex items-start gap-3 rounded-lg border p-3 transition-colors",
                config.className
              )}
            >
              <Icon className={cn("mt-0.5 h-4 w-4 shrink-0", config.iconClass)} />
              <div className="min-w-0 flex-1">
                <p className="text-xs font-medium text-card-foreground">{alert.message}</p>
                <div className="mt-1 flex items-center gap-2 text-[10px] text-muted-foreground">
                  <span>{alert.productName}</span>
                  <span>{"·"}</span>
                  <span>{formatTimeAgo(alert.timestamp)}</span>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
