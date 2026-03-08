import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"
import type { KPIData } from "@/lib/types"

export async function GET() {
  try {
    if (!isBackendConnected()) {
      return NextResponse.json(
        { error: "Backend not configured" },
        { status: 503 }
      )
    }
    const data = await backendFetch<KPIData>("/dashboard/kpis")
    return NextResponse.json(data)
  } catch (error) {
    console.error("[api/dashboard/kpis]", error)
    return NextResponse.json(
      { error: "Failed to fetch dashboard KPIs" },
      { status: 502 }
    )
  }
}
