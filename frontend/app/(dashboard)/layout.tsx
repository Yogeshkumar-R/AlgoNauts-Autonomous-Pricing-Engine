import { AppSidebar } from "@/components/app-sidebar"
import { MobileNav } from "@/components/mobile-nav"
import { Providers } from "@/components/providers"

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <Providers>
      <div className="flex h-screen overflow-hidden">
        <div className="hidden md:flex">
          <AppSidebar />
        </div>
        <main className="flex-1 overflow-auto pb-16 md:pb-0">
          {children}
        </main>
        <MobileNav />
      </div>
    </Providers>
  )
}
