// Core domain types for the Autonomous Pricing Manager
// These types map directly to the DynamoDB item shapes returned by the backend

export type ProductStatus = "stable" | "adjusted" | "corrected"

export interface Product {
  id: string
  name: string
  cost: number
  currentPrice: number
  competitorPrice: number
  margin: number
  status: ProductStatus
  category: string
  lastUpdated: string
  // Extended fields from DynamoDB
  sku?: string
  inventoryLevel?: number
  demandScore?: number
}

export interface PricingDecision {
  id: string
  productId: string
  productName: string
  oldPrice: number
  newPrice: number
  reason: string
  confidence: number
  type: "deterministic" | "ai_correction" | "guardrail" | "monitoring"
  timestamp: string
  status: "applied" | "blocked" | "pending"
  // Extended fields from Step Functions output
  executionArn?: string
  stepFunctionRunId?: string
}

export interface KPIData {
  activeProducts: number
  avgMargin: number
  revenueToday: number
  aiConfidence: number | null
  activeProductsDelta: number | null
  avgMarginDelta: number | null
  revenueDelta: number | null
  confidenceDelta: number | null
}

export interface Alert {
  id: string
  type: "warning" | "error" | "info"
  message: string
  productName: string
  timestamp: string
  acknowledged?: boolean
}

export interface RevenueDataPoint {
  date: string
  revenue: number
  competitor: number
}

export interface DecisionLogEntry {
  id: string
  type: "deterministic" | "guardrail" | "monitoring" | "ai_correction"
  productName: string
  description: string
  timestamp: string
  status: "success" | "blocked" | "warning" | "info"
  payload: Record<string, unknown>
}

export interface SimulationScenario {
  id: string
  name: string
  description: string
  type: "competitor_drop" | "demand_spike" | "inventory_shift"
}

export interface PipelineStep {
  id: string
  name: string
  status: "pending" | "running" | "completed" | "failed"
  duration?: number
  output?: Record<string, unknown>
}

export interface ChatMessage {
  id: string
  role: "user" | "assistant" | "system"
  content: string
  timestamp: string
  metadata?: {
    confidence?: number
    recommendation?: string
    blocked?: boolean
    blockReason?: string
    sources?: string[]
  }
}

export interface HistoricalPrice {
  date: string
  price: number
  competitorPrice: number
}

// ────────────────────────────────────────────
// API Request / Response contracts
// These define exactly what the backend must accept and return
// ────────────────────────────────────────────

/** POST /seed - Seed demo data */
export interface SeedRequest {
  productCount?: number
  category?: string
}
export interface SeedResponse {
  success: boolean
  message: string
  productsSeeded: number
}

/** POST /simulate - Trigger a pricing simulation */
export interface SimulateRequest {
  scenario: "competitor_drop" | "demand_spike" | "inventory_shift"
  productIds?: string[]
}
export interface SimulateResponse {
  runId: string
  executionArn: string
  status: "RUNNING" | "SUCCEEDED" | "FAILED"
}

/** GET /simulate/:runId/status - Poll simulation progress */
export interface SimulationStatusResponse {
  runId: string
  status: "RUNNING" | "SUCCEEDED" | "FAILED"
  steps: PipelineStep[]
  result?: {
    decisionsApplied: number
    decisionsBlocked: number
    avgConfidence: number
  }
}

/** POST /ingest/market-data - Ingest market data */
export interface IngestMarketDataRequest {
  productId: string
  competitorPrice: number
  demandScore?: number
  source?: string
}
export interface IngestMarketDataResponse {
  success: boolean
  productId: string
  priceUpdated: boolean
}

/** POST /ai/query - AI chat query */
export interface AIQueryRequest {
  query: string
  conversationId?: string
  context?: {
    productIds?: string[]
    timeRange?: string
  }
}
export interface AIQueryResponse {
  response: string
  confidence: number
  recommendation?: string
  blocked?: boolean
  blockReason?: string
  conversationId?: string
  sources?: string[]
}

/** GET /dashboard/kpis */
export type DashboardKPIsResponse = KPIData

/** GET /products */
export type ProductsListResponse = Product[]

/** GET /products/:id */
export type ProductDetailResponse = Product & {
  historicalPrices: HistoricalPrice[]
  decisions: PricingDecision[]
}

/** GET /products/:id/history */
export type ProductHistoryResponse = HistoricalPrice[]

/** GET /decisions/recent */
export type RecentDecisionsResponse = PricingDecision[]

/** GET /decisions/log */
export type DecisionLogResponse = DecisionLogEntry[]

/** GET /alerts */
export type AlertsResponse = Alert[]

/** GET /analytics/revenue */
export type RevenueAnalyticsResponse = RevenueDataPoint[]
