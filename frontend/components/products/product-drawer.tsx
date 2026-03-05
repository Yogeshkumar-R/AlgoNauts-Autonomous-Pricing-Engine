"use client"

import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet"
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Skeleton } from "@/components/ui/skeleton"
import { useHistoricalPrices, useProductDetail } from "@/lib/hooks"
import { cn } from "@/lib/utils"
import type { Product } from "@/lib/types"

interface ProductDrawerProps {
  product: Product | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

const statusColors: Record<string, string> = {
  stable: "bg-success/10 text-success border-success/20",
  adjusted: "bg-primary/10 text-primary border-primary/20",
  corrected: "bg-warning/10 text-warning border-warning/20",
}

export function ProductDrawer({ product, open, onOpenChange }: ProductDrawerProps) {
  const { data: historicalPrices, isLoading } = useHistoricalPrices(product?.id ?? null)
  const { data: productDetail } = useProductDetail(product?.id ?? null)

  if (!product) return null

  const relatedDecisions = productDetail?.decisions ?? []

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-full border-border bg-card sm:max-w-lg">
        <SheetHeader>
          <SheetTitle className="text-card-foreground">{product.name}</SheetTitle>
          <SheetDescription className="flex items-center gap-2">
            <Badge variant="outline" className={cn(statusColors[product.status])}>
              {product.status}
            </Badge>
            <span className="text-muted-foreground">{product.category}</span>
          </SheetDescription>
        </SheetHeader>

        <ScrollArea className="h-[calc(100vh-120px)] pr-4">
          <div className="flex flex-col gap-6 pb-6">
            {/* Price Summary */}
            <div className="grid grid-cols-3 gap-3">
              <div className="rounded-lg border border-border bg-secondary/30 p-3">
                <div className="text-xs text-muted-foreground">Cost</div>
                <div className="text-lg font-semibold text-card-foreground">{"₹"}{product.cost}</div>
              </div>
              <div className="rounded-lg border border-border bg-secondary/30 p-3">
                <div className="text-xs text-muted-foreground">Current Price</div>
                <div className="text-lg font-semibold text-primary">{"₹"}{product.currentPrice}</div>
              </div>
              <div className="rounded-lg border border-border bg-secondary/30 p-3">
                <div className="text-xs text-muted-foreground">Margin</div>
                <div className="text-lg font-semibold text-success">{product.margin}%</div>
              </div>
            </div>

            {/* Historical Pricing Chart */}
            <div>
              <h4 className="mb-3 text-sm font-semibold text-card-foreground">Historical Pricing</h4>
              {isLoading || !historicalPrices ? (
                <Skeleton className="h-48 w-full rounded-lg" />
              ) : (
                <div className="rounded-lg border border-border bg-secondary/20 p-3">
                  <ResponsiveContainer width="100%" height={200}>
                    <AreaChart data={historicalPrices} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                      <defs>
                        <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.3} />
                          <stop offset="95%" stopColor="var(--primary)" stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                      <XAxis dataKey="date" tick={{ fill: "var(--muted-foreground)", fontSize: 10 }} axisLine={false} tickLine={false} />
                      <YAxis tick={{ fill: "var(--muted-foreground)", fontSize: 10 }} axisLine={false} tickLine={false} tickFormatter={(v) => `₹${v}`} />
                      <Tooltip
                        contentStyle={{ backgroundColor: "var(--card)", border: "1px solid var(--border)", borderRadius: "8px", fontSize: "12px", color: "var(--foreground)" }}
                      />
                      <Area type="monotone" dataKey="price" stroke="var(--primary)" strokeWidth={2} fill="url(#priceGradient)" name="Your Price" />
                      <Area type="monotone" dataKey="competitorPrice" stroke="var(--chart-5)" strokeWidth={1.5} fill="none" strokeDasharray="4 4" name="Competitor" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>

            {/* Decision Log */}
            <div>
              <h4 className="mb-3 text-sm font-semibold text-card-foreground">Decision Log</h4>
              {relatedDecisions.length === 0 ? (
                <p className="text-xs text-muted-foreground">No recent decisions for this product.</p>
              ) : (
                <div className="space-y-2">
                  {relatedDecisions.map((d) => (
                    <div key={d.id} className="rounded-lg border border-border bg-secondary/20 p-3">
                      <div className="mb-1 flex items-center justify-between">
                        <Badge variant="outline" className="text-[10px] uppercase tracking-wider">
                          {d.type.replace("_", " ")}
                        </Badge>
                        <span className="text-[10px] text-muted-foreground">
                          {new Date(d.timestamp).toLocaleString("en-IN", { dateStyle: "short", timeStyle: "short" })}
                        </span>
                      </div>
                      <p className="text-xs leading-relaxed text-muted-foreground">{d.reason}</p>
                      <div className="mt-2 flex items-center gap-2 text-xs">
                        <span className="text-muted-foreground line-through">{"₹"}{d.oldPrice}</span>
                        <span className="font-medium text-card-foreground">{"₹"}{d.newPrice}</span>
                        <span className="ml-auto text-muted-foreground">Confidence: {d.confidence}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* AI Explanation */}
            <div>
              <h4 className="mb-3 text-sm font-semibold text-card-foreground">AI Explanation</h4>
              <div className="rounded-lg border border-primary/20 bg-primary/5 p-4">
                <p className="text-xs leading-relaxed text-muted-foreground">
                  This product is currently in <strong className="text-card-foreground">{product.status}</strong> state.
                  {product.status === "stable" && " No pricing action is needed. Current pricing is within the optimal range based on market conditions and margin targets."}
                  {product.status === "adjusted" && " The AI engine recently adjusted pricing based on competitive intelligence and demand forecasting. The adjustment aims to optimize revenue while maintaining the target margin."}
                  {product.status === "corrected" && " A guardrail correction was applied. The AI-recommended price was modified to comply with business rules and margin protection policies."}
                </p>
              </div>
            </div>
          </div>
        </ScrollArea>
      </SheetContent>
    </Sheet>
  )
}
