"use client"

import { useState, useRef, useEffect, JSX } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { Send, Bot, User, ShieldAlert, Sparkles, Loader2, PlusCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { postAIQuery } from "@/lib/api"
import type { ChatMessage } from "@/lib/types"

const quickPrompts = [
  "What products need price adjustments today?",
  "Show me my margin analysis",
  "How is competitor pricing trending?",
  "Explain the last AI decision",
  "Suggest pricing strategy for electronics",
]

const welcomeMessage: ChatMessage = {
  id: `welcome`,
  role: "assistant",
  content: "Hello! I'm your AI Pricing Assistant. How can I help you today?",
  timestamp: new Date().toISOString(),
}

/**
 * Preprocess text to add proper line breaks
 */
function preprocessText(text: string): string {
  let processed = text
  
  // Fix tables - add line breaks between table rows
  // Pattern: |...|...|  |...|...| becomes |...|...|\n|...|...|
  processed = processed.replace(/\|\s+\|/g, '|\n|')
  
  // Add line breaks before headings (#### ### ## #)
  // Match any non-whitespace followed by heading markers
  processed = processed.replace(/(\S)\s*(#{1,4})\s+(\w)/g, '$1\n\n$2 $3')
  
  // Also handle headings at the start of text
  processed = processed.replace(/^(#{1,4})\s+(\w)/gm, '\n$1 $2')
  
  // Add line breaks before list items (but not nested ones with leading spaces)
  processed = processed.replace(/([^\n])\s+\*\s+(?!\s)/g, '$1\n* ')
  processed = processed.replace(/([^\n])\s+-\s+(?!\s)/g, '$1\n- ')
  
  // Add line breaks before horizontal rules
  processed = processed.replace(/(\S)\s+(---)/g, '$1\n\n$2')
  
  // Add line breaks after horizontal rules
  processed = processed.replace(/(---)\s+(\S)/g, '$1\n\n$2')
  
  // Clean up: remove multiple consecutive newlines (keep max 2)
  processed = processed.replace(/\n{3,}/g, '\n\n')
  
  // Remove standalone # at the start or on its own line
  processed = processed.replace(/^#\s*$/gm, '')
  processed = processed.replace(/^#\s*\n/gm, '')
  
  // Trim leading/trailing whitespace
  processed = processed.trim()
  
  console.log('========== PREPROCESSED TEXT ==========')
  console.log(processed)
  console.log('=======================================')
  
  return processed
}

/**
 * Parse markdown text into React elements
 */
function parseMarkdown(text: string) {
  console.log('========== ORIGINAL TEXT ==========')
  console.log(text)
  console.log('===================================')
  
  // Preprocess to add line breaks
  const preprocessed = preprocessText(text)
  
  const lines = preprocessed.split('\n')
  const elements: JSX.Element[] = []
  let currentList: { type: 'ul' | 'ol'; items: string[] } | null = null
  let tableLines: string[] = []
  let inTable = false
  
  const flushList = () => {
    if (currentList) {
      const ListTag = currentList.type
      elements.push(
        <ListTag key={`list-${elements.length}`} className="my-2 space-y-1 pl-5 list-disc text-sm">
          {currentList.items.map((item, i) => (
            <li key={i} className="text-muted-foreground leading-relaxed font-normal">
              {parseInline(item)}
            </li>
          ))}
        </ListTag>
      )
      currentList = null
    }
  }
  
  const flushTable = () => {
    if (tableLines.length > 0) {
      const table = renderTable(tableLines, elements.length)
      if (table) {
        elements.push(table)
      }
      tableLines = []
      inTable = false
    }
  }
  
  console.log('========== PROCESSING LINES ==========')
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()
    
    // Skip empty lines
    if (!line) {
      flushList()
      flushTable()
      continue
    }
    
    console.log(`Line ${i}: "${line}"`)
    
    // Check for table
    if (line.startsWith('|') && line.endsWith('|')) {
      flushList()
      inTable = true
      tableLines.push(line)
      console.log(`  → TABLE LINE`)
      continue
    } else if (inTable) {
      flushTable()
    }
    
    // Headings
    if (line.startsWith('####')) {
      flushList()
      console.log(`  → H4 HEADING`)
      elements.push(
        <h4 key={`h4-${i}`} className="font-semibold text-card-foreground mt-3 mb-1.5 first:mt-0 text-sm">
          {parseInline(line.replace(/^####\s*/, ''))}
        </h4>
      )
      continue
    }
    
    if (line.startsWith('###')) {
      flushList()
      console.log(`  → H3 HEADING`)
      elements.push(
        <h3 key={`h3-${i}`} className="font-semibold text-card-foreground mt-3 mb-1.5 first:mt-0 text-sm">
          {parseInline(line.replace(/^###\s*/, ''))}
        </h3>
      )
      continue
    }
    
    if (line.startsWith('##')) {
      flushList()
      console.log(`  → H2 HEADING`)
      elements.push(
        <h2 key={`h2-${i}`} className="font-semibold text-card-foreground mt-3 mb-1.5 first:mt-0 text-base">
          {parseInline(line.replace(/^##\s*/, ''))}
        </h2>
      )
      continue
    }
    
    // Horizontal rule
    if (line === '---' || line === '***' || line === '___') {
      flushList()
      console.log(`  → HORIZONTAL RULE`)
      elements.push(<hr key={`hr-${i}`} className="my-4 border-border" />)
      continue
    }
    
    // Unordered list
    if (line.match(/^[-*]\s/)) {
      const content = line.replace(/^[-*]\s/, '')
      console.log(`  → LIST ITEM (UL): "${content}"`)
      if (!currentList || currentList.type !== 'ul') {
        flushList()
        currentList = { type: 'ul', items: [] }
      }
      currentList.items.push(content)
      continue
    }
    
    // Ordered list
    if (line.match(/^\d+\.\s/)) {
      const content = line.replace(/^\d+\.\s/, '')
      console.log(`  → LIST ITEM (OL): "${content}"`)
      if (!currentList || currentList.type !== 'ol') {
        flushList()
        currentList = { type: 'ol', items: [] }
      }
      currentList.items.push(content)
      continue
    }
    
    // Regular paragraph
    flushList()
    console.log(`  → PARAGRAPH`)
    elements.push(
      <p key={`p-${i}`} className="mb-2 last:mb-0 text-muted-foreground leading-relaxed text-sm font-normal">
        {parseInline(line)}
      </p>
    )
  }
  
  // Flush any remaining list or table
  flushList()
  flushTable()
  
  console.log(`========== GENERATED ${elements.length} ELEMENTS ==========`)
  
  return elements
}

/**
 * Parse inline markdown (bold, code, etc.)
 */
function parseInline(text: string): React.ReactNode {
  const parts: React.ReactNode[] = []
  let remaining = text
  let key = 0
  
  // Process text piece by piece
  while (remaining.length > 0) {
    // Try to match bold (**text** or __text__)
    const boldMatch = remaining.match(/(\*\*|__)([^*_]+?)\1/)
    
    // Try to match inline code (`text`)
    const codeMatch = remaining.match(/`([^`]+?)`/)
    
    // Find which match comes first
    const boldIndex = boldMatch ? remaining.indexOf(boldMatch[0]) : -1
    const codeIndex = codeMatch ? remaining.indexOf(codeMatch[0]) : -1
    
    let nextMatchIndex = -1
    let nextMatchLength = 0
    let nextMatchType: 'bold' | 'code' | null = null
    
    if (boldIndex >= 0 && (codeIndex < 0 || boldIndex < codeIndex)) {
      nextMatchIndex = boldIndex
      nextMatchLength = boldMatch![0].length
      nextMatchType = 'bold'
    } else if (codeIndex >= 0) {
      nextMatchIndex = codeIndex
      nextMatchLength = codeMatch![0].length
      nextMatchType = 'code'
    }
    
    if (nextMatchIndex >= 0) {
      // Add text before the match
      if (nextMatchIndex > 0) {
        parts.push(remaining.substring(0, nextMatchIndex))
      }
      
      // Add the matched element
      if (nextMatchType === 'bold' && boldMatch) {
        parts.push(
          <strong key={`bold-${key++}`} className="font-semibold text-card-foreground">
            {boldMatch[2]}
          </strong>
        )
      } else if (nextMatchType === 'code' && codeMatch) {
        parts.push(
          <code key={`code-${key++}`} className="bg-secondary/80 px-1 py-0.5 rounded text-xs font-mono text-card-foreground">
            {codeMatch[1]}
          </code>
        )
      }
      
      // Move past this match
      remaining = remaining.substring(nextMatchIndex + nextMatchLength)
    } else {
      // No more matches, add remaining text
      parts.push(remaining)
      break
    }
  }
  
  return parts.length > 0 ? parts : text
}

/**
 * Render table from markdown
 */
function renderTable(lines: string[], key: number) {
  if (lines.length < 2) return null
  
  // Parse header
  const headerCells = lines[0]
    .split('|')
    .map(cell => cell.trim())
    .filter(cell => cell)
  
  // Skip separator line (line 1)
  // Parse body rows
  const bodyRows = lines.slice(2).map(line =>
    line
      .split('|')
      .map(cell => cell.trim())
      .filter(cell => cell)
  )
  
  return (
    <table key={`table-${key}`} className="w-full border-collapse my-3 text-xs">
      <thead className="bg-secondary/30">
        <tr className="border-b border-border/50">
          {headerCells.map((cell, i) => (
            <th key={i} className="px-2 py-1.5 text-left font-medium text-card-foreground text-xs">
              {parseInline(cell)}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {bodyRows.map((row, i) => (
          <tr key={i} className="border-b border-border/50">
            {row.map((cell, j) => (
              <td key={j} className="px-2 py-1.5 text-muted-foreground text-xs">
                {parseInline(cell)}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}

export function AIChat() {

  const router = useRouter()
  const searchParams = useSearchParams()

  const conversationParam = searchParams.get("conversation") ?? undefined

  const [messages, setMessages] = useState<ChatMessage[]>([welcomeMessage])
  const [conversation_id, setconversation_id] = useState<string | undefined>(conversationParam)
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const hasUserMessage = messages.some((m) => m.role === "user")

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])


  /*
  ----------------------------
  LOAD HISTORY WHEN URL CHANGES
  ----------------------------
  */

  useEffect(() => {

    if (!conversationParam || conversationParam === "undefined") return

    async function loadHistory() {

      try {

        const res = await fetch(`/api/ai/history/${conversationParam}`)
        const data = await res.json()

        if (data?.messages?.length) {

          const formatted: ChatMessage[] = data.messages.map((m: any, i: number) => ({
            id: `${m.role}-${i}`,
            role: m.role,
            content: m.content,
            timestamp: m.timestamp,
          }))

          setMessages(formatted)
          setconversation_id(conversationParam)

        }

      } catch (err) {

        console.error("Failed to load conversation history", err)

      }

    }

    loadHistory()

  }, [conversationParam])


  /*
  ----------------------------
  SEND MESSAGE
  ----------------------------
  */

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

      const res = await postAIQuery(text, conversation_id)

      /*
      When first message creates conversation
      update URL so sidebar works
      */

      if (res.conversation_id && !conversation_id) {

        setconversation_id(res.conversation_id)

        router.replace(`/ai-chat?conversation=${res.conversation_id}`)

      }

      const aiMsg: ChatMessage = {
        id: `a-${Date.now()}`,
        role: "assistant",
        content: res.response,
        timestamp: new Date().toISOString(),
      }

      setMessages((prev) => [...prev, aiMsg])

    } catch (err) {

      console.error(err)

      const errorMsg: ChatMessage = {
        id: `e-${Date.now()}`,
        role: "assistant",
        content: "Something went wrong. Please try again.",
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


  /*
  ----------------------------
  NEW CHAT
  ----------------------------
  */

  function handleNewChat() {

    setMessages([welcomeMessage])
    setconversation_id(undefined)
    setInput("")

    router.push("/ai-chat")

    inputRef.current?.focus()
  }
  
  return (
    <div className="flex h-full flex-col rounded-xl border border-border bg-card">
      <div className="flex items-center gap-3 border-b border-border px-5 py-4">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary/10">
          <Sparkles className="h-4 w-4 text-primary" />
        </div>
        <div>
          <h3 className="text-sm font-semibold text-card-foreground">
            AI Pricing Assistant
          </h3>
          <p className="text-xs text-muted-foreground">
            Powered by Amazon Bedrock
          </p>
        </div>
        <div className="ml-auto">
          <Button
            variant="ghost"
            size="sm"
            onClick={handleNewChat}
            className="h-8 gap-1.5 px-3 text-xs"
          >
            <PlusCircle className="h-3.5 w-3.5" />
            New Chat
          </Button>
        </div>
      </div>
      <div className="flex flex-1 flex-col gap-4 overflow-y-auto p-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={cn(
              "flex gap-3",
              msg.role === "user" ? "flex-row-reverse" : "flex-row"
            )}
          >
            <div
              className={cn(
                "flex h-8 w-8 shrink-0 items-center justify-center rounded-lg",
                msg.role === "user" ? "bg-primary/10" : "bg-secondary"
              )}
            >
              {msg.role === "user"
                ? <User className="h-4 w-4 text-primary" />
                : <Bot className="h-4 w-4 text-card-foreground" />}
            </div>
            <div
              className={cn(
                "max-w-[80%] break-words rounded-xl px-4 py-3 leading-relaxed",
                msg.role === "user"
                  ? "bg-primary text-primary-foreground text-sm"
                  : "bg-secondary/50"
              )}
            >
              {msg.role === "user" ? (
                <p className="text-sm">{msg.content}</p>
              ) : (
                <div>
                  {parseMarkdown(msg.content)}
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-secondary">
              <Bot className="h-4 w-4 text-card-foreground" />
            </div>
            <div className="flex items-center gap-2 rounded-xl bg-secondary/50 px-4 py-3">
              <Loader2 className="h-4 w-4 animate-spin text-primary" />
              <span className="text-sm text-muted-foreground">
                Thinking...
              </span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      {!hasUserMessage && (
        <div className="flex shrink-0 gap-2 overflow-x-auto border-t border-border px-4 py-3">
          {quickPrompts.map((prompt) => (
            <button
              key={prompt}
              onClick={() => handleSend(prompt)}
              className="shrink-0 rounded-full border border-border bg-secondary/50 px-3 py-1.5 text-xs text-muted-foreground hover:border-primary/30 hover:text-card-foreground"
            >
              {prompt}
            </button>
          ))}
        </div>
      )}
      <div className="border-t border-border p-4">
        <div className="flex items-end gap-2">
          <textarea
            ref={inputRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about pricing, margins, competitor analysis..."
            className="max-h-32 min-h-[42px] flex-1 resize-none rounded-lg border border-border bg-secondary/50 px-4 py-2.5 text-sm text-card-foreground"
          />
          <Button
            onClick={() => handleSend()}
            disabled={!input.trim() || isLoading}
            size="icon"
            className="h-[42px] w-[42px]"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}