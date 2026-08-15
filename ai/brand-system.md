# THE WORD FOR ALL THE WORLD: Brand System

> **Brand system v5.2 · Messaging guide v1.0 · Updated 2026-08-15**
> Canonical source: <https://brand.theword.world/ai/manifest.json>
> The complete standard, assembled for machine reading. The human guides are at <https://brand.theword.world/brand> and <https://brand.theword.world/brand/messaging>.

This document is authoritative. Where any older deck, site, PDF, or remembered rule conflicts with it, this document wins. It governs work for THE WORD FOR ALL THE WORLD and for its three initiatives: Revival To My City, the EVERY1 Movement, and the School of the Local Church.

Issued August 2026. Applies to theword.world, RTMC, EVERY1, SLC.

Governance: this system changes one way. A proposed edit in writing, approval by Joel Zimmer and Nathan Zimmer, a version bump, and a changelog entry. No silent edits.

---

## 1. What this brand is

**An established institution with a burning message.**

The whole identity is two layers held in tension. When in doubt: the institution stays quiet, and the content burns.

Two layers held in tension. **The institution** is the parent, THE WORD FOR ALL THE WORLD: deep navy, warm paper, serif headlines, dated documents, signatures. It speaks for the record, the prophecy, the official numbers, and the donor relationship. **The movement** is CLEAN, BURN, and TRAIN: bold sans, Flame, real footage. Revival To My City, EVERY1, and the School of the Local Church speak here, for events, activation, testimonies, and the field.

**Boundary.** We never use governmental iconography. No seals, no flags, no eagles. We carry authority; we do not imitate office.

## 2. The foundation

**The public mission line, used everywhere:**

> Strengthening the local church to fulfill the Great Commission, until EVERY1 knows the name Jesus.

**Purpose.** To build a real relationship with Jesus. To please God, walk with Jesus, and minister to Him.

**Mission.** To strengthen the local church to do the Great Commission. Fire starts fire. We burn for Jesus in locations across the world, and they catch it, because they're dry enough.

**Vision.** Every tribe, every tongue, every nation, and EVERY1, will know the name Jesus. (Hebrews 8:11)

**The rally cry.** EVERY1 Will Know The Name Jesus.

**The lead narrative.** Every generation seeks a revival. No one told them it is already here. Revival is not a hope we are waiting on. It is a fact we are announcing. All messaging flows downstream of this posture.

### The prophecy

Received before the ministry had a name for what it would become. It is quoted exactly, in full, or not at all. Never paraphrased, never excerpted for effect.

> As tensions grow between man and foe, the light of THE WORD is needed. No peace they'll find, they'll react in kind, until THE WORD is heeded. But great peace have they that love God's Law, and in that Word their reflections saw — and went forth knowing the enemy is defeated.
>
> Received December 2019

## 3. The six laws

These rules help govern how THE WORD looks, sounds, and carries authority everywhere we appear. Everything we produce is tested against these rules.

### Law I. Few words, spoken as commands.

We organize everything around a tiny set of imperative declarations. Our three are fixed: CLEAN · BURN · TRAIN. Big statements are short; short statements are big.

- Never more than three to five priorities on any page or deck. If everything is featured, nothing is.
- Priority words sit over full-bleed footage, one bold word per panel, mission line beneath.
- Each priority links to its own named page. A priority without a destination is decoration.

### Law II. Everything is a record.

We publish documents, not posts. Field reports, impact reports, devotionals, the prophecy: each carries the marks of a record: a kicker, a dateline, and only official facts.

- Every record opens with a letterspaced kicker and closes with a dateline (what · where · when).
- Statistics come from the official ministry record only, never estimates, never memory (per the Minister Agreement).
- The record register uses Parchment, hairline rules, and DM Serif Text. It is never decorated.

### Law III. One house, named front doors.

Revival To My City, EVERY1, and School of the Local Church live as named pages under theword.world, never as scattered websites. The house lends them weight; they lend the house fire.

- Every sub-brand carries the endorsement line: "A ministry of THE WORD FOR ALL THE WORLD."
- Vanity domains (revivaltmc.com) redirect into their page. They never become separate homes.
- One recorded exception: the future EVERY1 app (YouVersion model, §09).

### Law IV. The institution signs its work.

Authority is anchored in named people. Vision statements close with real handwritten signatures. Reports name who filed them. The institution speaks first; a person is its voice.

- The About page vision statement always closes with Joel's and Nathan's actual signatures.
- Testimonies, field reports, and teachings carry a name. Nothing important is anonymous.
- Signatures are scanned ink, never a script font pretending to be ink.

### Law V. A formal frame around burning content.

Composition is centered, spacious, and disciplined: navy and paper grounds, letterspaced labels, sentence-case serif headlines, hairline rules. The formality is the frame; the footage, the fire, and the testimony are the picture.

- Flame never exceeds a tenth of any composition and never carries text (§03).
- Serif headlines are sentence case with at most one italic word; all-caps belongs to the wordmark and labels.
- Generous whitespace is mandatory. Crowding reads as hype, and we are never hype.

### Law VI. Real over staged. Always.

Our homepage already says it: Real People, Real Fire, & Real Change. Every image and every frame of video is documentary, from our conferences, our crusades, our streets. Nothing stock, nothing staged, nothing borrowed.

- No stock photography or stock footage, ever. An empty slot is better than a borrowed moment.
- Every person is shown with dignity, as a co-laborer, never an object of pity (§06).
- Raw beats polished: honest capture over produced perfection, per the ministry's own voice rules.

## 4. Color

Five colors that do one job together. Midnight holds the room and carries the institution. Word Blue supports it where a second structural voice is needed. Parchment is the ground everything rests on, so the page reads as paper rather than screen. Flame is the fire, used sparingly enough that it still means something. Ember is that same fire brought down to text size, where it has to stay readable.

| Token | Name | Hex | Role |
| --- | --- | --- | --- |
| midnight | Midnight | #0B1A2D | Primary ground. Heroes, bands, footers. |
| word-blue | Word Blue | #023D6F | Structural secondary. Logo continuity. |
| parchment | Parchment | #F7F3EC | Light ground. Official paper, never gray. |
| flame | Flame | #F85842 | Non-text accent: BURN moments, display numerals, highlights. Never carries text. ≤10%. |
| ember | Ember | #C13A24 | Fire at text size: primary buttons, links, labels, hovers. |
| white | White | #FFFFFF | Cards, reversed text, button labels. |

**Proportion, 60 / 30 / 10.** Parchment about 60 percent, Midnight about 30 percent, Flame a tenth or less. If Flame covers more than a tenth of a layout, the institution disappears and the design reads as a startup.

## 5. System tokens and states

These are the named values to build with. Every one is a design token: a decision made once here and referenced everywhere else by name, so nobody re-picks it per project. The machine-readable copy is published at /ai/tokens.json.

| Token | Value | Rule |
| --- | --- | --- |
| Button hover | #A62F1B | Ember deepened ~10%. State-only. Never a palette color. |
| Focus ring | 2px Ember (Flame on dark), 3px offset | Visible on every interactive element. Never removed. |
| Success state | #5FAD56 | Forms and dashboards only. Never in brand layouts. |
| Photo/video scrim | Midnight gradient, ~70% at text | Required under any text on imagery (§07). |
| Corner radius | 3px buttons · 4px cards · 6px frames | Three steps, no others. |
| Muted text | 80% Midnight (light grounds) · 75% Parchment (dark) | Captions and metadata. Nothing lighter. It fails contrast. |
| Breakpoint | 720px | Single-column below; grids above. |

## 6. Typography

DM Serif and DM Sans were drawn as companions on shared proportions. That is why the page reads as one smooth rhythm. All free on Google Fonts, for every volunteer, partner, and field team.

- **DM Serif Display.** Large headlines, 36px and up. Fine, engraved hairlines. Regular + Italic only. No bold exists.
- **DM Serif Text.** Serif moments from 22–36px: pull quotes, the prophecy, document headings. Regular + Italic only.
- **DM Sans.** Everything functional: body, nav, labels, buttons, sub-brand materials. Weights 400–700 with true italics.

Stacks as the site renders them:

- Serif display: `'DM Serif Display', Georgia, 'Times New Roman', serif`
- Serif text: `'DM Serif Text', Georgia, 'Times New Roman', serif`
- Sans: `'DM Sans', -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif`

Three faces, and no others. All three come from Google Fonts, so every volunteer, partner, and field team can install them free. Where they cannot load, the fallbacks are Georgia for the serifs and the system sans for DM Sans. Proxima Nova is retired and is not used again.

## 7. Logo

**The wordmark stays.** The wordmark is fixed and is not redrawn. It sits beside DM Sans as family, because both are built on the same geometry, and its letterspaced sub-line already matches the eyebrow style used throughout this guide. The serif never enters the lockup. Inside the wordmark zone, the mark owns all-caps.

## 8. Photography and video

Law VI applied. Our imagery is documentary evidence of what God is doing, captured in our conferences, our crusades, and our streets. It is treated like the record it is.

### Photography

- **Documentary only.** Real moments from real ministry. No stock photography, ever. An empty slot is better than a borrowed moment.
- **Dignity is non-negotiable.** Every subject, especially in Uganda and especially children, is portrayed as a co-laborer in the gospel, never an object of pity. No poverty-framing, no exploitation of need. Consent before capture; official media use follows the Minister Agreement.
- **Every photo is a record.** Published photography carries a caption in the record register: what happened, place, and date. Names when known and permitted.
- **Honest color.** Natural grading. No heavy filters, no HDR drama, no artificial warmth. The moment carries the drama.
- **Text needs a scrim.** Type over imagery sits on the Midnight scrim (~70% at the text). White or Parchment text only. Never Flame or Ember text over photography. Logo per §06.

### Video

- **Footage is the fire.** Full-bleed motion belongs in heroes and priority panels: muted, looping, roughly 6–15 seconds, cut from real field footage.
- **Captions, always.** Every spoken word is subtitled in DM Sans 500 or heavier, on the Midnight scrim bar. Most viewers watch with sound off; captions are also an accessibility requirement.
- **Still fallback, always.** Every loop ships with a still frame honored under prefers-reduced-motion and on slow connections.
- **Lower thirds in the system.** Name and role in DM Sans, letterspaced caps, on the scrim bar, with an optional Flame tick. Nothing animated or bouncing.
- **Raw beats polished.** Honest capture is on-brand, a Wednesday-worship phone recording included. Over-produced hype editing, dramatic sound design, and manufactured urgency are not. We are never hype.

### Field capture standards

- **Shoot every key moment twice** once vertical for Reels/Stories, once horizontal (16:9) for the website, priority panels, and YouTube. The web starves without wide frames.
- **Consent is announced and logged.** Hosts announce photography at the start of every session; anyone captured individually (testimonies, portraits) gives explicit permission. One line in the event run-sheet, every event.
- **Caption at capture, not from memory.** Rename files the same day as YYYY-MM-DD_place_event_## and keep a one-line log: what happened, where, when, who shot it. No photo publishes without its record.
- **Sweep the stage edges before sessions.** Cables, wedges, and water bottles out of the frame line. Tidying is not staging.
- **Own the golden hour.** Midday under cream canvas runs flat and blown; assign someone to shoot the last 30 minutes of daylight and the evening sessions, every event.
- **Fill the missing shots:** prayer and ministry moments up close · a Bible passing from one hand to another · testimony portraits · exteriors that establish place · details (open Bible and pen, the offering basket).

Bracketed caption fields are pending verification against the ministry record. Law II applies to captions too.

Both clips above are the ministry's own footage from the July 2026 conferences, playing here exactly as they would in a hero. The three approved loops and their posters are listed at /ai/assets.json.

The photographs above are the ministry's own, from the July 2026 conferences, and set the standard for all future capture. The video frames are the ministry's own conference loops, playing as they would in a hero. The one remaining gradient is the DON’T card, which is a deliberate counter-example.

## 9. The record

**The record, set as a document.** Law II and Law IV in their purest form. The canonical treatment, in order: short rule, letterspaced kicker, the body in DM Serif Text italic, dateline, signatures. Always on Parchment. Reuse this exact pattern for scripture features, vision statements, and official impact summaries.

Every record carries the marks of a record: a letterspaced kicker, a dateline of what, where, and when, and only official facts. Statistics come from the official ministry record, never estimates and never memory. Signatures are scanned ink, never a script font pretending to be ink.

**Testimonies use four slots, in order:** Before, Encounter, Transformation, Outcome, closing with the person's name and an invitation to respond. Real, consented, and named. Never fabricated, never composited, never anonymous.

## 10. The house and its named front doors

Law III applied. The outreaches lead in their own moments and always carry the endorsement line. Sub-brand materials are DM Sans led, and the serif appears only where the parent speaks.

| Stage | Initiative | Mission | Messaging document |
| --- | --- | --- | --- |
| CLEAN | Revival To My City | Stirring the local church to return to their first love. | https://brand.theword.world/documents/revival-to-my-city |
| BURN | EVERY1 Movement | Empowering the local church to do the Great Commission and walk in God's calling. | https://brand.theword.world/documents/every1 |
| TRAIN | School of the Local Church | Training the local church to know their authority in Christ and build a real relationship with Jesus. | https://brand.theword.world/documents/school-of-the-local-church |

Each door is told apart by ground, Flame ceiling, and register, not by a separate palette.

| Stage | Ground | Type | Flame | Register |
| --- | --- | --- | --- | --- |
| CLEAN | White or Parchment. The most whitespace of the three. | Midnight on light. DM Sans led. | 5% ceiling. The quietest door. | Before the fire. Calm, open, unhurried. |
| BURN | Midnight, full bleed wherever it can be. | Parchment on Midnight. Ember for links and buttons. | The full tenth. This door owns the fire. | The fire itself. Loudest, fastest, most footage. |
| TRAIN | Word Blue structure on Parchment. | Parchment on Word Blue. The most typographic door. | 5% ceiling. Structure carries it, not colour. | A building. Ordered, sequential, institutional. |

Every initiative surface carries the endorsement line: *A ministry of THE WORD FOR ALL THE WORLD*

Exception on record: the EVERY1 app follows the YouVersion model and will not visibly promote the parent. Until it ships, EVERY1 follows this guide. RTMC's script-logo exploration ("Revival" cursive) remains open and compatible. The script is custom lettering, not a brand font.

## 11. Voice

**Bold, clear, simple, direct.** Pastoral with prophetic urgency. Invitation-first. Short, punchy sentences. Never polished-corporate, never hype. Recurring language: real relationship with Jesus · first love · fire starts fire · turn your heart back to Jesus · walk with Jesus. Full rules live in the Voice & Vision Sheet.

**The filter.** Would Nathan actually say this? Does it point people to Jesus Himself? Is it clear to a new believer? Does it invite response? If unsure, simplify and center Jesus.

**Standing rules.** Short sentences. One idea each. Say Jesus by name, not "faith," not "spirituality." Never invent a statistic, a quote, or a testimony; the record or nothing (Law II). Never manufacture a catchphrase: if a line has to be explained to be catchy, kill it. Invitation before information: every piece ends with something the reader can do.

### Load-bearing phrases

Use these exactly as written.

| Phrase | What it carries |
| --- | --- |
| Real relationship with Jesus | The gospel in five words. The good news is not religion. It's Him. |
| First love | Revelation 3. The heart of every RTMC message: return. |
| Fire starts fire | How the mission spreads. We burn; the dry catch. |
| Revival is here, not coming | Our posture. We announce a fact, we don't market a hope. |
| EVERY1 in the church for EVERY1 outside the church | The whole movement in one line. Always styled EVERY1. |
| Lighting hearts and seats on fire for Jesus | What a revival meeting does. |
| Walk with Jesus · turn your heart back to Jesus | The invitation, said plainly. |
| Authority in Christ | What the School trains. Believers carry power, not permission slips. |
| The Holy Spirit runs our services | The guarantee. There is no routine He can't interrupt. |

### Language we never use

**Hype.** insane, epic, unreal, next-level, game-changer, "God showed up and showed out", "you won't believe", walls of 🔥 emojis, ALL-CAPS excitement

Hype manufactures a feeling. We report what God actually did. The record is more powerful than the adjective.

**Corporate Polish.** leverage, synergy, solutions, optimize, engage stakeholders, "excited to announce", comprehensive, robust

We are a ministry, not a vendor. Corporate language makes the guide the hero and the mission a product.

**Churchy Insider Talk.** traveling mercies, hedge of protection, "love on", "do life together", "press in", "contend for breakthrough", "a God thing", "fresh anointing" (unexplained), "blessed to announce"

Insider language tells a new believer this isn't for them. Everything we say is for them.

Theological words such as repentance, salvation, and Holy Spirit baptism are never banned. They are explained. The test is always the filter: clear to a new believer.

### Rewrites

| Never this | Always this |
| --- | --- |
| "🔥🔥 INSANE night!! God showed UP and showed OUT!!" | "Friday night in [city]: [n] people heard the gospel. [n] turned their hearts back to Jesus. The fire is spreading." (numbers from the official record only) |
| "Join us as we press into a fresh anointing and contend for breakthrough." | "Come. Jesus is moving. Bring the person you've been praying for." |
| "We provide comprehensive discipleship solutions for local church partners." | "We train the local church to walk with Jesus." |

## 12. Message architecture

The believer is the hero. We are the guide. That order never flips. Messaging never makes THE WORD the hero of the story.

| Element | Canonical language |
| --- | --- |
| The hero | The local church and the believer. They want a real, active relationship with Jesus and to walk in their purpose, but they feel dry, distracted, or asleep. |
| The problem | External: the church is asleep and the fire has gone out. Internal: "I know there's more to this walk with Jesus. I just don't know how to get there." Philosophical: the world is waiting for the Church to wake up. |
| The guide | THE WORD FOR ALL THE WORLD. We don't bring hype. We bring hunger. The Holy Spirit runs our services, and fire starts fire. |
| The plan | CLEAN · BURN · TRAIN: Revival To My City wakes the church, the EVERY1 Movement sends it, the School of the Local Church roots it. |
| The call | Primary: join the movement: host a Revival To My City, join EVERY1, enroll in the School. Transitional: watch a testimony, join the prayer meeting, take the free personal evangelism course. |
| The stakes | If the church stays asleep, people keep searching for life in all the wrong places and entire cities stay unchanged. |
| The success | Believers become bold, the Great Commission is fulfilled, cities are transformed. The world knows Jesus. |

## 13. The five people we speak to

Every piece is aimed at one of these five. Know which one before writing a word. The "needs to hear" line is the heart of the message: say it in your own words, but say that.

### The Local Pastor (US & International)

- **They want:** to multiply disciples and lead revival without burning out.
- **Their pain:** exhaustion, plateaued growth, no discipleship pathway.
- **Needs to hear:** "We come to serve your church, not build ours. When we leave, your people stay, on fire and equipped."
- **First step:** host a Revival To My City · train leaders through the School.

### The Hungry Church Member (The Pew, Awake or Asleep)

- **They want:** to grow spiritually and live on mission.
- **Their pain:** dry faith. The conviction that "there must be more."
- **Needs to hear:** "There is more, and it isn't a program. It's a real relationship with Jesus, and it starts with turning back to your first love."
- **First step:** join the EVERY1 Movement · start the School.

### The Lost Online Searcher (18 to 30 · Digital-First)

- **They want:** truth, healing, identity, purpose.
- **Their pain:** anxiety, loneliness, distrust of religion, hungry for what's real.
- **Needs to hear:** "What you're looking for has a name. You can have a real relationship with Jesus, starting today."
- **First step:** watch a testimony → request prayer → begin the intro course.

### The Legacy Leader (66+ · Finishing Well)

- **They want:** to pass the torch and leave their people stronger.
- **Their pain:** feeling forgotten; fear the work dies with them.
- **Needs to hear:** "Your fire isn't finished. The next generation needs what you carry."
- **First step:** mentor through the School · cover the movement in prayer · give.

### The Kingdom Partner (Businesses & Ministries)

- **They want:** eternal impact with their influence and resources.
- **Their pain:** unsure whom to trust; tired of shallow ministry.
- **Needs to hear:** "Fund what heaven is doing. Every number we report comes from the official record. You will always know exactly what your partnership did."
- **First step:** sponsor a Revival To My City · scholarship School students.

## 14. How an agent uses this system

These rules govern AI work specifically. They sit alongside the brand law above, they do not
replace it.

#### Before you produce anything

1. **Fetch the manifest first.** `https://brand.theword.world/ai/manifest.json` is the doorway.
   Read the resources it names. Do not work from remembered brand rules when the manifest is
   reachable, and do not assume a cached copy is current: the manifest carries a version and a
   SHA-256 for every file, so you can tell.
2. **Decide who is speaking.** Four voices share this system:
   - **THE WORD FOR ALL THE WORLD**, the parent institution. Serif, Midnight, Parchment, records,
     signatures, official numbers, the donor relationship.
   - **Revival To My City (CLEAN)**, **the EVERY1 Movement (BURN)**, **the School of the Local
     Church (TRAIN)**, the three named front doors. DM Sans led, bolder, closer to the field.
   The parent's register and an initiative's register are not interchangeable. Pick one before
   the first word or the first pixel.
3. **Read the initiative's own guide when the work is for an initiative.** Each one publishes a
   brand guide under `/letterhead/<slug>` and a messaging document under `/documents/<slug>`.
   The manifest lists them.

#### While you produce

4. **Use approved assets. Never invent them.** Logos, photography, and video are listed in
   `assets.json` with their permitted grounds. If the asset you need is not listed, say so and
   leave the slot empty. An empty slot is on-brand; a borrowed or generated one is not.
5. **Never generate a photograph or a video frame of ministry work.** Law VI is documentary only.
   Synthetic imagery of people, congregations, conferences, or field moments is a brand violation
   no matter how good it looks. Illustration of abstract structure (diagrams, layout wireframes)
   is fine.
6. **Never invent a number, a quote, a testimony, or a date.** Statistics come from the official
   ministry record. If you do not have the record, write the sentence with a bracketed field
   (`[n]`) and flag it. A bracketed placeholder is honest; a plausible figure is a fabrication.
7. **Never invent a Bible reference or paraphrase the prophecy.** The prophecy is quoted exactly,
   in full, or not at all.
8. **Hold the ratios.** Flame is a tenth of a composition at most, and it never carries text.
   Ember is the text-size fire. If you find yourself reaching for Flame on type, you want Ember.
9. **Write to one of the five audiences.** The Messaging Guide names them. Know which one before
   the first sentence.

#### Before you hand the work back

10. **Run the audit.** `https://brand.theword.world/ai/audit.md` is the rubric. Complete it and
    include the result with your output. Work that has not been audited is a draft, not a
    deliverable.
11. **State the version you used.** Every audit report opens with the brand-system version and
    messaging-guide version from the manifest. A year from now that line is how anyone tells which
    standard the work was measured against.
12. **Report what you could not load.** If the manifest or any resource it names was unreachable,
    say so plainly and do not claim brand compliance. "I could not reach `tokens.json`, so the
    colors below are unverified" is a useful answer. Silent guessing is not.

#### When the standards do not cover your case

13. **Reason from the six laws, then say you did.** The laws are the constitution; the sections are
    the case law. If nothing covers your situation, apply the nearest law, choose the more
    restrained option, and flag the gap in your audit under "Open questions" so it can be settled
    in the next version.
14. **Never resolve a conflict silently.** Where the Brand Guide and the Messaging Guide appear to
    disagree, the Messaging Guide rules on wording and the Brand Guide rules on appearance. Where
    an initiative guide and a parent guide appear to disagree, the parent guide rules unless the
    initiative guide records an explicit exception. Report any conflict you find.

## 15. Version history

### Brand Guide v5.2

| Version | Date | Owner | Changed | Approved |
| --- | --- | --- | --- | --- |
| 5.2 | 2026-08-15 | Nathan Zimmer | An initiative brand guide published for each door at /brand/<slug>, each rendering in the identity it publishes and linking to its messaging document. Nine documentary assets added from the July 2026 Sanga conference: three muted loops with posters and six stills. | Joel Zimmer, Nathan Zimmer |
| 5.1 | 2026-08-15 | Nathan Zimmer | Sub-brand identity system added to §11. The three doors are now told apart by ground, Flame ceiling, and register rather than by three separate palettes, and each card renders in the identity it describes. Each door links to its messaging document. No new colours. | Joel Zimmer, Nathan Zimmer |
| 5.0 | 2026-08-15 | Nathan Zimmer | Guide restated as the single source of truth rather than against the retired PDF: Supersedes line dropped, prophecy moved to the Messaging Guide, governmental-iconography boundary and retired colours moved to the anti-patterns record, voice filter de-duplicated, website example retired, design tokens renamed and moved to §08, colour rationale restated as five colours doing one job, swatches set on one row, changelog rebuilt with owner and approval, em dashes removed throughout. | Joel Zimmer, Nathan Zimmer |
| 4.5 | 2026-08-15 | Nathan Zimmer | Signature masters published as approved assets, the initiative documents signed in real ink rather than an italic stand-in, and a Signatures page added to the portal. | Joel Zimmer, Nathan Zimmer |
| 4.4 | not recorded | not recorded | Do/Don’t pairs aligned like-for-like, so each rule and its violation share a row. | not recorded |
| 4.3 | not recorded | not recorded | Do/Don’t reorganized into opposing columns, Tokens & States promoted to its own section, operational checklists removed from the standard. | not recorded |
| 4.2 | not recorded | not recorded | Readability pass: provenance badges removed from swatches, inherited light-on-light text corrected on all card components, muted-text tokens darkened. | not recorded |
| 4.1 | not recorded | not recorded | Real field photographs from the July 2026 conferences embedded as exemplars, field capture checklist added. | not recorded |
| 4.0 | not recorded | not recorded | Design language codified as six native laws, adopted and owned, with governmental iconography excluded. New photography and video rules added with rendered examples. | not recorded |
| 3.1 | not recorded | not recorded | Accessibility and integrity revision: Ember buttons, stats relabelled, tokens and states introduced. | not recorded |
| 3.0 | not recorded | not recorded | Presentation rebuild with Do/Don’t pairs. | not recorded |
| 2.2 | not recorded | not recorded | DM companion pairing adopted. | not recorded |
| 2.1 | not recorded | not recorded | DM Serif Text with Instrument Sans trialled and rejected on readability. | not recorded |
| 2.0 | not recorded | not recorded | Instrument Serif with DM Sans. | not recorded |

### Messaging Guide v1.0

| Version | Date | Change |
| --- | --- | --- |
| 1.0 | August 2026 | Initial guide. Rulings on record: fused mission line public with Purpose/Mission/Vision internal · SOSKA roadmap-only · books/music/clothing out of scope. Origin-story fields bracketed pending verification. Banned-word starter lists pending strike/keep review. |

