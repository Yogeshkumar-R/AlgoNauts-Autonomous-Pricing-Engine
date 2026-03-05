"use client"

import { SimulationControl } from "@/components/simulation/simulation-control"

export default function SimulationPage() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-6 lg:px-8">
      <div className="mb-6">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">Simulation Control</h1>
        <p className="text-sm text-muted-foreground">
          Trigger pricing scenarios and observe the Step Functions pipeline in real-time
        </p>
      </div>
      <SimulationControl />
    </div>
  )
}
