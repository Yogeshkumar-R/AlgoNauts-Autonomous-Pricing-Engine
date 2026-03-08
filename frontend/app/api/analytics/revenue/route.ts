import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"
import type { RevenueDataPoint } from "@/lib/types"

export async function GET() {
  try {
    if (!isBackendConnected()) {
      return NextResponse.json(
        { error: "Backend not configured" },
        { status: 503 }
      )
    }
    const data = await backendFetch<RevenueDataPoint[]>("/analytics/revenue")
    return NextResponse.json(data)
  } catch (error) {
    console.error("[api/analytics/revenue]", error)
    return NextResponse.json(
      { error: "Failed to fetch revenue analytics" },
      { status: 502 }
    )
  }
}
