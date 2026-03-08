"use client"

import { useEffect } from "react"
import { DecisionTimeline } from "@/components/decisions/decision-timeline"

export default function DecisionsPage() {
  useEffect(() => {
    // console.info("[page] mounted /decisions")
  }, [])

  return (
    <div className="mx-auto max-w-4xl px-4 py-6 lg:px-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">Decision Log</h1>
        <p className="text-sm text-muted-foreground">
          Complete audit trail of all pricing decisions, guardrail checks, and AI corrections
        </p>
      </div>
      <DecisionTimeline />
    </div>
  )
}
