"use client"

import { SWRConfig } from "swr"
import type { ReactNode } from "react"

export function Providers({ children }: { children: ReactNode }) {
  return (
    <SWRConfig
      value={{
        revalidateOnFocus: true,
        dedupingInterval: 5000,
      }}
    >
      {children}
    </SWRConfig>
  )
}
