import Link from "next/link"
import { ArrowRight } from "lucide-react"

export function LandingHero() {
  return (
    <section className="mx-auto max-w-6xl px-6 pb-20 pt-16 text-center md:pt-24 lg:pt-32">
      {/* Eyebrow badge */}
      <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5">
        <span className="h-1.5 w-1.5 rounded-full bg-success" />
        <span className="text-xs font-medium tracking-wide text-primary">
          Autonomous Pricing Engine
        </span>
      </div>

      <h1 className="mx-auto max-w-3xl text-balance text-4xl font-bold leading-tight tracking-tight text-foreground md:text-5xl lg:text-6xl">
        AI that prices your products{" "}
        <span className="text-primary">while you sleep</span>
      </h1>

      <p className="mx-auto mt-5 max-w-xl text-pretty text-base leading-relaxed text-muted-foreground md:text-lg">
        APE uses AWS Step Functions and Amazon Bedrock to continuously
        monitor competitors, adjust margins, and protect your profit --
        fully autonomously.
      </p>

      <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
        <Link
          href="/dashboard"
          className="group inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/25 transition-all hover:bg-primary/90 hover:shadow-primary/40"
        >
          Enter Dashboard
          <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
        </Link>
        <Link
          href="/dashboard/simulation"
          className="inline-flex items-center gap-2 rounded-lg border border-border px-6 py-3 text-sm font-medium text-secondary-foreground transition-colors hover:bg-secondary"
        >
          Run a Simulation
        </Link>
      </div>

      {/* Stats row */}
      <div className="mx-auto mt-16 grid max-w-2xl grid-cols-3 gap-8 border-t border-border pt-10">
        {[
          { value: "342", label: "Products Monitored" },
          { value: "94%", label: "AI Confidence" },
          { value: "23%", label: "Avg Margin" },
        ].map((stat) => (
          <div key={stat.label} className="flex flex-col items-center">
            <span className="text-2xl font-bold text-foreground md:text-3xl">
              {stat.value}
            </span>
            <span className="mt-1 text-xs text-muted-foreground">
              {stat.label}
            </span>
          </div>
        ))}
      </div>
    </section>
  )
}
