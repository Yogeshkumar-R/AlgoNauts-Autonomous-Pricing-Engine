import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"
import type { Product } from "@/lib/types"

export async function GET() {
  try {
    if (!isBackendConnected()) {
      return NextResponse.json(
        { error: "Backend not configured" },
        { status: 503 }
      )
    }
    const data = await backendFetch<Product[]>("/products")
    return NextResponse.json(data)
  } catch (error) {
    console.error("[api/products]", error)
    return NextResponse.json(
      { error: "Failed to fetch products" },
      { status: 502 }
    )
  }
}
