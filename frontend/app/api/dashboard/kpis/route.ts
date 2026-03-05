import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"
import { mockKPIs } from "@/lib/mock-data"
import type { KPIData } from "@/lib/types"

export async function GET() {
  try {
    if (!isBackendConnected()) {
      return NextResponse.json(mockKPIs)
    }
    const data = await backendFetch<KPIData>("/dashboard/kpis")
    return NextResponse.json(data)
  } catch (error) {
    console.error("[api/dashboard/kpis]", error)
    return NextResponse.json(mockKPIs)
  }
}
