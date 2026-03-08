"use client"

import { useEffect } from "react"
import { ProductsTable } from "@/components/products/products-table"

export default function ProductsPage() {
  useEffect(() => {
    console.info("[page] mounted /products")
  }, [])

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 lg:px-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">Products</h1>
        <p className="text-sm text-muted-foreground">
          Manage and monitor pricing across your product catalog
        </p>
      </div>
      <ProductsTable />
    </div>
  )
}
