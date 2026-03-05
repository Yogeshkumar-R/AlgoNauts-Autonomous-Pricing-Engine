import {
  Brain,
  ShieldCheck,
  Activity,
  Zap,
} from "lucide-react"

const features = [
  {
    icon: Brain,
    title: "AI-Powered Decisions",
    description:
      "Amazon Bedrock analyzes competitor prices, demand signals, and inventory levels to recommend optimal pricing in real-time.",
  },
  {
    icon: ShieldCheck,
    title: "Guardrail Protection",
    description:
      "Deterministic rules enforce margin floors, rate-of-change caps, and competitor bounds before any price goes live.",
  },
  {
    icon: Activity,
    title: "Real-Time Monitoring",
    description:
      "EventBridge ingests market data continuously. Every pricing decision is logged, auditable, and reversible.",
  },
  {
    icon: Zap,
    title: "Step Functions Pipeline",
    description:
      "A fully serverless orchestration pipeline handles ingestion, analysis, decision-making, and deployment in under 3 seconds.",
  },
]

export function LandingFeatures() {
  return (
    <section className="border-t border-border bg-card/50">
      <div className="mx-auto max-w-6xl px-6 py-20">
        <div className="mb-12 text-center">
          <h2 className="text-2xl font-bold tracking-tight text-foreground md:text-3xl">
            How it works
          </h2>
          <p className="mt-3 text-sm text-muted-foreground">
            Four pillars of autonomous pricing, built entirely on AWS
          </p>
        </div>

        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="group rounded-xl border border-border bg-card p-6 transition-all duration-200 hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5"
            >
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
                <feature.icon className="h-5 w-5 text-primary" />
              </div>
              <h3 className="text-sm font-semibold text-foreground">
                {feature.title}
              </h3>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
