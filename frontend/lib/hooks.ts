import useSWR from "swr"
import {
  fetchKPIs,
  fetchProducts,
  fetchRecentDecisions,
  fetchAlerts,
  fetchRevenueData,
  fetchDecisionLog,
  fetchHistoricalPrices,
  fetchProductDetail,
} from "./api"

export function useKPIs() {
  return useSWR("kpis", fetchKPIs, {
    refreshInterval: 30000,
    revalidateOnFocus: true,
  })
}

export function useProducts() {
  return useSWR("products", fetchProducts, {
    refreshInterval: 15000,
  })
}

export function useProductDetail(productId: string | null) {
  return useSWR(
    productId ? `product-detail-${productId}` : null,
    () => (productId ? fetchProductDetail(productId) : null),
    { refreshInterval: 30000 }
  )
}

export function useRecentDecisions() {
  return useSWR("recent-decisions", fetchRecentDecisions, {
    refreshInterval: 10000,
  })
}

export function useAlerts() {
  return useSWR("alerts", fetchAlerts, {
    refreshInterval: 10000,
  })
}

export function useRevenueData() {
  return useSWR("revenue-data", fetchRevenueData, {
    refreshInterval: 60000,
  })
}

export function useDecisionLog() {
  return useSWR("decision-log", fetchDecisionLog, {
    refreshInterval: 15000,
  })
}

export function useHistoricalPrices(productId: string | null) {
  return useSWR(
    productId ? `historical-prices-${productId}` : null,
    () => (productId ? fetchHistoricalPrices(productId) : null),
    { refreshInterval: 30000 }
  )
}
