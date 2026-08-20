import * as React from "react"
import { cx } from "./util"

// components.json: button-primary, button-ghost
//
// There is no Flame variant and there must never be one. Flame under a white
// label is 3.3:1 and fails AA, which is why Ember exists. See gate G4.
export type ButtonVariant = "primary" | "ghost"

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  /** Render as an anchor. A button that navigates is a link. */
  href?: string
}

export const Button = React.forwardRef<HTMLButtonElement & HTMLAnchorElement, ButtonProps>(
  function Button({ variant = "primary", href, className, children, ...rest }, ref) {
    const cls = cx("btn", variant === "ghost" && "ghost", className)
    if (href) {
      return (
        <a ref={ref} href={href} className={cls} {...(rest as object)}>
          {children}
        </a>
      )
    }
    return (
      <button ref={ref} className={cls} {...rest}>
        {children}
      </button>
    )
  },
)
