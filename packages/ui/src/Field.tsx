import * as React from "react"
import { cx } from "./util"

// components.json: form-field
//
// An error names what is wrong and how to fix it. It is wired to the input with
// aria-describedby, because colour alone never carries the message.
export interface FieldProps {
  id: string
  label: string
  hint?: string
  error?: string
  warning?: string
  children?: React.ReactNode
  className?: string
}

export function Field({ id, label, hint, error, warning, children, className }: FieldProps) {
  const state = error ? "error" : warning ? "warning" : undefined
  const describedBy = error ? `${id}-error` : hint ? `${id}-hint` : undefined
  return (
    <div className={cx("field", className)} data-state={state}>
      <label htmlFor={id}>{label}</label>
      {React.isValidElement(children)
        ? React.cloneElement(children as React.ReactElement<Record<string, unknown>>, {
            id,
            "aria-describedby": describedBy,
            "aria-invalid": error ? true : undefined,
          })
        : children}
      {hint && !error ? (
        <p className="hint" id={`${id}-hint`}>
          {hint}
        </p>
      ) : null}
      {error ? (
        <p className="error" id={`${id}-error`}>
          {error}
        </p>
      ) : null}
    </div>
  )
}
