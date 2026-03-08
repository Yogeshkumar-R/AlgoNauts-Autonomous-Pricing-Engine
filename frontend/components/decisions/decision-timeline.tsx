"use client"

import { useState } from "react"
import {
  Calculator,
  ShieldCheck,
  Activity,
  Brain,
  ChevronDown,
  ChevronRight,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Info,
} from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { useDecisionLog } from "@/lib/hooks"
import { cn } from "@/lib/utils"

const typeConfig = {
  deterministic: {
    icon: Calculator,
    label: "Deterministic",
    color: "text-chart-2",
    bg: "bg-chart-2/10",
    border: "border-chart-2/20",
  },
  guardrail: {
    icon: ShieldCheck,
    label: "Guardrail",
    color: "text-warning",
    bg: "bg-warning/10",
    border: "border-warning/20",
  },
  monitoring: {
    icon: Activity,
    label: "Monitoring",
    color: "text-chart-4",
    bg: "bg-chart-4/10",
    border: "border-chart-4/20",
  },
  ai_correction: {
    icon: Brain,
    label: "AI Correction",
    color: "text-primary",
    bg: "bg-primary/10",
    border: "border-primary/20",
  },
}

const statusConfig = {
  success: { icon: CheckCircle2, color: "text-success", label: "Success" },
  blocked: { icon: XCircle, color: "text-destructive", label: "Blocked" },
  warning: { icon: AlertTriangle, color: "text-warning", label: "Warning" },
  info: { icon: Info, color: "text-primary", label: "Info" },
}

// Define payload types
interface PayloadData {
  input_data?: {
    current_price?: number
  }
  output_data?: {
    recommended_price?: number
  }
  oldPrice?: number
  newPrice?: number
  [key: string]: any
}

export function DecisionTimeline() {
  const { data: entries, isLoading } = useDecisionLog()
  const [expanded, setExpanded] = useState<Record<string, boolean>>({})

  if (isLoading || !entries) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-24 w-full rounded-xl" />
        ))}
      </div>
    )
  }

  function toggleExpand(id: string) {
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }))
  }

  return (
    <div className="relative">
      {/* Timeline line */}
      <div className="absolute left-[19px] top-0 h-full w-px bg-border" />

      <div className="space-y-4">
        {entries.map((entry) => {
          const type = typeConfig[entry.type] || typeConfig.deterministic
          const status = statusConfig[entry.status] || statusConfig.info
          const isExpanded = expanded[entry.id]
          const TypeIcon = type.icon
          const StatusIcon = status.icon
          
          // Type assertion for payload
          const payload = entry.payload as PayloadData
          const oldPrice = Number(payload?.input_data?.current_price ?? payload?.oldPrice ?? 0).toFixed(2)
          const newPrice = Number(payload?.output_data?.recommended_price ?? payload?.newPrice ?? 0).toFixed(2)

          return (
            <div key={entry.id} className="relative pl-12">
              {/* Timeline dot */}
              <div className={cn("absolute left-2 top-4 flex h-6 w-6 items-center justify-center rounded-full border", type.bg, type.border)}>
                <TypeIcon className={cn("h-3 w-3", type.color)} />
              </div>

              <div className="rounded-xl border border-border bg-card transition-all duration-200 hover:border-primary/20">
                <button
                  onClick={() => toggleExpand(entry.id)}
                  className="flex w-full items-start gap-3 p-4 text-left"
                >
                  <div className="min-w-0 flex-1">
                    <div className="mb-1 flex flex-wrap items-center gap-2">
                      <Badge variant="outline" className={cn("text-[10px] uppercase tracking-wider", type.bg, type.color, type.border)}>
                        {type.label}
                      </Badge>
                      <span className="text-sm font-medium text-card-foreground">{entry.productName}</span>
                      <div className={cn("flex items-center gap-1", status.color)}>
                        <StatusIcon className="h-3 w-3" />
                        <span className="text-[10px] font-medium uppercase">{status.label}</span>
                      </div>
                    </div>
                    <p className="text-xs leading-relaxed text-muted-foreground">{entry.description}</p>
                    <span className="mt-1 block text-[10px] text-muted-foreground">
                      {new Date(entry.timestamp).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" })}
                    </span>
                  </div>
                  {isExpanded ? (
                    <ChevronDown className="mt-1 h-4 w-4 shrink-0 text-muted-foreground" />
                  ) : (
                    <ChevronRight className="mt-1 h-4 w-4 shrink-0 text-muted-foreground" />
                  )}
                </button>

                {isExpanded && (
                  <div className="border-t border-border px-4 py-3">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs font-medium text-muted-foreground">Payload</span>
                    </div>
                    <div className="grid grid-cols-2 gap-4 mb-3">
                      <div className="rounded-lg bg-secondary/50 p-3">
                        <span className="mb-1 block text-xs text-muted-foreground">Old Price</span>
                        <span className="font-mono text-sm font-medium line-through opacity-70">₹{oldPrice}</span>
                      </div>
                      <div className="rounded-lg bg-secondary/50 p-3">
                        <span className="mb-1 block text-xs text-muted-foreground">New Price</span>
                        <span className="font-mono text-sm font-medium text-primary">₹{newPrice}</span>
                      </div>
                    </div>
                    {/* <pre className="overflow-x-auto rounded-lg bg-secondary/50 p-3 text-xs font-mono text-muted-foreground leading-relaxed">
                      {JSON.stringify(entry.payload, null, 2)}
                    </pre> */}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}