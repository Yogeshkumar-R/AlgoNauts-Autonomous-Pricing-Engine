import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"
import { mockAlerts } from "@/lib/mock-data"
import type { Alert } from "@/lib/types"

export async function GET() {
  try {
    if (!isBackendConnected()) {
      return NextResponse.json(mockAlerts)
    }
    const data = await backendFetch<Alert[]>("/alerts")
    return NextResponse.json(data)
  } catch (error) {
    console.error("[api/alerts]", error)
    return NextResponse.json(mockAlerts)
  }
}
