import type {
  Product,
  PricingDecision,
  KPIData,
  Alert,
  RevenueDataPoint,
  DecisionLogEntry,
  SimulationScenario,
  ChatMessage,
  HistoricalPrice,
} from "./types"

export const mockKPIs: KPIData = {
  activeProducts: 342,
  avgMargin: 23.4,
  revenueToday: 284500,
  aiConfidence: 94.2,
  activeProductsDelta: 12,
  avgMarginDelta: 1.8,
  revenueDelta: 8.3,
  confidenceDelta: 0.5,
}

export const mockProducts: Product[] = [
  { id: "1", name: "Wireless Earbuds Pro", cost: 450, currentPrice: 899, competitorPrice: 849, margin: 49.9, status: "stable", category: "Electronics", lastUpdated: "2026-03-04T10:30:00Z" },
  { id: "2", name: "USB-C Hub 7-in-1", cost: 320, currentPrice: 599, competitorPrice: 549, margin: 46.6, status: "adjusted", category: "Electronics", lastUpdated: "2026-03-04T09:15:00Z" },
  { id: "3", name: "Bamboo Desk Organizer", cost: 180, currentPrice: 399, competitorPrice: 449, margin: 54.9, status: "stable", category: "Home", lastUpdated: "2026-03-03T18:00:00Z" },
  { id: "4", name: "Organic Cotton T-Shirt", cost: 120, currentPrice: 249, competitorPrice: 229, margin: 51.8, status: "corrected", category: "Apparel", lastUpdated: "2026-03-04T11:00:00Z" },
  { id: "5", name: "Stainless Steel Bottle", cost: 95, currentPrice: 199, competitorPrice: 189, margin: 52.3, status: "stable", category: "Home", lastUpdated: "2026-03-03T14:30:00Z" },
  { id: "6", name: "LED Desk Lamp", cost: 280, currentPrice: 549, competitorPrice: 499, margin: 49.0, status: "adjusted", category: "Electronics", lastUpdated: "2026-03-04T08:45:00Z" },
  { id: "7", name: "Yoga Mat Premium", cost: 200, currentPrice: 449, competitorPrice: 399, margin: 55.5, status: "stable", category: "Fitness", lastUpdated: "2026-03-02T16:00:00Z" },
  { id: "8", name: "Bluetooth Speaker Mini", cost: 350, currentPrice: 699, competitorPrice: 649, margin: 49.9, status: "adjusted", category: "Electronics", lastUpdated: "2026-03-04T10:00:00Z" },
  { id: "9", name: "Leather Wallet Slim", cost: 150, currentPrice: 349, competitorPrice: 299, margin: 57.0, status: "corrected", category: "Accessories", lastUpdated: "2026-03-04T07:30:00Z" },
  { id: "10", name: "Phone Case Ultra", cost: 45, currentPrice: 129, competitorPrice: 99, margin: 65.1, status: "stable", category: "Electronics", lastUpdated: "2026-03-03T20:00:00Z" },
  { id: "11", name: "Portable Charger 20K", cost: 520, currentPrice: 999, competitorPrice: 949, margin: 47.9, status: "adjusted", category: "Electronics", lastUpdated: "2026-03-04T11:30:00Z" },
  { id: "12", name: "Cotton Bed Sheets Set", cost: 400, currentPrice: 799, competitorPrice: 849, margin: 49.9, status: "stable", category: "Home", lastUpdated: "2026-03-02T12:00:00Z" },
]

export const mockRecentDecisions: PricingDecision[] = [
  { id: "d1", productId: "2", productName: "USB-C Hub 7-in-1", oldPrice: 649, newPrice: 599, reason: "Competitor price drop detected. AI adjusted to maintain market position.", confidence: 92, type: "ai_correction", timestamp: "2026-03-04T09:15:00Z", status: "applied" },
  { id: "d2", productId: "4", productName: "Organic Cotton T-Shirt", oldPrice: 279, newPrice: 249, reason: "Demand spike pattern detected. Guardrail capped discount at 10%.", confidence: 88, type: "guardrail", timestamp: "2026-03-04T11:00:00Z", status: "applied" },
  { id: "d3", productId: "6", productName: "LED Desk Lamp", oldPrice: 499, newPrice: 549, reason: "Margin recovery triggered after inventory restock.", confidence: 95, type: "deterministic", timestamp: "2026-03-04T08:45:00Z", status: "applied" },
  { id: "d4", productId: "9", productName: "Leather Wallet Slim", oldPrice: 399, newPrice: 349, reason: "AI recommended price cut. Guardrail blocked below-cost pricing.", confidence: 76, type: "guardrail", timestamp: "2026-03-04T07:30:00Z", status: "blocked" },
  { id: "d5", productId: "8", productName: "Bluetooth Speaker Mini", oldPrice: 749, newPrice: 699, reason: "Seasonal demand adjustment based on historical patterns.", confidence: 91, type: "monitoring", timestamp: "2026-03-04T10:00:00Z", status: "applied" },
]

export const mockAlerts: Alert[] = [
  { id: "a1", type: "warning", message: "Margin deviation detected: below 20% threshold", productName: "USB-C Hub 7-in-1", timestamp: "2026-03-04T09:20:00Z" },
  { id: "a2", type: "error", message: "Competitor price undercut by 15%", productName: "Leather Wallet Slim", timestamp: "2026-03-04T07:35:00Z" },
  { id: "a3", type: "info", message: "AI confidence improved after retraining cycle", productName: "System", timestamp: "2026-03-04T06:00:00Z" },
  { id: "a4", type: "warning", message: "Unusual demand pattern detected", productName: "Organic Cotton T-Shirt", timestamp: "2026-03-04T10:50:00Z" },
]

export const mockRevenueData: RevenueDataPoint[] = [
  { date: "Feb 25", revenue: 245000, competitor: 238000 },
  { date: "Feb 26", revenue: 258000, competitor: 242000 },
  { date: "Feb 27", revenue: 252000, competitor: 251000 },
  { date: "Feb 28", revenue: 267000, competitor: 255000 },
  { date: "Mar 01", revenue: 271000, competitor: 260000 },
  { date: "Mar 02", revenue: 278000, competitor: 265000 },
  { date: "Mar 03", revenue: 280000, competitor: 268000 },
  { date: "Mar 04", revenue: 284500, competitor: 272000 },
]

export const mockDecisionLog: DecisionLogEntry[] = [
  { id: "dl1", type: "deterministic", productName: "LED Desk Lamp", description: "Rule-based price increase: inventory restocked, demand stable, margin target met.", timestamp: "2026-03-04T08:45:00Z", status: "success", payload: { rule: "margin_recovery", oldPrice: 499, newPrice: 549, inventoryLevel: 450, marginTarget: 48 } },
  { id: "dl2", type: "guardrail", productName: "Organic Cotton T-Shirt", description: "Guardrail validation: discount capped at 10%. AI requested 15% reduction.", timestamp: "2026-03-04T11:00:00Z", status: "warning", payload: { requestedDiscount: 15, appliedDiscount: 10, maxAllowed: 10, reason: "exceeds_max_discount" } },
  { id: "dl3", type: "ai_correction", productName: "USB-C Hub 7-in-1", description: "AI-driven price adjustment based on competitor intelligence and demand forecasting.", timestamp: "2026-03-04T09:15:00Z", status: "success", payload: { model: "claude-haiku-4.5", confidence: 0.92, competitorDelta: -50, demandForecast: "increasing" } },
  { id: "dl4", type: "guardrail", productName: "Leather Wallet Slim", description: "BLOCKED: Proposed price would result in negative margin. Minimum margin guardrail triggered.", timestamp: "2026-03-04T07:30:00Z", status: "blocked", payload: { proposedPrice: 129, cost: 150, resultingMargin: -14, minimumMargin: 15, action: "blocked" } },
  { id: "dl5", type: "monitoring", productName: "Bluetooth Speaker Mini", description: "Monitoring detected seasonal demand pattern. Triggered price review cycle.", timestamp: "2026-03-04T10:00:00Z", status: "info", payload: { seasonalIndex: 1.15, avgDailyDemand: 45, forecastDemand: 52, triggerThreshold: 1.1 } },
  { id: "dl6", type: "deterministic", productName: "Phone Case Ultra", description: "Scheduled review: no action needed. Price within optimal range.", timestamp: "2026-03-04T06:00:00Z", status: "success", payload: { optimalRange: [119, 139], currentPrice: 129, action: "no_change" } },
]

export const mockScenarios: SimulationScenario[] = [
  { id: "s1", name: "Competitor Price Drop", description: "Simulate a major competitor dropping prices by 10-20% across electronics category.", type: "competitor_drop" },
  { id: "s2", name: "Demand Spike", description: "Simulate a sudden demand increase (3x normal) triggered by a flash sale event.", type: "demand_spike" },
  { id: "s3", name: "Inventory Shift", description: "Simulate low inventory alert triggering price protection mechanisms.", type: "inventory_shift" },
]

export const mockChatMessages: ChatMessage[] = [
  { id: "c1", role: "assistant", content: "Hello! I'm your PRIME. I can help you analyze pricing strategies, explain recent decisions, and provide market insights. What would you like to know?", timestamp: "2026-03-04T10:00:00Z" },
]

export const mockHistoricalPrices: HistoricalPrice[] = [
  { date: "Feb 18", price: 699, competitorPrice: 699 },
  { date: "Feb 20", price: 699, competitorPrice: 679 },
  { date: "Feb 22", price: 679, competitorPrice: 659 },
  { date: "Feb 24", price: 649, competitorPrice: 649 },
  { date: "Feb 26", price: 649, competitorPrice: 629 },
  { date: "Feb 28", price: 619, competitorPrice: 599 },
  { date: "Mar 01", price: 599, competitorPrice: 569 },
  { date: "Mar 02", price: 599, competitorPrice: 549 },
  { date: "Mar 04", price: 599, competitorPrice: 549 },
]

export function generatePipelineSteps() {
  return [
    { id: "p1", name: "Ingest Market Data", status: "pending" as const },
    { id: "p2", name: "Deterministic Pricing", status: "pending" as const },
    { id: "p3", name: "AI Analysis (Bedrock)", status: "pending" as const },
    { id: "p4", name: "Guardrail Validation", status: "pending" as const },
    { id: "p5", name: "Apply Decision", status: "pending" as const },
    { id: "p6", name: "Monitor & Report", status: "pending" as const },
  ]
}
