import * as React from "react"
import { cx } from "./util"

// components.json: photo-caption
//
// A photograph without its record does not publish. `event`, `place`, and `date`
// are separate so a missing one is visibly missing rather than quietly dropped.
export interface CaptionProps extends React.HTMLAttributes<HTMLParagraphElement> {
  event?: string
  place?: string
  date?: string
}

export function Caption({ event, place, date, className, children, ...rest }: CaptionProps) {
  const line = [event, place, date].filter(Boolean).join(" · ")
  return (
    <p className={cx("caption", className)} {...rest}>
      {children}
      {line ? (
        <>
          <br />
          <small>{line}</small>
        </>
      ) : null}
    </p>
  )
}
