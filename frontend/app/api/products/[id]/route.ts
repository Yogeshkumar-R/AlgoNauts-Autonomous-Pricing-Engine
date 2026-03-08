import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"
import type { ProductDetailResponse } from "@/lib/types"

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params
  try {
    if (!isBackendConnected()) {
      return NextResponse.json(
        { error: "Backend not configured" },
        { status: 503 }
      )
    }
    const data = await backendFetch<ProductDetailResponse>(`/products/${id}`)
    return NextResponse.json(data)
  } catch (error) {
    // console.error(`[api/products/${id}]`, error)
    return NextResponse.json({ error: "Failed to fetch product" }, { status: 502 })
  }
}
