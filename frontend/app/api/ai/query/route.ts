import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"
import type { AIQueryRequest, AIQueryResponse } from "@/lib/types"

// Mock AI responses for demo mode
const mockResponses: Record<string, AIQueryResponse> = {
  default: {
    response: `Based on my analysis of your current pricing landscape:\n\n**Market Position:** Your portfolio is well-positioned with an average margin of 23.4%. I've identified 3 products that could benefit from price adjustments.\n\n**Key Insights:**\n- USB-C Hub 7-in-1 is priced 9% above the closest competitor - consider a strategic reduction\n- Bamboo Desk Organizer has room for a 5-8% increase based on demand elasticity\n- Organic Cotton T-Shirt demand has increased 15% this week\n\n**Recommendation:** Focus on the electronics category where competitor activity is highest. I can run a detailed simulation if you'd like.`,
    confidence: 94,
    recommendation: "Review electronics pricing within 24 hours",
  },
  margin: {
    response: `**Margin Analysis Summary:**\n\n**Top Performers (>50% margin):**\n- Phone Case Ultra: 65.1%\n- Leather Wallet Slim: 57.0%\n- Yoga Mat Premium: 55.5%\n- Bamboo Desk Organizer: 54.9%\n\n**At Risk (<48% margin):**\n- Portable Charger 20K: 47.9% - competitor pressure increasing\n- USB-C Hub 7-in-1: 46.6% - recently adjusted downward\n\n**Overall Health:** 10 of 12 products above target margin of 45%. The portfolio average of 23.4% reflects weighted revenue contribution.`,
    confidence: 97,
    recommendation: "Monitor Portable Charger 20K margins closely",
  },
  competitor: {
    response: `**Competitor Pricing Trends (Last 7 Days):**\n\n**Aggressive Moves Detected:**\n- Electronics category saw 5-10% price drops across 3 competitor SKUs\n- Home category remains stable with minimal competitor activity\n\n**Your Response:**\n- AI auto-adjusted USB-C Hub and Bluetooth Speaker to stay competitive\n- Maintained premium positioning on Bamboo Desk Organizer (priced above competitor)\n\n**Forecast:** Expect continued competitor pressure in electronics through Q1. Recommend maintaining AI-driven dynamic pricing for this category.`,
    confidence: 89,
    recommendation: "Enable aggressive mode for electronics pricing",
  },
}

function getMockResponse(query: string): AIQueryResponse {
  const q = query.toLowerCase()
  if (q.includes("margin")) return mockResponses.margin
  if (q.includes("competitor") || q.includes("competition")) return mockResponses.competitor
  return mockResponses.default
}

export async function POST(request: Request) {
  try {
    const body: AIQueryRequest = await request.json()

    if (!body.query || typeof body.query !== "string" || body.query.trim().length === 0) {
      return NextResponse.json({ error: "Query is required" }, { status: 400 })
    }

    // Sanitize input
    const sanitizedQuery = body.query.trim().slice(0, 2000)

    if (!isBackendConnected()) {
      // Simulate network latency
      await new Promise((r) => setTimeout(r, 800 + Math.random() * 800))
      return NextResponse.json(getMockResponse(sanitizedQuery))
    }

    const data = await backendFetch<AIQueryResponse>("/ai/query", {
      method: "POST",
      body: JSON.stringify({
        query_type: "query",
        seller_id: "SELLER-001",
        query: sanitizedQuery,
        conversationId: body.conversationId,
        context: body.context,
      }),
    })
    return NextResponse.json(data)
  } catch (error) {
    console.error("[api/ai/query]", error)
    return NextResponse.json(
      {
        response: "I'm having trouble connecting to the AI service right now. Please try again in a moment.",
        confidence: 0,
        blocked: false,
      },
      { status: 200 } // Return 200 so the chat UI handles it gracefully
    )
  }
}
