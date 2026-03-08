"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import {
  LayoutDashboard,
  Package,
  MessageSquare,
  ScrollText,
  FlaskConical,
  Zap,
  ChevronLeft,
  ChevronRight,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { useEffect, useState } from "react"
import { fetchConversations } from "@/lib/api"

type Conversation = {
  id: string
  title: string
  lastMessage?: string
  messageCount?: number
}

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/products", label: "Products", icon: Package },
  { href: "/ai-chat", label: "PRIME", icon: MessageSquare },
  { href: "/simulation", label: "Simulation", icon: FlaskConical },
  { href: "/decisions", label: "Decision Log", icon: ScrollText }
]

export function AppSidebar() {
  const pathname = usePathname()
  const [collapsed, setCollapsed] = useState(false)
  const [conversations, setConversations] = useState<Conversation[]>([])

  useEffect(() => {
    if (!pathname?.startsWith("/ai-chat")) return

    async function load() {
      try {
        const res = await fetchConversations()
        if (res?.conversations) {
          setConversations(res.conversations)
        }
      } catch (err) {
        // console.error("Failed to load conversations", err)
      }
    }

    load()
  }, [pathname])

  return (
    <aside
      className={cn(
        "flex flex-col border-r border-border bg-sidebar transition-all duration-300",
        collapsed ? "w-16" : "w-60"
      )}
    >
      {/* Logo */}

      <div className={cn("flex items-center border-b border-border p-4", collapsed ? "justify-center" : "gap-3")}>
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
          <Zap className="h-4 w-4 text-primary-foreground" />
        </div>

        {!collapsed && (
          <div className="flex flex-col">
            <span className="text-sm font-semibold text-sidebar-foreground">APE</span>
            <span className="text-xs text-muted-foreground">AI Pricing</span>
          </div>
        )}
      </div>

      {/* Navigation */}

      <nav className="flex flex-1 flex-col gap-1 p-3">
        {navItems.map((item) => {
          const isActive =
            item.href === "/dashboard"
              ? pathname === "/dashboard"
              : pathname.startsWith(item.href)

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group flex items-center rounded-lg px-3 py-2.5 text-sm font-medium",
                collapsed ? "justify-center" : "gap-3",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-secondary hover:text-sidebar-foreground"
              )}
            >
              <item.icon className="h-4 w-4 shrink-0" />
              {!collapsed && <span>{item.label}</span>}
            </Link>
          )
        })}

        {/* Conversations */}

        {pathname?.startsWith("/ai-chat") && (
          <>
            <div className="my-2 border-t border-border" />

            {!collapsed && (
              <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground">
                Conversations
              </div>
            )}

            {conversations.map((conv) => (
              <Link
                key={conv.id}
                href={`/ai-chat?conversation=${conv.id}`}
                className={cn(
                  "group flex items-center rounded-lg px-3 py-2 text-sm",
                  collapsed ? "justify-center" : "gap-3",
                  "text-muted-foreground hover:bg-secondary hover:text-sidebar-foreground"
                )}
              >
                <MessageSquare className="h-4 w-4 shrink-0" />
                {!collapsed && <span className="truncate">{conv.title || "Conversation"}</span>}
              </Link>
            ))}

            {!conversations.length && !collapsed && (
              <div className="px-3 py-2 text-xs text-muted-foreground">
                No conversations yet
              </div>
            )}
          </>
        )}
      </nav>

      {/* Collapse button */}

      <div className="border-t border-border p-3">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="flex w-full items-center justify-center rounded-lg px-3 py-2 text-sm text-muted-foreground hover:bg-secondary hover:text-sidebar-foreground"
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
          {!collapsed && <span className="ml-2">Collapse</span>}
        </button>
      </div>
    </aside>
  )
}