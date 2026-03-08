import Link from "next/link"
import { LandingHero } from "@/components/landing/hero"
import { LandingFeatures } from "@/components/landing/features"
import { LandingCTA } from "@/components/landing/cta"

export default function LandingPage() {
  // console.info("[page] render /")

  return (
    <div className="relative min-h-screen overflow-hidden bg-background">
      {/* Subtle radial glow */}
      <div
        className="pointer-events-none absolute left-1/2 top-0 -translate-x-1/2"
        aria-hidden="true"
        style={{
          width: "900px",
          height: "600px",
          background:
            "radial-gradient(ellipse at center, rgba(99,102,241,0.12) 0%, transparent 70%)",
        }}
      />

      {/* Top navigation */}
      <header className="relative z-10 mx-auto flex max-w-6xl items-center justify-between px-6 py-5">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <svg
              viewBox="0 0 24 24"
              fill="none"
              className="h-4 w-4 text-primary-foreground"
              aria-hidden="true"
            >
              <path
                d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"
                fill="currentColor"
              />
            </svg>
          </div>
          <span className="text-lg font-semibold tracking-tight text-foreground">
            APE
          </span>
        </div>
        <Link
          href="/dashboard"
          className="rounded-lg border border-border bg-secondary px-4 py-2 text-sm font-medium text-secondary-foreground transition-colors hover:bg-secondary/80"
        >
          Open Dashboard
        </Link>
      </header>

      <main className="relative z-10">
        <LandingHero />
        <LandingFeatures />
        <LandingCTA />
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-border">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
          <p className="text-xs text-muted-foreground">
            Built for AWS Hackathon 2025
          </p>
          <p className="text-xs text-muted-foreground">
            Powered by Step Functions, Bedrock, DynamoDB
          </p>
        </div>
      </footer>
    </div>
  )
}
