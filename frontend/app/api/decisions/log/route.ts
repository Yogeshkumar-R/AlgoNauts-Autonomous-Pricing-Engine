import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"
import { mockDecisionLog } from "@/lib/mock-data"
import type { DecisionLogEntry } from "@/lib/types"

export async function GET() {
  try {
    if (!isBackendConnected()) {
      return NextResponse.json(mockDecisionLog)
    }
    
    // Try /decisions/log first, fallback to /decisions/recent
    try {
      const data = await backendFetch<DecisionLogEntry[]>("/decisions/log")
      return NextResponse.json(data)
    } catch (error) {
      // Fallback to recent decisions if log endpoint doesn't exist
      const data = await backendFetch<DecisionLogEntry[]>("/decisions/recent")
      return NextResponse.json(data)
    }
  } catch (error) {
    console.error("[api/decisions/log]", error)
    return NextResponse.json(mockDecisionLog)
  }
}
