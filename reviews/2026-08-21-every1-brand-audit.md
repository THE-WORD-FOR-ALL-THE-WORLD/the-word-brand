# EVERY1 Brand Audit

**August 2026 · Brand v7.4**

What the movement's brand covers today, what it does not, and where vision belongs.

| | |
| --- | --- |
| Date | 21 August 2026 |
| Brand version | v7.4 |
| Audited | `brand.every1movement.com`, the EVERY1 pages on `brand.theword.world`, and the repository at `a17b528` |
| Findings | 6, of which 2 critical |

---

## Resolution

Acted on in **v7.5**, 21 August 2026. This audit stands as written: the findings are the record of
what was true at v7.4, and are not edited to match the fix.

| Finding | State | Where |
| --- | --- | --- |
| F1, messaging document contradicts itself | Fixed | `tools/gen_docs.py`, Section 1 now reads the rule for the door it describes |
| F2, no messaging on the public site | Fixed | `every1/#say`, from `ai-source/every1-messaging.json` |
| F3, vision lockup ships an unreadable promise | Fixed | The vision is published as text, and the footer states the whole line |
| F4, no copy for EVERY1's audience | Fixed | Two audiences recorded, 23 strings added, unknown audiences now fail the build |
| F5, app named but not designed | Fixed | `every1/#app`, 8 screens and 9 rules, from `ai-source/every1-app.json` |
| F6, checker published but unlinked | Fixed | Linked from the command that names it |

Phase 3 of the sequence, the private repository, is not done: it is a decision about where ministry
material lives rather than a defect in this system. Phase 5, the Canva and Figma sync, still stands
open and the linter still warns about it.

---

## Verdict

**The mark system is genuinely strong. Everything downstream of the mark is missing.**

EVERY1 has eight published lockups, three inks each, with clear space and minimum sizes measured
from the artwork rather than guessed, all generated from approved masters and verified in CI. That
is better than most organisations ten times its size manage.

The problem is what a partner does after they download the file. The public site has nine sections.
Every one of them is about the logo, the colour, or the typeface. Not one is about what to say. An
outside organisation running a conference under this mark will get the artwork exactly right and
then write its own copy, its own promise, and its own explanation of what EVERY1 is.

Wrong words on a correct logo does more damage than a stretched logo, and it is far harder to take
back. That is the gap this audit is mostly about.

---

## Coverage

Measured against what a designer, an engineer, or an outside partner can actually find and use
today, without asking anyone.

| Area | State | What exists |
| --- | --- | --- |
| Logos | **Strong** | 8 lockups, 3 inks, clear space and minimum size per mark, SVG and PNG, generated from masters, checked in CI. The 1-as-mask rule is a real signature move and it is written down. |
| Colour and type | **Strong** | Six colours with stated roles and the Flame ceiling. Three faces, all Open Font License, so a partner installs them free. |
| Messaging | **Absent** | Nothing on the public site. A messaging document exists on the portal, marked internal use, and it contradicts itself. See F1 and F2. |
| App design | **Named only** | The app is named as core identity in both the messaging document and the brand guide. One image exists. No screens, no navigation, no flows. See F5. |
| Vision casting | **Mark only** | A vision lockup ships with the verse inside the artwork. The verse is never written in text anywhere a partner can read it. See F3. |

---

## Findings

Six, in the order I would fix them.

### F1. The messaging document contradicts itself on the one rule that defines EVERY1

**Critical**

The document that establishes EVERY1's standing tells a reader to do the exact thing the brand law
exempts it from, and then, seven sections later, tells them not to.

**Evidence.** Section 1, Name and Standing:

> Wherever its name appears, it carries the endorsement line: A ministry of THE WORD FOR ALL THE
> WORLD.

Section 8, On the Record:

> EVERY1 is the one door that stands on its own. On the YouVersion model, it carries no endorsement
> line and no parent lockup.

Source: `tools/gen_docs.py:262` emits the Section 1 sentence unconditionally for every initiative.
`tools/gen_docs.py:322` states EVERY1's exception. Both run for this document.

Anyone reading top down stops at Section 1 and adds the endorsement line, which is precisely what
the standalone site, the separate domain, and the recorded exception all exist to prevent.

**Fix.** Make the Section 1 sentence conditional on the initiative's endorsement rule, reading it
from the same source the Brand Guide reads. One generator change, and the contradiction cannot come
back for a future initiative either.

### F2. The public site is a mark guide presented as a brand guide

**Critical**

Its nine sections are: pick the file for the ground, every published form, six colours, three
faces, the never list, the 1 as a mask, country lockups, check your work, and ask. All craft. No
content.

**Evidence.** The site's own opening states its audience:

> For our team, and for any organisation carrying EVERY1 at a conference, an activation, or on a
> shirt. Everything you need is on this page.

There is no mission line, no voice guidance, no vocabulary, no banned words, and no boilerplate
paragraph a partner could paste into a conference program.

The promise "everything you need is on this page" is not currently true for the audience the page
names. A partner has the files and none of the words.

**Fix.** Add a messaging section: the mission line, the promise, what the movement is, who may join,
the four phrases it carries, how to write as EVERY1, the banned words, and one boilerplate
paragraph. Sections 4, 5 and 7 of the existing messaging document are already written and already
correct. This is mostly a matter of moving approved words to where partners are.

### F3. The vision lockup ships a promise nobody can read

**High**

The most prominent mark in the set is described by its own entry as carrying the whole promise, and
that promise appears nowhere in text.

**Evidence.** The vision lockup's published use:

> The whole promise in one mark: the verse above, the name, and what it leads to below. Banners,
> stage backdrops, and the back of a shirt. Never small.

The verse is inside the artwork as outlines. Neither the public site nor the portal's EVERY1 brand
page states it in text. The footer closes with "Every tribe. Every tongue. Every nation." and never
explains it.

So a partner can put the promise on a stage backdrop but cannot quote it in a program, cannot check
a translation of it, cannot set it in type beside the mark, and cannot tell whether their own
conference copy agrees with it. This is the single strongest argument for putting vision on this
site: you are already shipping vision, as artwork, without the words.

**Fix.** State the verse and the promise in text, next to the lockup that contains them. Treat that
text as a brand fact with a version, like a colour.

### F4. The copy bank has 47 approved strings and none for EVERY1's audience

**High**

**Evidence.** Attributed audiences across all seven sets: The Local Pastor (7), The Hungry Church
Member (6), The Lost Online Searcher (4), The Kingdom Partner (3), The Legacy Leader (1),
unattributed (26).

EVERY1's stated audience, from its own messaging document:

> Every believer. There is no maturity requirement. The movement carries special fire for the young
> and the newly saved.

Those are the parent's audiences, written for pastors and seekers. Not one string is written for an
ordinary believer being sent out, a newly saved teenager, or a partner organisation promoting an
activation. Anyone running an EVERY1 ad or email today writes from scratch, which means the copy
bank does not constrain the surface where volume will actually be highest.

**Fix.** Add EVERY1's audiences to the messaging guide, then add strings against them. Sets and
character limits already exist, so this is content, not engineering.

### F5. The app is central to the identity and absent from the design system

**High**

**Evidence.** The brand guide records the exception as applying "across the movement, the app, and
the activation platform alike," so the app is named as a first-class surface.

What exists: one image, `every1-app-sign-in.png`. The `app` channel spec on the portal is
parent-generic: touch target, app icon, splash, control states. Nothing EVERY1-specific, no screens,
no navigation model, no empty states, and nothing on how the 1-mask behaves in an interface rather
than on a poster.

Whoever builds the app will therefore invent its design, and the app will become the most-seen
expression of this brand. That is the largest uncontrolled surface in the system.

**Fix.** Specify screens rather than commissioning mockups. See the note on app design below: a
mockup is a picture that goes stale, a screen spec built from tokens does not.

### F6. The checker is published but never linked

**Low**

The site tells partners they can verify their own work and shows the command
`python3 brand_check.py poster.html`. The file is genuinely served, at
`brand.every1movement.com/brand_check.py`, and it returns 200. There is no link to it anywhere on
the page, so a partner has to guess the URL.

**Fix.** Link it from the command. One anchor.

---

## Your actual question

**Yes, put vision here. A specific slice of it.**

Your instinct is right, and the split you proposed is close. I would move the line, though: the
useful boundary is not vision versus brand. Vision splits down the middle, and the half that belongs
on this site is the half a partner has to repeat.

> ### The test
>
> **Would someone carrying this mark at their own conference need to say this out loud?**
>
> If yes, it is **public vision** and it belongs on `brand.every1movement.com`, because they will say
> something in that slot whether you wrote it or not.
>
> If no, it is **internal direction** and it belongs in the private project, because it is yours to
> decide and nobody downstream needs it to do their job.

Vision casting content, the why, the promise, the invitation, is exactly what an outside organisation
repeats from a stage. Vision setting, where the movement is going, how it gets there, and what it
measures, is not. Finding F3 is what happens when you ship the first kind as artwork but keep the
words in the second bucket.

### Public

On `brand.every1movement.com`:

- The verse the vision lockup already contains, in text
- The mission line, in one sentence
- The promise: EVERY1 in the church going to EVERY1 outside the church
- What the movement is, and who may join
- The four phrases it carries
- The first three steps
- Voice: how to write as EVERY1, and the banned words
- One boilerplate paragraph for a program or a press note
- Everything already on the site: marks, colour, type, the never list, the mask

### Private

In a separate private repository:

- Overall ministry identity and how the three movements relate
- Direction, targets, and growth plans
- The prophecy's internal reading and teaching notes
- Processes, approvals, staffing, finance
- Partner vetting: who may carry the mark, and how that is decided
- Anything unapproved or still in draft

### Two places, not three

You said the goal is one place to look for everything. Keep that, with one exception, and be strict
about the exception. Public EVERY1 material goes on the site you just launched. Private ministry
material goes in a private repository. Nothing goes in a third place.

Make the private one a separate repository, not a private folder inside this one. This repository
deploys publicly on every push to main, so an unpublished directory is one build-glob mistake away
from being a disclosure. A separate repository makes that class of accident impossible rather than
unlikely. Use the same toolchain, the same generators, and the same linter, so the discipline carries
over.

One more argument for putting public vision in this repository rather than the private one: the
mechanism already exists. Every fact on the EVERY1 site is generated from `ai-source/` plus the
guides, and the linter fails when a page disagrees with its source. Adding messaging is adding a
source file. Splitting the public promise into a second private project means the words partners read
and the words you approve can drift, with nothing checking across the boundary.

---

## App design

**Specify screens. Do not commission mockups.**

Include the app here, and make it a real part of the system rather than a gallery. Mockups are the
wrong artifact for a brand portal: a picture of a screen is correct on the day it is exported and
silently wrong after the next token change, and nothing in the build can tell. That is the same class
of failure this repository has been fixing all along, where a page looks fine and disagrees with the
standard it claims to come from.

What to publish instead, in order of value:

1. **A screen inventory.** Name every screen the app has: sign in, home, share Jesus, log a
   conversation, prayer meeting, course, profile, invite. Naming them is most of the design decision,
   and it is cheap.
2. **A spec per screen**, in the same shape as the existing channel specs: purpose, the one action,
   which marks may appear, which colours, what the empty state says, and what the error says.
   Generated, so it moves when tokens move.
3. **Live component examples** rendered from the real stylesheet, the way the components page already
   works. A partner sees the actual button, not a picture of one.
4. **Then** two or three flat mockups, clearly dated and labelled illustrative, for the pitch
   conversations where a picture genuinely helps.

The 1-mask needs its own interface rule while you are here. On a poster it is one per view. In an app,
a scrolling feed will put six on screen unless something forbids it, and that turns a signature move
into wallpaper.

---

## Sequence

### Phase 1, correctness

**Stop the system contradicting itself.** F1 and F6. Both are small and both are defects rather than
judgement calls. F1 is the one that matters: while it stands, the document defining EVERY1's
independence instructs people to undo it.

### Phase 2, words

**Give partners something to say.**

- State the verse and the promise in text, beside the lockup that carries them (F3)
- Add the messaging section to the public site, drawn from the approved document (F2)
- Add EVERY1's audiences and their strings to the copy bank (F4)

This is the highest-value work in the audit and most of the content is already written and already
approved. It mainly needs moving and a source file.

### Phase 3, boundary

**Stand up the private repository.** Same toolchain, no deploy. Move internal direction into it as it
gets written, and apply the out-loud test at the boundary each time. Doing this before much internal
material exists is far easier than sorting it later.

### Phase 4, surface

**Specify the app.** Screen inventory first, then specs, then live examples. Add the 1-mask interface
rule. Leave mockups last and label them.

### Phase 5, coverage

**Close the remaining gaps.** Publish the country queue so partners can see what is drawn and what is
coming. Sync Canva and Figma, which the linter has been warning about for four versions.

---

## One thing worth saying plainly

The reason this audit reads as harsh on messaging and generous on craft is that the craft here is
genuinely unusual. Measured clear space, generated marks, CI that refuses to deploy a page
disagreeing with its own standard: most organisations never get there.

That is exactly why the messaging gap is worth fixing now. The machinery to hold words to the same
standard as colours already exists and is already running. Right now it is holding nothing about what
EVERY1 says, on the one site built for people who will say it on your behalf.

---

Findings verified against the live sites and the repository at commit `a17b528`, brand v7.4, on
21 August 2026. Quotations are taken verbatim from the published pages and the generators named.
