import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"
import type { PricingDecision } from "@/lib/types"

export async function GET() {
  try {
    if (!isBackendConnected()) {
      return NextResponse.json(
        { error: "Backend not configured" },
        { status: 503 }
      )
    }
    const data = await backendFetch<PricingDecision[]>("/decisions/recent")
    return NextResponse.json(data)
  } catch (error) {
    // console.error("[api/decisions/recent]", error)
    return NextResponse.json(
      { error: "Failed to fetch recent decisions" },
      { status: 502 }
    )
  }
}
