import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"
import type { AIQueryRequest, AIQueryResponse } from "@/lib/types"

export async function POST(request: Request) {
  try {
    const body: AIQueryRequest = await request.json()

    if (!body.query || typeof body.query !== "string" || body.query.trim().length === 0) {
      return NextResponse.json({ error: "Query is required" }, { status: 400 })
    }

    // Sanitize input
    const sanitizedQuery = body.query.trim().slice(0, 2000)

    if (!isBackendConnected()) {
      return NextResponse.json(
        { error: "Backend not configured" },
        { status: 503 }
      )
    }

    const data = await backendFetch<AIQueryResponse>("/ai/query", {
      method: "POST",
      body: JSON.stringify({
        query_type: "query",
        seller_id: "SELLER-001",
        query: sanitizedQuery,
        conversation_id: body.conversation_id, // Use camelCase from the request body
        context: body.context, // Assuming context is also passed
      }),
    })
    return NextResponse.json(data)
  } catch (error) {
    console.error("[api/ai/query]", error)
    return NextResponse.json(
      { error: "Failed to query AI service" },
      { status: 502 }
    )
  }
}
