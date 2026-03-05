import Link from "next/link"
import { ArrowRight } from "lucide-react"

export function LandingCTA() {
  return (
    <section className="mx-auto max-w-6xl px-6 py-20">
      <div className="relative overflow-hidden rounded-2xl border border-primary/20 bg-gradient-to-br from-primary/10 via-card to-card p-10 text-center md:p-16">
        {/* Subtle glow */}
        <div
          className="pointer-events-none absolute -right-20 -top-20 h-60 w-60 rounded-full opacity-30"
          style={{ background: "radial-gradient(circle, var(--primary) 0%, transparent 70%)" }}
          aria-hidden="true"
        />

        <h2 className="relative text-balance text-2xl font-bold tracking-tight text-foreground md:text-3xl">
          See the pricing engine in action
        </h2>
        <p className="relative mx-auto mt-3 max-w-md text-sm leading-relaxed text-muted-foreground">
          Trigger a competitor price-drop simulation and watch the
          Step Functions pipeline analyze, decide, and apply new prices in
          real-time.
        </p>

        <div className="relative mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <Link
            href="/dashboard"
            className="group inline-flex items-center gap-2 rounded-lg bg-primary px-6 py-3 text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/25 transition-all hover:bg-primary/90 hover:shadow-primary/40"
          >
            Open Dashboard
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
          </Link>
          <Link
            href="/dashboard/ai-chat"
            className="inline-flex items-center gap-2 rounded-lg border border-border px-6 py-3 text-sm font-medium text-secondary-foreground transition-colors hover:bg-secondary"
          >
            Chat with AI Advisor
          </Link>
        </div>
      </div>
    </section>
  )
}
