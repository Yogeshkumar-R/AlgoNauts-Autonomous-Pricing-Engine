import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"
import { mockProducts, mockRecentDecisions, mockHistoricalPrices } from "@/lib/mock-data"
import type { ProductDetailResponse } from "@/lib/types"

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  try {
    if (!isBackendConnected()) {
      const product = mockProducts.find((p) => p.id === id)
      if (!product) {
        return NextResponse.json({ error: "Product not found" }, { status: 404 })
      }
      return NextResponse.json({
        ...product,
        historicalPrices: mockHistoricalPrices,
        decisions: mockRecentDecisions.filter((d) => d.productId === id),
      })
    }
    const data = await backendFetch<ProductDetailResponse>(`/products/${id}`)
    return NextResponse.json(data)
  } catch (error) {
    console.error(`[api/products/${id}]`, error)
    return NextResponse.json({ error: "Failed to fetch product" }, { status: 500 })
  }
}
