"use client"

import { useState, useRef, useEffect } from "react"
import { Send, Bot, User, ShieldAlert, Sparkles, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { cn } from "@/lib/utils"
import { postAIQuery } from "@/lib/api"
import { mockChatMessages } from "@/lib/mock-data"
import type { ChatMessage } from "@/lib/types"

const quickPrompts = [
  "What products need price adjustments today?",
  "Show me my margin analysis",
  "How is competitor pricing trending?",
  "Explain the last AI decision",
  "Suggest pricing strategy for electronics",
]

function MarkdownLite({ text }: { text: string }) {
  // Simple markdown-like rendering for bold, headers, bullets
  const lines = text.split("\n")
  return (
    <div className="flex flex-col gap-1.5">
      {lines.map((line, i) => {
        if (line.startsWith("**") && line.endsWith("**")) {
          return <p key={i} className="font-semibold text-card-foreground">{line.slice(2, -2)}</p>
        }
        if (line.startsWith("- ")) {
          return (
            <div key={i} className="flex items-start gap-2">
              <div className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-primary" />
              <span>{renderBold(line.slice(2))}</span>
            </div>
          )
        }
        if (line.trim() === "") return <div key={i} className="h-1" />
        return <p key={i}>{renderBold(line)}</p>
      })}
    </div>
  )
}

function renderBold(text: string) {
  const parts = text.split(/\*\*(.*?)\*\*/)
  return parts.map((part, i) =>
    i % 2 === 1 ? (
      <strong key={i} className="text-card-foreground">{part}</strong>
    ) : (
      <span key={i}>{part}</span>
    )
  )
}

export function AIChat() {
  const [messages, setMessages] = useState<ChatMessage[]>(mockChatMessages)
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [conversationId, setConversationId] = useState<string | undefined>()
  const scrollRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages])

  async function handleSend(prompt?: string) {
    const text = prompt || input.trim()
    if (!text || isLoading) return

    const userMsg: ChatMessage = {
      id: `u-${Date.now()}`,
      role: "user",
      content: text,
      timestamp: new Date().toISOString(),
    }

    setMessages((prev) => [...prev, userMsg])
    setInput("")
    setIsLoading(true)

    try {
      const res = await postAIQuery(text, conversationId)
      if (res.conversationId) {
        setConversationId(res.conversationId)
      }
      const aiMsg: ChatMessage = {
        id: `a-${Date.now()}`,
        role: "assistant",
        content: res.response,
        timestamp: new Date().toISOString(),
        metadata: {
          confidence: res.confidence,
          recommendation: res.recommendation,
          blocked: res.blocked,
          blockReason: res.blockReason,
          sources: res.sources,
        },
      }
      setMessages((prev) => [...prev, aiMsg])
    } catch {
      const errorMsg: ChatMessage = {
        id: `e-${Date.now()}`,
        role: "assistant",
        content: "I encountered an error processing your request. Please try again.",
        timestamp: new Date().toISOString(),
      }
      setMessages((prev) => [...prev, errorMsg])
    } finally {
      setIsLoading(false)
    }
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="flex h-[calc(100vh-10rem)] flex-col rounded-xl border border-border bg-card md:h-[calc(100vh-8rem)]">
      {/* Chat Header */}
      <div className="flex items-center gap-3 border-b border-border px-5 py-4">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
          <Sparkles className="h-4 w-4 text-primary" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-card-foreground">AI Pricing Assistant</h3>
          <p className="text-xs text-muted-foreground">Powered by Amazon Bedrock</p>
        </div>
        <div className="ml-auto flex items-center gap-1.5">
          <div className="h-2 w-2 rounded-full bg-success" />
          <span className="text-xs text-muted-foreground">Online</span>
        </div>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 p-4" ref={scrollRef}>
        <div className="flex flex-col gap-4">
          {messages.map((msg) => (
            <div key={msg.id} className={cn("flex gap-3", msg.role === "user" ? "flex-row-reverse" : "flex-row")}>
              <div className={cn(
                "flex h-8 w-8 shrink-0 items-center justify-center rounded-lg",
                msg.role === "user" ? "bg-primary/10" : "bg-secondary"
              )}>
                {msg.role === "user" ? (
                  <User className="h-4 w-4 text-primary" />
                ) : (
                  <Bot className="h-4 w-4 text-card-foreground" />
                )}
              </div>
              <div className={cn(
                "max-w-[80%] rounded-xl px-4 py-3 text-sm leading-relaxed",
                msg.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "bg-secondary/50 text-muted-foreground"
              )}>
                {msg.metadata?.blocked ? (
                  <div className="flex items-start gap-2">
                    <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0 text-destructive" />
                    <div>
                      <p className="font-medium text-destructive">Guardrail Blocked</p>
                      <p className="mt-1 text-xs">{msg.metadata.blockReason || "This query was blocked by safety guardrails."}</p>
                    </div>
                  </div>
                ) : (
                  <MarkdownLite text={msg.content} />
                )}

                {msg.metadata && !msg.metadata.blocked && (msg.metadata.confidence || msg.metadata.recommendation) && (
                  <div className="mt-3 flex flex-col gap-2 border-t border-border/50 pt-3">
                    {msg.metadata.confidence && (
                      <div className="flex items-center gap-2">
                        <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-secondary">
                          <div
                            className="h-full rounded-full bg-primary transition-all duration-500"
                            style={{ width: `${msg.metadata.confidence}%` }}
                          />
                        </div>
                        <span className="text-xs font-medium text-primary">{msg.metadata.confidence}%</span>
                      </div>
                    )}
                    {msg.metadata.recommendation && (
                      <div className="rounded-lg border border-primary/20 bg-primary/5 px-3 py-2">
                        <p className="text-xs font-medium text-primary">Recommendation</p>
                        <p className="text-xs text-muted-foreground">{msg.metadata.recommendation}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3">
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-secondary">
                <Bot className="h-4 w-4 text-card-foreground" />
              </div>
              <div className="flex items-center gap-2 rounded-xl bg-secondary/50 px-4 py-3">
                <Loader2 className="h-4 w-4 animate-spin text-primary" />
                <span className="text-sm text-muted-foreground">Analyzing...</span>
              </div>
            </div>
          )}
        </div>
      </ScrollArea>

      {/* Quick Prompts */}
      <div className="flex gap-2 overflow-x-auto border-t border-border px-4 py-3">
        {quickPrompts.map((prompt) => (
          <button
            key={prompt}
            onClick={() => handleSend(prompt)}
            disabled={isLoading}
            className="shrink-0 rounded-full border border-border bg-secondary/50 px-3 py-1.5 text-xs text-muted-foreground transition-colors hover:border-primary/30 hover:text-card-foreground disabled:opacity-50"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input */}
      <div className="border-t border-border p-4">
        <div className="flex items-end gap-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about pricing, margins, competitor analysis..."
            className="max-h-32 min-h-[42px] flex-1 resize-none rounded-lg border border-border bg-secondary/50 px-4 py-2.5 text-sm text-card-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            rows={1}
          />
          <Button
            onClick={() => handleSend()}
            disabled={!input.trim() || isLoading}
            size="icon"
            className="h-[42px] w-[42px] shrink-0 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            <Send className="h-4 w-4" />
            <span className="sr-only">Send message</span>
          </Button>
        </div>
      </div>
    </div>
  )
}
