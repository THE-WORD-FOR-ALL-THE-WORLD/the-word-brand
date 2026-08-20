import * as React from "react"
import { cx } from "./util"

// components.json: eyebrow
// Law II: every record opens with one.
export interface EyebrowProps extends React.HTMLAttributes<HTMLSpanElement> {}

export function Eyebrow({ className, children, ...rest }: EyebrowProps) {
  return (
    <span className={cx("eyebrow", className)} {...rest}>
      {children}
    </span>
  )
}
