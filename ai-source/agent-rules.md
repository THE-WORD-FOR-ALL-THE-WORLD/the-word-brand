## How an agent uses this system

These rules govern AI work specifically. They sit alongside the brand law above, they do not
replace it.

### Before you produce anything

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

### While you produce

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

### Before you hand the work back

10. **Run the audit.** `https://brand.theword.world/ai/audit.md` is the rubric. Complete it and
    include the result with your output. Work that has not been audited is a draft, not a
    deliverable.
11. **State the version you used.** Every audit report opens with the brand-system version and
    messaging-guide version from the manifest. A year from now that line is how anyone tells which
    standard the work was measured against.
12. **Report what you could not load.** If the manifest or any resource it names was unreachable,
    say so plainly and do not claim brand compliance. "I could not reach `tokens.json`, so the
    colors below are unverified" is a useful answer. Silent guessing is not.

### When the standards do not cover your case

13. **Reason from the six laws, then say you did.** The laws are the constitution; the sections are
    the case law. If nothing covers your situation, apply the nearest law, choose the more
    restrained option, and flag the gap in your audit under "Open questions" so it can be settled
    in the next version.
14. **Never resolve a conflict silently.** Where the Brand Guide and the Messaging Guide appear to
    disagree, the Messaging Guide rules on wording and the Brand Guide rules on appearance. Where
    an initiative guide and a parent guide appear to disagree, the parent guide rules unless the
    initiative guide records an explicit exception. Report any conflict you find.
