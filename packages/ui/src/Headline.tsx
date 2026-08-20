import * as React from "react"
import { cx } from "./util"

// components.json: headline-serif
//
// The serif has Regular and Italic and no bold cut. `size` goes up rather than
// weight going up, which is why there is no weight prop.
export type HeadlineSize = "small" | "default" | "large"

export interface HeadlineProps extends React.HTMLAttributes<HTMLHeadingElement> {
  size?: HeadlineSize
  as?: "h1" | "h2" | "h3"
}

export function Headline({ size = "default", as: Tag = "h2", className, children, ...rest }: HeadlineProps) {
  return (
    <Tag
      className={cx("headline", size === "small" && "headline-small", size === "large" && "headline-large", className)}
      {...rest}
    >
      {children}
    </Tag>
  )
}

// components.json: the serif band between 22px and 36px.
export function Title({ className, children, ...rest }: React.HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3 className={cx("title", className)} {...rest}>
      {children}
    </h3>
  )
}
