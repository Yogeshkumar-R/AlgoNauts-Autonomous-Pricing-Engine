"use client"

import { useState } from "react"
import {
  TrendingDown,
  Flame,
  Package,
  Play,
  CheckCircle2,
  Loader2,
  Circle,
  XCircle,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { mockScenarios } from "@/lib/mock-data"
import { postSimulation, simulatePipelineProgress } from "@/lib/api"
import { toast } from "sonner"
import type { PipelineStep, SimulationScenario } from "@/lib/types"

const scenarioIcons = {
  competitor_drop: TrendingDown,
  demand_spike: Flame,
  inventory_shift: Package,
}

const scenarioColors = {
  competitor_drop: "border-destructive/30 hover:border-destructive/50",
  demand_spike: "border-warning/30 hover:border-warning/50",
  inventory_shift: "border-primary/30 hover:border-primary/50",
}

const scenarioIconColors = {
  competitor_drop: "text-destructive bg-destructive/10",
  demand_spike: "text-warning bg-warning/10",
  inventory_shift: "text-primary bg-primary/10",
}

function StepIcon({ status }: { status: PipelineStep["status"] }) {
  switch (status) {
    case "completed":
      return <CheckCircle2 className="h-5 w-5 text-success" />
    case "running":
      return <Loader2 className="h-5 w-5 animate-spin text-primary" />
    case "failed":
      return <XCircle className="h-5 w-5 text-destructive" />
    default:
      return <Circle className="h-5 w-5 text-muted-foreground/30" />
  }
}

export function SimulationControl() {
  const [selectedScenario, setSelectedScenario] = useState<SimulationScenario | null>(null)
  const [isRunning, setIsRunning] = useState(false)
  const [pipelineSteps, setPipelineSteps] = useState<PipelineStep[]>([])
  const [runComplete, setRunComplete] = useState(false)

  async function handleRunSimulation() {
    if (!selectedScenario || isRunning) return

    setIsRunning(true)
    setRunComplete(false)
    setPipelineSteps([])

    try {
      // Trigger the simulation on the backend (or get mock runId)
      const { runId } = await postSimulation(selectedScenario.type)

      // Track pipeline progress (polls real backend or animates mock)
      await simulatePipelineProgress(runId, (steps) => {
        setPipelineSteps([...steps])
      })

      setRunComplete(true)
      toast.success("Simulation completed successfully")
    } catch (error) {
      toast.error("Simulation failed. Please try again.")
      console.error("[simulation]", error)
    } finally {
      setIsRunning(false)
    }
  }

  const completedSteps = pipelineSteps.filter((s) => s.status === "completed").length
  const totalSteps = pipelineSteps.length
  const progress = totalSteps > 0 ? (completedSteps / totalSteps) * 100 : 0

  return (
    <div className="flex flex-col gap-6">
      {/* Scenario Selection */}
      <div>
        <h3 className="mb-3 text-sm font-semibold text-foreground">Select Scenario</h3>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          {mockScenarios.map((scenario) => {
            const Icon = scenarioIcons[scenario.type]
            const isSelected = selectedScenario?.id === scenario.id
            return (
              <button
                key={scenario.id}
                onClick={() => {
                  setSelectedScenario(scenario)
                  setRunComplete(false)
                  setPipelineSteps([])
                }}
                disabled={isRunning}
                className={cn(
                  "flex flex-col items-start gap-3 rounded-xl border bg-card p-4 text-left transition-all duration-200 disabled:opacity-50",
                  isSelected ? "border-primary ring-1 ring-primary/30" : scenarioColors[scenario.type]
                )}
              >
                <div className={cn("flex h-10 w-10 items-center justify-center rounded-lg", scenarioIconColors[scenario.type])}>
                  <Icon className="h-5 w-5" />
                </div>
                <div>
                  <h4 className="text-sm font-medium text-card-foreground">{scenario.name}</h4>
                  <p className="mt-1 text-xs leading-relaxed text-muted-foreground">{scenario.description}</p>
                </div>
                {isSelected && (
                  <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20 text-[10px]">
                    Selected
                  </Badge>
                )}
              </button>
            )
          })}
        </div>
      </div>

      {/* Run Button */}
      <div className="flex items-center gap-4">
        <Button
          onClick={handleRunSimulation}
          disabled={!selectedScenario || isRunning}
          className="bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
        >
          {isRunning ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Running Simulation...
            </>
          ) : (
            <>
              <Play className="mr-2 h-4 w-4" />
              Run Simulation
            </>
          )}
        </Button>
        {isRunning && (
          <div className="flex items-center gap-3">
            <div className="h-2 w-48 overflow-hidden rounded-full bg-secondary">
              <div
                className="h-full rounded-full bg-primary transition-all duration-500 ease-out"
                style={{ width: `${progress}%` }}
              />
            </div>
            <span className="text-xs text-muted-foreground">{completedSteps}/{totalSteps}</span>
          </div>
        )}
        {runComplete && (
          <div className="flex items-center gap-2 text-success">
            <CheckCircle2 className="h-4 w-4" />
            <span className="text-sm font-medium">Simulation complete</span>
          </div>
        )}
      </div>

      {/* Pipeline Visualization */}
      {pipelineSteps.length > 0 && (
        <div>
          <h3 className="mb-3 text-sm font-semibold text-foreground">Step Functions Pipeline</h3>
          <div className="rounded-xl border border-border bg-card p-5">
            <div className="flex flex-col gap-1">
              {pipelineSteps.map((step, i) => (
                <div key={step.id}>
                  <div className={cn(
                    "flex items-center gap-3 rounded-lg px-4 py-3 transition-all duration-300",
                    step.status === "running" && "bg-primary/5 border border-primary/20",
                    step.status === "completed" && "bg-success/5",
                    step.status === "pending" && "opacity-50"
                  )}>
                    <StepIcon status={step.status} />
                    <div className="flex-1">
                      <span className={cn(
                        "text-sm font-medium",
                        step.status === "completed" ? "text-card-foreground" :
                        step.status === "running" ? "text-primary" :
                        "text-muted-foreground"
                      )}>
                        {step.name}
                      </span>
                    </div>
                    {step.duration && (
                      <span className="text-xs text-muted-foreground">{step.duration}ms</span>
                    )}
                    {step.status === "running" && (
                      <Badge variant="outline" className="bg-primary/10 text-primary border-primary/20 text-[10px] animate-pulse">
                        Processing
                      </Badge>
                    )}
                  </div>
                  {i < pipelineSteps.length - 1 && (
                    <div className="ml-[22px] flex h-4 items-center">
                      <div className={cn(
                        "h-full w-px",
                        step.status === "completed" ? "bg-success/50" : "bg-border"
                      )} />
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
