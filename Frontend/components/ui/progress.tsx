"use client"

import * as ProgressPrimitive from "@radix-ui/react-progress"
import * as React from "react"

import { cn } from "@/lib/utils"

type ProgressColor = "primary" | "green" | "yellow" | "red"

interface ProgressProps extends React.ComponentProps<typeof ProgressPrimitive.Root> {
  value?: number
  color?: ProgressColor
}

function Progress({
  className,
  value,
  color = "primary",
  ...props
}: ProgressProps) {
  const trackColorByVariant: Record<ProgressColor, string> = {
    primary: "bg-primary/20",
    green: "bg-emerald-500/20",
    yellow: "bg-amber-500/20",
    red: "bg-rose-500/20",
  }

  const barColorByVariant: Record<ProgressColor, string> = {
    primary: "bg-primary",
    green: "bg-emerald-500",
    yellow: "bg-amber-500",
    red: "bg-rose-500",
  }

  return (
    <ProgressPrimitive.Root
      data-slot="progress"
      className={cn(
        `${trackColorByVariant[color]} relative h-2 w-full overflow-hidden rounded-full`,
        className
      )}
      {...props}
    >
      <ProgressPrimitive.Indicator
        data-slot="progress-indicator"
        className={`${barColorByVariant[color]} h-full w-full flex-1 transition-all`}
        style={{ transform: `translateX(-${100 - (value || 0)}%)` }}
      />
    </ProgressPrimitive.Root>
  )
}

export { Progress }

