import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"
import { mockProducts } from "@/lib/mock-data"
import type { Product } from "@/lib/types"

export async function GET() {
  try {
    if (!isBackendConnected()) {
      return NextResponse.json(mockProducts)
    }
    const data = await backendFetch<Product[]>("/products")
    return NextResponse.json(data)
  } catch (error) {
    console.error("[api/products]", error)
    return NextResponse.json(mockProducts)
  }
}
