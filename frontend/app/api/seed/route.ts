import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"
import type { SeedRequest, SeedResponse } from "@/lib/types"

export async function POST(request: Request) {
  try {
    const body: SeedRequest = await request.json()

    if (!isBackendConnected()) {
      return NextResponse.json(
        { error: "Backend not configured" },
        { status: 503 }
      )
    }

    const data = await backendFetch<SeedResponse>("/seed", {
      method: "POST",
      body: JSON.stringify(body),
    })
    return NextResponse.json(data)
  } catch (error) {
    console.error("[api/seed]", error)
    return NextResponse.json({ error: "Seed operation failed" }, { status: 500 })
  }
}
