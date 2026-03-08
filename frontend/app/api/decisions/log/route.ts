import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"
import type { DecisionLogEntry } from "@/lib/types"

export async function GET() {
  try {
    if (!isBackendConnected()) {
      return NextResponse.json(
        { error: "Backend not configured" },
        { status: 503 }
      )
    }

    try {
      const data = await backendFetch<DecisionLogEntry[]>("/decisions/log")
      return NextResponse.json(data)
    } catch {
      const data = await backendFetch<DecisionLogEntry[]>("/decisions/recent")
      return NextResponse.json(data)
    }
  } catch (error) {
    // console.error("[api/decisions/log]", error)
    return NextResponse.json(
      { error: "Failed to fetch decision log" },
      { status: 502 }
    )
  }
}
