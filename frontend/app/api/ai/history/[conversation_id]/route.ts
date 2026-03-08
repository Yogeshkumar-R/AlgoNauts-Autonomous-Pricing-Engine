import { NextResponse } from "next/server"
import { backendFetch, isBackendConnected } from "@/lib/backend"

export async function GET(
    request: Request,
    { params }: { params: Promise<{ conversation_id: string }> }
) {
    const { conversation_id } = await params

    try {
        if (!isBackendConnected()) {
            return NextResponse.json(
                { error: "Backend not configured" },
                { status: 503 }
            )
        }

        const data = await backendFetch(
            `/ai/history/${encodeURIComponent(conversation_id)}`,
            {
                method: "GET",
            }
        )

        return NextResponse.json(data)

    } catch (error) {
        // console.error("[api/ai/history]", error)

        return NextResponse.json(
            { error: "Failed to fetch conversation history" },
            { status: 502 }
        )
    }
}
