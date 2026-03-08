import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"
import { mockHistoricalPrices } from "@/lib/mock-data"
import type { HistoricalPrice } from "@/lib/types"

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  try {
    if (!isBackendConnected()) {
      return NextResponse.json(mockHistoricalPrices)
    }
    const data = await backendFetch<HistoricalPrice[]>(`/products/${id}/history`)
    return NextResponse.json(data)
  } catch (error) {
    console.error(`[api/products/${id}/history]`, error)
    return NextResponse.json(mockHistoricalPrices)
  }
}
