import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"

export async function GET() {
  try {
    if (!isBackendConnected()) {
      return NextResponse.json(
        { error: "Backend not configured" },
        { status: 503 }
      )
    }

    const data = await backendFetch("/ai/conversations", {
      method: "GET",
    })

    return NextResponse.json(data)

  } catch (error) {
    console.error("[api/ai/conversations]", error)

    return NextResponse.json(
      { error: "Failed to fetch conversations" },
      { status: 502 }
    )
  }
}
