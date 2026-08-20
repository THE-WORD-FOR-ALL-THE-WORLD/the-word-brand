import * as React from "react"
import { cx } from "./util"

// components.json: hero-video, lower-third
//
// The scrim is not optional and is rendered here rather than left to the caller,
// because type on footage without it is gate G5. `poster` is required: the still
// is what shows under a reduced-motion preference and on a slow connection.
export interface FootageProps extends React.HTMLAttributes<HTMLDivElement> {
  src: string
  poster: string
  alt?: string
}

export function Footage({ src, poster, alt, className, children, ...rest }: FootageProps) {
  return (
    <div className={cx("footage", className)} {...rest}>
      <video autoPlay muted loop playsInline poster={poster} aria-label={alt}>
        <source src={src} type="video/mp4" />
      </video>
      <div className="scrim" />
      <div className="inner">{children}</div>
    </div>
  )
}

export interface LowerThirdProps extends React.HTMLAttributes<HTMLDivElement> {
  name: string
  role: string
}

export function LowerThird({ name, role, className, ...rest }: LowerThirdProps) {
  return (
    <div className={cx("lower-third", className)} {...rest}>
      <div className="name">{name}</div>
      <div className="role">{role}</div>
    </div>
  )
}
