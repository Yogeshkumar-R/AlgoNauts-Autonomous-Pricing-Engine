import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"
import { mockRecentDecisions } from "@/lib/mock-data"
import type { PricingDecision } from "@/lib/types"

export async function GET() {
  try {
    if (!isBackendConnected()) {
      return NextResponse.json(mockRecentDecisions)
    }
    const data = await backendFetch<PricingDecision[]>("/decisions/recent")
    return NextResponse.json(data)
  } catch (error) {
    console.error("[api/decisions/recent]", error)
    return NextResponse.json(mockRecentDecisions)
  }
}
