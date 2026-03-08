// Server-side only: proxies requests to AWS API Gateway
// This file should ONLY be imported from API route handlers (app/api/*)

const BACKEND_URL = process.env.API_BASE || process.env.API_GATEWAY_URL || ""
const API_KEY = process.env.API_GATEWAY_KEY || ""

export function isBackendConnected(): boolean {
  return !!BACKEND_URL
}

export async function backendFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  if (!BACKEND_URL) {
    throw new Error("BACKEND_NOT_CONFIGURED")
  }

  const url = `${BACKEND_URL}${path}`

  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(API_KEY ? { "x-api-key": API_KEY } : {}),
      ...options?.headers,
    },
  })

  if (!res.ok) {
    const errorText = await res.text().catch(() => "Unknown error")
    throw new Error(`Backend ${res.status}: ${errorText}`)
  }

  return res.json()
}
