import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"
import type { IngestMarketDataRequest, IngestMarketDataResponse } from "@/lib/types"

export async function POST(request: Request) {
  try {
    const body: IngestMarketDataRequest = await request.json()

    if (!body.productId || typeof body.competitorPrice !== "number") {
      return NextResponse.json(
        { error: "productId and competitorPrice are required" },
        { status: 400 }
      )
    }

    if (!isBackendConnected()) {
      return NextResponse.json(
        { error: "Backend not configured" },
        { status: 503 }
      )
    }

    const data = await backendFetch<IngestMarketDataResponse>("/ingest/market-data", {
      method: "POST",
      body: JSON.stringify(body),
    })
    return NextResponse.json(data)
  } catch (error) {
    // console.error("[api/ingest/market-data]", error)
    return NextResponse.json({ error: "Ingestion failed" }, { status: 500 })
  }
}
