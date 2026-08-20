import * as React from "react"
import { cx } from "./util"

// components.json: record-document, endorsement-line
//
// Never decorated. A dateline closes it, and a signature is scanned ink: the
// `signature` prop takes an image source, never a script font.
export interface RecordProps extends React.HTMLAttributes<HTMLElement> {
  kicker: string
  dateline: string
  signature?: { src: string; alt: string }
}

export function Record({ kicker, dateline, signature, className, children, ...rest }: RecordProps) {
  return (
    <article className={cx("record", className)} {...rest}>
      <span className="eyebrow">{kicker}</span>
      <div className="verse">{children}</div>
      <div className="dateline">{dateline}</div>
      {signature ? (
        <div className="signature">
          <img src={signature.src} alt={signature.alt} />
        </div>
      ) : null}
    </article>
  )
}

// Law III: required wherever an initiative's name appears.
export function Endorsement({ className, ...rest }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={cx("endorse", className)} {...rest}>
      A ministry of THE WORD FOR ALL THE WORLD
    </div>
  )
}
