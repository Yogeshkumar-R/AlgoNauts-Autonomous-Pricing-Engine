// Server-side only: proxies requests to AWS API Gateway
// This file should ONLY be imported from API route handlers (app/api/*)

function getBackendUrl(): string {
  const raw =
    process.env.API_BASE ||
    process.env.API_GATEWAY_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    process.env.NEXT_PUBLIC_API_BASE ||
    ""

  // Normalize once so `${base}${path}` is predictable.
  return raw.replace(/\/+$/, "")
}

function getApiKey(): string {
  return process.env.API_GATEWAY_KEY || ""
}

export function isBackendConnected(): boolean {
  const backendUrl = getBackendUrl()
  const connected = !!backendUrl

  console.info("[backend] connectivity check", {
    connected,
    backendUrl,
    hasApiKey: !!getApiKey(),
    nodeEnv: process.env.NODE_ENV,
  })

  return connected
}

export async function backendFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const backendUrl = getBackendUrl()
  const apiKey = getApiKey()

  if (!backendUrl) {
    console.error("[backend] missing backend URL", {
      hasApiBase: !!process.env.API_BASE,
      hasApiGatewayUrl: !!process.env.API_GATEWAY_URL,
      hasNextPublicApiUrl: !!process.env.NEXT_PUBLIC_API_URL,
      hasNextPublicApiBase: !!process.env.NEXT_PUBLIC_API_BASE,
    })
    throw new Error("BACKEND_NOT_CONFIGURED")
  }

  const url = `${backendUrl}${path}`
  const method = options?.method || "GET"

  console.info("[backend] forwarding request", {
    method,
    path,
    url,
    hasApiKey: !!apiKey,
  })

  const res = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(apiKey ? { "x-api-key": apiKey } : {}),
      ...options?.headers,
    },
  })

  console.info("[backend] received response", {
    method,
    path,
    url,
    status: res.status,
    ok: res.ok,
  })

  if (!res.ok) {
    const errorText = await res.text().catch(() => "Unknown error")
    console.error("[backend] backend request failed", {
      method,
      path,
      url,
      status: res.status,
      errorText,
    })
    throw new Error(`Backend ${res.status}: ${errorText}`)
  }

  return res.json()
}
