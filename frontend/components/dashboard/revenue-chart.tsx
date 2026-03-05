"use client"

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { useRevenueData } from "@/lib/hooks"
import { Skeleton } from "@/components/ui/skeleton"

export function RevenueChart() {
  const { data, isLoading } = useRevenueData()

  if (isLoading || !data) {
    return (
      <div className="rounded-xl border border-border bg-card p-5">
        <Skeleton className="mb-4 h-5 w-48" />
        <Skeleton className="h-64 w-full rounded-lg" />
      </div>
    )
  }

  return (
    <div className="rounded-xl border border-border bg-card p-5">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-card-foreground">Revenue vs Competitor Trend</h3>
          <p className="text-xs text-muted-foreground">Last 8 days comparison</p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full bg-primary" />
            <span className="text-muted-foreground">Your Revenue</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="h-2 w-2 rounded-full bg-chart-5" />
            <span className="text-muted-foreground">Competitor</span>
          </div>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.3} />
              <stop offset="95%" stopColor="var(--primary)" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorCompetitor" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="var(--chart-5)" stopOpacity={0.15} />
              <stop offset="95%" stopColor="var(--chart-5)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
          <XAxis
            dataKey="date"
            tick={{ fill: "var(--muted-foreground)", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "var(--muted-foreground)", fontSize: 12 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}K`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--card)",
              border: "1px solid var(--border)",
              borderRadius: "8px",
              fontSize: "12px",
              color: "var(--foreground)",
            }}
            formatter={(value: number) => [`₹${value.toLocaleString("en-IN")}`, ""]}
            labelStyle={{ color: "var(--muted-foreground)" }}
          />
          <Area
            type="monotone"
            dataKey="revenue"
            stroke="var(--primary)"
            strokeWidth={2}
            fill="url(#colorRevenue)"
            name="Your Revenue"
          />
          <Area
            type="monotone"
            dataKey="competitor"
            stroke="var(--chart-5)"
            strokeWidth={2}
            fill="url(#colorCompetitor)"
            name="Competitor"
            strokeDasharray="4 4"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
