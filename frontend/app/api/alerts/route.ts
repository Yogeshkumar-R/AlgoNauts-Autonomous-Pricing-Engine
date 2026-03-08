import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"
import type { Alert } from "@/lib/types"

export async function GET() {
  try {
    if (!isBackendConnected()) {
      return NextResponse.json(
        { error: "Backend not configured" },
        { status: 503 }
      )
    }
    const data = await backendFetch<Alert[]>("/alerts")
    return NextResponse.json(data)
  } catch (error) {
    console.error("[api/alerts]", error)
    return NextResponse.json(
      { error: "Failed to fetch alerts" },
      { status: 502 }
    )
  }
}
