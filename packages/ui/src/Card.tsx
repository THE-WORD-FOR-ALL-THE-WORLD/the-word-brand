import * as React from "react"
import { cx } from "./util"

// components.json: card
// Cards sit on Parchment. On a dark band the whole band inverts, not the card.
export interface CardProps extends React.HTMLAttributes<HTMLElement> {
  href?: string
}

export function Card({ href, className, children, ...rest }: CardProps) {
  const cls = cx("card", className)
  if (href) {
    return (
      <a href={href} className={cls} {...(rest as object)}>
        {children}
      </a>
    )
  }
  return (
    <div className={cls} {...rest}>
      {children}
    </div>
  )
}
