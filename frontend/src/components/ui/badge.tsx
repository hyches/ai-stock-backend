
import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"

import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-md px-2 py-1 text-xs font-medium ring-1 ring-inset",
  {
    variants: {
      variant: {
        default:
          "bg-primary/10 text-primary ring-primary/20",
        secondary:
          "bg-secondary/10 text-secondary-foreground ring-secondary/20",
        destructive:
          "bg-destructive/10 text-destructive ring-destructive/20",
        outline:
          "text-foreground ring-border",
        success:
          "bg-green-500/10 text-green-500 ring-green-500/20",
        warning:
          "bg-yellow-500/10 text-yellow-500 ring-yellow-500/20",
        info:
          "bg-blue-500/10 text-blue-500 ring-blue-500/20",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
