import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"
import { mockDecisionLog } from "@/lib/mock-data"
import type { DecisionLogEntry } from "@/lib/types"

export async function GET() {
  try {
    if (!isBackendConnected()) {
      return NextResponse.json(mockDecisionLog)
    }
    const data = await backendFetch<DecisionLogEntry[]>("/decisions/log")
    return NextResponse.json(data)
  } catch (error) {
    console.error("[api/decisions/log]", error)
    return NextResponse.json(mockDecisionLog)
  }
}
