import * as React from "react"
import { cx } from "./util"

// components.json: stat-figure
//
// Flame's one job at size. `source` is required by the guide: a figure without
// the record it came from is a figure somebody remembered.
export interface StatProps extends React.HTMLAttributes<HTMLDivElement> {
  figure: string
  label: string
  source: string
}

export function Stat({ figure, label, source, className, ...rest }: StatProps) {
  return (
    <div className={cx("stat", className)} {...rest}>
      <div className="fig">{figure}</div>
      <div className="lab">{label}</div>
      <div className="source">{source}</div>
    </div>
  )
}
