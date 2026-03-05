"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  Package,
  MessageSquare,
  ScrollText,
  FlaskConical,
} from "lucide-react"
import { cn } from "@/lib/utils"

const navItems = [
  { href: "/dashboard", label: "Home", icon: LayoutDashboard },
  { href: "/products", label: "Products", icon: Package },
  { href: "/ai-chat", label: "AI", icon: MessageSquare },
  { href: "/decisions", label: "Logs", icon: ScrollText },
  { href: "/simulation", label: "Simulate", icon: FlaskConical },
]

export function MobileNav() {
  const pathname = usePathname()

  return (
    <nav className="fixed inset-x-0 bottom-0 z-50 flex items-center justify-around border-t border-border bg-sidebar/95 px-2 py-2 backdrop-blur-lg md:hidden">
      {navItems.map((item) => {
        const isActive = pathname === item.href
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex flex-col items-center gap-0.5 rounded-lg px-3 py-1.5 text-xs transition-colors",
              isActive ? "text-primary" : "text-muted-foreground"
            )}
          >
            <item.icon className="h-5 w-5" />
            <span>{item.label}</span>
          </Link>
        )
      })}
    </nav>
  )
}
