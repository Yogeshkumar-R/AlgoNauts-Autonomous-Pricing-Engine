"use client"

import { Suspense, useEffect } from "react"
import { AIChat } from "@/components/chat/ai-chat"

export default function AIChatPage() {
  useEffect(() => {
    console.info("[page] mounted /ai-chat")
  }, [])

  return (
    <div className="mx-auto max-w-6xl px-4 py-6 lg:px-8 h-[calc(100vh-10px)] flex flex-col">
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">
          AI Pricing Manager
        </h1>
        <p className="text-sm text-muted-foreground">
          Chat with your AI assistant for pricing insights and recommendations
        </p>
      </div>

      <div className="flex-1 overflow-hidden">
        <Suspense fallback={<div className="p-4 text-sm text-muted-foreground">Loading chat...</div>}>
          <AIChat />
        </Suspense>
      </div>
    </div>
  )
}
