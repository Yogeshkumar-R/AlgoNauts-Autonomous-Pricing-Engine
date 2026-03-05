import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"
import type { SimulationStatusResponse } from "@/lib/types"

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ runId: string }> }
) {
  const { runId } = await params
  try {
    if (!isBackendConnected()) {
      // In demo mode, pipeline is driven client-side
      return NextResponse.json({
        runId,
        status: "SUCCEEDED",
        steps: [],
      } satisfies SimulationStatusResponse)
    }

    const data = await backendFetch<SimulationStatusResponse>(
      `/simulate/${runId}/status`
    )
    return NextResponse.json(data)
  } catch (error) {
    console.error(`[api/simulate/${runId}/status]`, error)
    return NextResponse.json({ error: "Failed to get simulation status" }, { status: 500 })
  }
}
