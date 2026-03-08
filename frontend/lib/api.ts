// API client - All calls go through Next.js API routes (/api/*)
// which proxy to the real AWS API Gateway backend.
// When NEXT_PUBLIC_API_URL is not set, the API routes return mock data.

import type {
  KPIData,
  Product,
  PricingDecision,
  Alert,
  RevenueDataPoint,
  DecisionLogEntry,
  HistoricalPrice,
  PipelineStep,
  AIQueryResponse,
  SimulateResponse,
  SimulationStatusResponse,
  SeedResponse,
  IngestMarketDataResponse,
  ProductDetailResponse,
} from "./types"

// ── Helpers ──────────────────────────────────────────

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  })

  if (!res.ok) {
    const errorBody = await res.text().catch(() => "Unknown error")
    throw new Error(`API Error ${res.status}: ${errorBody}`)
  }

  return res.json()
}
export type Conversation = {
  id: string
  title: string
  lastMessage?: string
  messageCount?: number
}

export type ConversationsResponse = {
  conversations: Conversation[]
}

// ── Dashboard ────────────────────────────────────────

export function fetchKPIs(): Promise<KPIData> {
  return apiFetch("/api/dashboard/kpis")
}

// ── Products ─────────────────────────────────────────

export function fetchProducts(): Promise<Product[]> {
  return apiFetch("/api/products")
}

export function fetchProductDetail(productId: string): Promise<ProductDetailResponse> {
  return apiFetch(`/api/products/${productId}`)
}

export function fetchHistoricalPrices(productId: string): Promise<HistoricalPrice[]> {
  return apiFetch(`/api/products/${productId}/history`)
}

// ── Decisions ────────────────────────────────────────

export function fetchRecentDecisions(): Promise<PricingDecision[]> {
  return apiFetch("/api/decisions/recent")
}

export function fetchDecisionLog(): Promise<DecisionLogEntry[]> {
  return apiFetch("/api/decisions/log")
}

// ── Alerts ───────────────────────────────────────────

export function fetchAlerts(): Promise<Alert[]> {
  return apiFetch("/api/alerts")
}

// ── Analytics ────────────────────────────────────────

export function fetchRevenueData(): Promise<RevenueDataPoint[]> {
  return apiFetch("/api/analytics/revenue")
}

// ── AI Chat ──────────────────────────────────────────

export function fetchConversations(): Promise<ConversationsResponse> {
  return apiFetch("/api/ai/conversations")
}

export function postAIQuery(
  query: string,
  conversationId?: string
): Promise<AIQueryResponse> {
  return apiFetch("/api/ai/query", {
    method: "POST",
    body: JSON.stringify({ query, conversationId }),
  })
}

// ── Simulation ───────────────────────────────────────

export function postSimulation(
  scenario: string,
  productIds?: string[]
): Promise<SimulateResponse> {
  return apiFetch("/api/simulate", {
    method: "POST",
    body: JSON.stringify({ scenario, productIds }),
  })
}

export function fetchSimulationStatus(runId: string): Promise<SimulationStatusResponse> {
  return apiFetch(`/api/simulate/${runId}/status`)
}

// ── Seed & Ingest ────────────────────────────────────

export function postSeed(productCount?: number): Promise<SeedResponse> {
  return apiFetch("/api/seed", {
    method: "POST",
    body: JSON.stringify({ productCount }),
  })
}

export function postIngestMarketData(
  productId: string,
  competitorPrice: number,
  demandScore?: number
): Promise<IngestMarketDataResponse> {
  return apiFetch("/api/ingest/market-data", {
    method: "POST",
    body: JSON.stringify({ productId, competitorPrice, demandScore }),
  })
}

// ── Pipeline Simulation (client-side for demo) ───────

export async function simulatePipelineProgress(
  runId: string,
  onUpdate: (steps: PipelineStep[]) => void
): Promise<void> {
  const isBackendConnected = !!process.env.NEXT_PUBLIC_API_URL

  if (isBackendConnected) {
    // Poll real backend for step function status
    let done = false
    while (!done) {
      try {
        const status = await fetchSimulationStatus(runId)
        onUpdate(status.steps)
        if (status.status === "SUCCEEDED" || status.status === "FAILED") {
          done = true
        } else {
          await new Promise((r) => setTimeout(r, 2000))
        }
      } catch {
        done = true
      }
    }
  } else {
    // Mock pipeline animation for demo
    const { generatePipelineSteps } = await import("./mock-data")
    const steps = generatePipelineSteps()

    for (let i = 0; i < steps.length; i++) {
      steps[i].status = "running"
      onUpdate([...steps])
      await new Promise((r) => setTimeout(r, 800 + Math.random() * 1200))
      steps[i].status = "completed"
      steps[i].duration = Math.floor(400 + Math.random() * 800)
      onUpdate([...steps])
      await new Promise((r) => setTimeout(r, 200))
    }
  }
}


