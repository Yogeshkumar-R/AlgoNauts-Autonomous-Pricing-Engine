import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"
import type { SimulateRequest, SimulateResponse } from "@/lib/types"

export async function POST(request: Request) {
  try {
    const body: SimulateRequest = await request.json()

    const validScenarios = ["competitor_drop", "demand_spike", "inventory_shift"]
    if (!body.scenario || !validScenarios.includes(body.scenario)) {
      return NextResponse.json({ error: "Invalid scenario type" }, { status: 400 })
    }

    if (!isBackendConnected()) {
      // Mock simulation response
      return NextResponse.json({
        runId: `sim-${Date.now()}`,
        executionArn: `arn:aws:states:ap-south-1:mock:execution:PricingPipeline:sim-${Date.now()}`,
        status: "RUNNING",
      } satisfies SimulateResponse)
    }

    const data = await backendFetch<any>("/simulate", {
      method: "POST",
      body: JSON.stringify(body),
    })
    
    // Extract runId from execution_arn
    const executionArn = data.execution_arn || data.executionArn || ""
    const runId = executionArn.split(':').pop() || `sim-${Date.now()}`
    
    return NextResponse.json({
      runId,
      executionArn,
      status: "RUNNING"
    } satisfies SimulateResponse)
  } catch (error) {
    console.error("[api/simulate]", error)
    return NextResponse.json({ error: "Simulation failed to start" }, { status: 500 })
  }
}
