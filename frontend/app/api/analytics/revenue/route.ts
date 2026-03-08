import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"
import { mockRevenueData } from "@/lib/mock-data"
import type { RevenueDataPoint } from "@/lib/types"

export async function GET() {
  try {
    if (!isBackendConnected()) {
      return NextResponse.json(mockRevenueData)
    }
    const data = await backendFetch<RevenueDataPoint[]>("/analytics/revenue")
    return NextResponse.json(data)
  } catch (error) {
    console.error("[api/analytics/revenue]", error)
    return NextResponse.json(mockRevenueData)
  }
}
