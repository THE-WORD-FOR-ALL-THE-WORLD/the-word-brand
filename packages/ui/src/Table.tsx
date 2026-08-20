import * as React from "react"
import { cx } from "./util"

// components.json: data-table
// The table scrolls inside its own frame. The page body never scrolls sideways.
export function TableScroll({ className, children, ...rest }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cx("table-scroll", className)} {...rest}>
      <table>{children}</table>
    </div>
  )
}
