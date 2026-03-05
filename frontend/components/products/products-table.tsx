"use client"

import { useState, useMemo } from "react"
import { Search, ArrowUpDown } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { useProducts } from "@/lib/hooks"
import { cn } from "@/lib/utils"
import { ProductDrawer } from "./product-drawer"
import type { Product } from "@/lib/types"

const statusColors: Record<string, string> = {
  stable: "bg-success/10 text-success border-success/20",
  adjusted: "bg-primary/10 text-primary border-primary/20",
  corrected: "bg-warning/10 text-warning border-warning/20",
}

type SortKey = "name" | "cost" | "currentPrice" | "competitorPrice" | "margin" | "status"

export function ProductsTable() {
  const { data: products, isLoading } = useProducts()
  const [search, setSearch] = useState("")
  const [sortKey, setSortKey] = useState<SortKey>("name")
  const [sortDir, setSortDir] = useState<"asc" | "desc">("asc")
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null)
  const [drawerOpen, setDrawerOpen] = useState(false)

  const filtered = useMemo(() => {
    if (!products) return []
    let result = products.filter(
      (p) =>
        p.name.toLowerCase().includes(search.toLowerCase()) ||
        p.category.toLowerCase().includes(search.toLowerCase())
    )
    result.sort((a, b) => {
      const aVal = a[sortKey]
      const bVal = b[sortKey]
      if (typeof aVal === "string" && typeof bVal === "string") {
        return sortDir === "asc" ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal)
      }
      return sortDir === "asc"
        ? (aVal as number) - (bVal as number)
        : (bVal as number) - (aVal as number)
    })
    return result
  }, [products, search, sortKey, sortDir])

  function handleSort(key: SortKey) {
    if (key === sortKey) {
      setSortDir(sortDir === "asc" ? "desc" : "asc")
    } else {
      setSortKey(key)
      setSortDir("asc")
    }
  }

  function handleRowClick(product: Product) {
    setSelectedProduct(product)
    setDrawerOpen(true)
  }

  if (isLoading) {
    return (
      <div className="rounded-xl border border-border bg-card p-5">
        <div className="mb-4 flex items-center gap-3">
          <Skeleton className="h-10 w-64" />
        </div>
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="mb-2 h-12 w-full rounded-lg" />
        ))}
      </div>
    )
  }

  const columns: { key: SortKey; label: string; className?: string }[] = [
    { key: "name", label: "Product Name" },
    { key: "cost", label: "Cost", className: "hidden md:table-cell" },
    { key: "currentPrice", label: "Price" },
    { key: "competitorPrice", label: "Competitor", className: "hidden lg:table-cell" },
    { key: "margin", label: "Margin %" },
    { key: "status", label: "Status" },
  ]

  return (
    <>
      <div className="rounded-xl border border-border bg-card">
        <div className="border-b border-border p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search products or categories..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="border-border bg-secondary/50 pl-10 text-card-foreground placeholder:text-muted-foreground"
            />
          </div>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-border">
                {columns.map((col) => (
                  <th
                    key={col.key}
                    className={cn(
                      "cursor-pointer px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-muted-foreground transition-colors hover:text-card-foreground",
                      col.className
                    )}
                    onClick={() => handleSort(col.key)}
                  >
                    <div className="flex items-center gap-1">
                      {col.label}
                      <ArrowUpDown className="h-3 w-3" />
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((product) => (
                <tr
                  key={product.id}
                  className="cursor-pointer border-b border-border/50 transition-colors hover:bg-secondary/30"
                  onClick={() => handleRowClick(product)}
                >
                  <td className="px-4 py-3">
                    <div>
                      <div className="text-sm font-medium text-card-foreground">{product.name}</div>
                      <div className="text-xs text-muted-foreground">{product.category}</div>
                    </div>
                  </td>
                  <td className="hidden px-4 py-3 text-sm text-muted-foreground md:table-cell">
                    {"₹"}{product.cost}
                  </td>
                  <td className="px-4 py-3 text-sm font-medium text-card-foreground">
                    {"₹"}{product.currentPrice}
                  </td>
                  <td className="hidden px-4 py-3 text-sm text-muted-foreground lg:table-cell">
                    {"₹"}{product.competitorPrice}
                  </td>
                  <td className="px-4 py-3">
                    <span className={cn("text-sm font-medium", product.margin >= 50 ? "text-success" : product.margin >= 30 ? "text-warning" : "text-destructive")}>
                      {product.margin}%
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <Badge variant="outline" className={cn("text-[10px] uppercase tracking-wider", statusColors[product.status])}>
                      {product.status}
                    </Badge>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={6} className="py-12 text-center text-sm text-muted-foreground">
                    No products found matching your search.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
        <div className="border-t border-border px-4 py-3 text-xs text-muted-foreground">
          Showing {filtered.length} of {products?.length ?? 0} products
        </div>
      </div>

      <ProductDrawer product={selectedProduct} open={drawerOpen} onOpenChange={setDrawerOpen} />
    </>
  )
}
