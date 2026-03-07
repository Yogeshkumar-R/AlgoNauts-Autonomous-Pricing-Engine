"use client"

import { useState } from "react"
import { Wifi, WifiOff, Database, Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { postSeed } from "@/lib/api"
import { toast } from "sonner"
import { cn } from "@/lib/utils"

export function ConnectionBanner() {
  const isConnected = !!process.env.NEXT_PUBLIC_API_BASE || !!process.env.NEXT_PUBLIC_API_URL
  const [seeding, setSeeding] = useState(false)

  async function handleSeed() {
    setSeeding(true)
    try {
      const res = await postSeed()
      toast.success(`${res.message} (${res.productsSeeded} products)`)
    } catch {
      toast.error("Failed to seed data")
    } finally {
      setSeeding(false)
    }
  }

  return (
    <div
      className={cn(
        "flex items-center justify-between rounded-lg border px-4 py-2.5 text-xs",
        isConnected
          ? "border-success/20 bg-success/5 text-success"
          : "border-warning/20 bg-warning/5 text-warning"
      )}
    >
      <div className="flex items-center gap-2">
        {isConnected ? (
          <Wifi className="h-3.5 w-3.5" />
        ) : (
          <WifiOff className="h-3.5 w-3.5" />
        )}
        <span className="font-medium">
          {isConnected
            ? "Connected to AWS API Gateway"
            : "Demo Mode - Using mock data"}
        </span>
        {!isConnected && (
          <span className="text-muted-foreground">
            Set API_BASE env var to connect
          </span>
        )}
      </div>
      {/* <Button
        variant="ghost"
        size="sm"
        onClick={handleSeed}
        disabled={seeding}
        className="h-7 gap-1.5 text-xs"
      >
        {seeding ? (
          <Loader2 className="h-3 w-3 animate-spin" />
        ) : (
          <Database className="h-3 w-3" />
        )}
        Seed Data
      </Button> */}
    </div>
  )
}
