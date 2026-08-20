// @theword/ui
//
// The React implementation of the components specified at
// https://brand.theword.world/ai/components.json
//
// This package is a CONSUMER of the brand system, never a source. When this
// disagrees with components.json, components.json is right and this is a bug.
// Component names match the ids there, the Figma layer names, and the Storybook
// stories, so a Card is a Card wherever anyone looks it up.

export { Button } from "./Button"
export type { ButtonProps, ButtonVariant } from "./Button"

export { Eyebrow } from "./Eyebrow"
export type { EyebrowProps } from "./Eyebrow"

export { Headline, Title } from "./Headline"
export type { HeadlineProps, HeadlineSize } from "./Headline"

export { Card } from "./Card"
export type { CardProps } from "./Card"

export { Caption } from "./Caption"
export type { CaptionProps } from "./Caption"

export { Stat } from "./Stat"
export type { StatProps } from "./Stat"

export { Field } from "./Field"
export type { FieldProps } from "./Field"

export { Record, Endorsement } from "./Record"
export type { RecordProps } from "./Record"

export { Footage, LowerThird } from "./Footage"
export type { FootageProps, LowerThirdProps } from "./Footage"

export { TableScroll } from "./Table"

export { cx } from "./util"
export type { Ground } from "./util"
