#!/usr/bin/env python3
"""Generate the initiative messaging documents (/documents)."""
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<title>{title} · THE WORD FOR ALL THE WORLD</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&display=swap" rel="stylesheet">
<style>
  :root{{
    --midnight:#0B1A2D;
    --word-blue:#023D6F;
    --parchment:#F7F3EC;
    --flame:#F85842;
    --ember:#C13A24;
    --white:#FFFFFF;
    --rule:rgba(11,26,45,.18);
    --rule-light:rgba(247,243,236,.22);
    --serif-display:'DM Serif Display', Georgia, 'Times New Roman', serif;
    --sans:'DM Sans', -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif;
  }}
  *{{margin:0;padding:0;box-sizing:border-box;}}
  @media (prefers-reduced-motion: no-preference){{html{{scroll-behavior:smooth;}}}}
  body{{font-family:var(--sans);font-size:17px;line-height:1.7;color:var(--midnight);background:var(--parchment);-webkit-font-smoothing:antialiased;}}
  a:focus-visible,button:focus-visible{{outline:2px solid var(--ember);outline-offset:3px;border-radius:3px;}}
  .wrap{{max-width:1020px;margin:0 auto;padding:0 32px;width:100%;}}

  /* site nav · unified chrome */
  .sitenav{{position:absolute;top:0;left:0;right:0;z-index:10;}}
  .sitenav .bar{{max-width:1240px;margin:0 auto;padding:26px 36px;display:flex;justify-content:space-between;align-items:center;gap:20px;}}
  .sitenav .logo img{{height:20px;width:auto;display:block;}}
  .sitenav .links{{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:12px 28px;font-size:12.5px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;}}
  .sitenav .links a{{color:rgba(247,243,236,.9);text-decoration:none;}}
  .sitenav .links a:hover{{color:var(--white);}}
  .sitenav .links a.active{{color:var(--white);border-bottom:1px solid rgba(255,255,255,.6);padding-bottom:2px;}}

  /* page band · midnight backdrop for the nav */
  .band{{background:var(--midnight);color:var(--parchment);padding:{band_pad};text-align:center;}}
  .band .kicker{{font-size:13px;font-weight:600;letter-spacing:.22em;text-transform:uppercase;color:var(--white);opacity:.8;margin-bottom:18px;display:block;}}
  .band h1{{font-family:var(--serif-display);font-weight:400;line-height:1.1;font-size:clamp(34px,5vw,54px);}}
  .band h1 em{{font-style:italic;}}
  .band p{{margin:18px auto 0;max-width:600px;color:rgba(247,243,236,.85);}}

  footer{{background:var(--midnight);color:rgba(247,243,236,.75);padding:40px 0;font-size:12.5px;letter-spacing:.06em;text-transform:uppercase;font-weight:500;}}
  footer .wrap{{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;}}
  footer img{{height:16px;width:auto;display:block;opacity:.9;}}
  @media(max-width:640px){{.sitenav .bar{{padding:20px 24px;}}}}
{extra_css}
</style>
</head>
<body>

<nav class="sitenav">
  <div class="bar">
    <a class="logo" href="/" aria-label="THE WORD FOR ALL THE WORLD, portal home">
      <img src="/assets/logos/the-word-for-all-the-world.png" alt="THE WORD FOR ALL THE WORLD">
    </a>
    <div class="links">
      <a href="/">Home</a>
      <a href="/brand/">Brand Guide</a>
      <a href="/brand/messaging/">Messaging</a>
      <a href="/documents/"{doc_active}>Documents</a>
      <a href="/letterhead/"{lh_active}>Letterhead</a>
      <a href="/signatures/">Signatures</a>
    </div>
  </div>
</nav>
"""

FOOT = """
<footer>
  <div class="wrap">
    <a href="/" aria-label="THE WORD FOR ALL THE WORLD, portal home"><img src="/assets/logos/the-word-for-all-the-world.png" alt="THE WORD FOR ALL THE WORLD"></a>
    <span>Every tribe. Every tongue. Every nation. EVERY1.</span>
    <span>brand.theword.world · Internal use</span>
  </div>
</footer>

</body>
</html>
"""

DOC_CSS = """
  /* the paper */
  main{padding:64px 0 96px;}
  .toolbar{max-width:820px;margin:0 auto 22px;padding:0 24px;display:flex;justify-content:space-between;align-items:center;gap:14px;flex-wrap:wrap;}
  .toolbar .back{font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--word-blue);text-decoration:none;}
  .toolbar .back:hover{color:var(--ember);}
  .printbtn{font-family:var(--sans);font-size:12px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--white);background:var(--word-blue);border:none;border-radius:3px;padding:11px 22px;cursor:pointer;}
  .printbtn:hover{background:var(--midnight);}
  .paper{max-width:820px;margin:0 auto;background:var(--white);border:1px solid var(--rule);box-shadow:0 18px 50px rgba(11,26,45,.14);padding:clamp(40px,7vw,84px);}
  .letterhead{text-align:center;padding-bottom:26px;border-bottom:1px solid var(--midnight);margin-bottom:44px;}
  .letterhead img{height:22px;width:auto;}
  .doctitle{font-family:var(--serif-display);font-weight:400;font-size:clamp(28px,4vw,40px);line-height:1.16;text-align:center;margin:0 0 12px;}
  .doctitle em{font-style:italic;}
  .docmeta{text-align:center;font-size:12px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:rgba(11,26,45,.6);margin-bottom:44px;}
  .docbody{font-family:var(--sans);font-size:16px;line-height:1.75;}
  .docbody .whereas{margin-bottom:16px;}
  .docbody .whereas b{font-size:13px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--word-blue);}
  .docbody .therefore{margin:30px 0 8px;font-size:13px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;text-align:center;}
  .sec{margin-top:34px;}
  .sec .sh{font-size:13px;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--midnight);border-bottom:1px solid var(--rule);padding-bottom:8px;margin-bottom:14px;}
  .sec .sh .n{color:var(--ember);margin-right:10px;}
  .sec p{margin-bottom:12px;}
  .sec ul{margin:6px 0 12px 22px;}
  .sec li{margin-bottom:8px;}
  .sec .plain{font-size:14px;line-height:1.7;color:rgba(11,26,45,.85);background:var(--parchment);border-left:3px solid var(--word-blue);padding:14px 18px;margin-top:10px;}
  .keywords{display:flex;flex-wrap:wrap;gap:8px;margin-top:6px;}
  .keywords span{font-size:13px;font-weight:600;border:1px solid var(--rule);border-radius:2px;padding:5px 12px;background:var(--parchment);}
  .adoption{margin-top:48px;padding-top:28px;border-top:1px solid var(--midnight);text-align:center;}
  .adoption .ad{font-size:12px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:rgba(11,26,45,.7);}
  .sigrow{display:flex;justify-content:center;gap:80px;flex-wrap:wrap;margin-top:44px;}
  .sig{min-width:220px;}
  .sig .ink{height:62px;display:flex;align-items:flex-end;justify-content:center;}
  .sig .ink img{max-height:62px;max-width:220px;width:auto;height:auto;display:block;}
  .sig .name{margin-top:8px;padding-top:10px;border-top:1px solid var(--midnight);font-size:14px;font-weight:700;letter-spacing:.06em;line-height:1.3;color:var(--midnight);}
  .sig .role{margin-top:6px;font-size:11px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:rgba(11,26,45,.75);}
  .sealline{margin-top:40px;font-size:11px;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:rgba(11,26,45,.55);}

  @media print{
    .sitenav,.band,.toolbar,footer{display:none !important;}
    body{background:var(--white);}
    main{padding:0;}
    .paper{max-width:none;margin:0;border:none;box-shadow:none;padding:0.4in 0.5in;}
    .docbody{font-size:11.5pt;line-height:1.65;}
    .sec{page-break-inside:avoid;}
    .adoption{page-break-inside:avoid;}
    .sig .ink{height:52px;}
    .sig .ink img{max-height:52px;}
    a{color:inherit;text-decoration:none;}
  }
"""

DOC_PAGE = """
<div class="band"></div>
<main>
  <div class="toolbar">
    <a class="back" href="{backurl}">&larr; {backlabel}</a>
    <button class="printbtn" onclick="window.print()">Print this document</button>
  </div>
  <article class="paper">
    <div class="letterhead">
      <img src="/assets/logos/wordmark-midnight-ink.png" alt="THE WORD FOR ALL THE WORLD">
    </div>
    <h1 class="doctitle">{doctitle}</h1>
    <div class="docmeta">{metaline}</div>
    <div class="docbody">
{body}
      <div class="adoption">
        <div class="ad">Entered into the record · August 2026</div>
{sigrow}
        <div class="sealline">Every tribe. Every tongue. Every nation. EVERY1.</div>
      </div>
    </div>
  </article>
</main>
"""

# Who signs, and the signature master placed above each printed name. A signatory with
# no master published yet gets the empty space above the rule, which is what an unsigned
# line looks like. Add the file path here the day the master lands in assets/signatures/.
SIGNATORIES = [
    ("Joel Zimmer", "Approved and Recorded", None),
    ("Nathan Zimmer", "Approved and Recorded", "/assets/signatures/nathaniel-zimmer.svg"),
]


def sigrow():
    out = '        <div class="sigrow">\n'
    for name, role, mark in SIGNATORIES:
        ink = f'<img src="{mark}" alt="Signed by {name}">' if mark else ""
        out += (
            '          <div class="sig">\n'
            f'            <div class="ink">{ink}</div>\n'
            f'            <div class="name">{name}</div>\n'
            f'            <div class="role">{role}</div>\n'
            "          </div>\n"
        )
    return out + "        </div>"


def sec(n, title, inner):
    return f'      <div class="sec">\n        <div class="sh"><span class="n">Section {n}.</span>{title}</div>\n{inner}      </div>\n'

def p(text):
    return f"        <p>{text}</p>\n"

def ul(items):
    lis = "".join(f"          <li>{i}</li>\n" for i in items)
    return f"        <ul>\n{lis}        </ul>\n"

def plain(text):
    return f'        <div class="plain">In plain words: {text}</div>\n'

def keywords(words):
    spans = "".join(f"<span>{w}</span>" for w in words)
    return f'        <div class="keywords">{spans}</div>\n'

FOUNDATION = (
    '      <p class="whereas"><b>The foundation.</b> In December 2019 this ministry received the prophecy that stands as its founding document. The word came before the work. THE WORD FOR ALL THE WORLD exists to strengthen the local church to fulfill the Great Commission, until EVERY1 knows the name Jesus. The ministry orders its work as one journey in three parts, CLEAN, BURN, and TRAIN, held always in that order: a heart is cleaned, then it burns, then it is trained to keep burning.</p>\n'
)

def sec_name_standing(n, name_html):
    return sec(n, "Name and Standing",
        p(f"The initiative is named {name_html}. It is a named front door of THE WORD FOR ALL THE WORLD. It is not a separate organization, not a separate home, and not a denomination. Wherever its name appears, it carries the endorsement line: <em>A ministry of THE WORD FOR ALL THE WORLD.</em>"))

def sec_authority(n, extends):
    return sec(n, "Authority and Amendment",
        p(f"This document is part of the {extends} and carries its authority. It changes one way: a proposed edit in writing, approval by Joel Zimmer and Nathan Zimmer, and a recorded entry in the changelog. No silent edits, ever."))

# ============ MESSAGING DOCUMENTS (/documents) ============

MSG_LEAD = '      <p class="therefore">This document records what the initiative is, in the words of the ministry</p>\n'

rtmc_msg = FOUNDATION
rtmc_msg += '      <p class="whereas">The church in many places is asleep and the fire has gone out. Revival is not a hope we are waiting on. It is a fact we are announcing.</p>\n'
rtmc_msg += MSG_LEAD
rtmc_msg += sec_name_standing(1, "<strong>Revival To My City</strong>")
rtmc_msg += sec(2, "Place in the Journey",
    p("Revival To My City is the first movement of the journey. Its word is <strong>CLEAN</strong>. Before a believer can burn, the heart must be cleaned out and turned back to its first love."))
rtmc_msg += sec(3, "Purpose",
    p("To stir the local church to return to their first love (Revelation 3). It speaks to congregations and pew sitters who are asleep at the wheel: complacent, bogged down by the weeds in their hearts.")
    + plain("Revival To My City wakes the church up."))
rtmc_msg += sec(4, "What It Is",
    p("Two to three evenings of Spirit-led revival meetings held in a city: worship, preaching, altar calls, and healing. Hearts get cleaned out and set back on their first love.")
    + p("The Holy Spirit runs the services. There is no routine He cannot interrupt.")
    + p("The message of every meeting is this: Jesus has already saved you, healed you, and purchased your freedom. Now receive it."))
rtmc_msg += sec(5, "What It Is Not",
    ul(["It is not a replacement for the local church. We come to serve their house, not build ours.",
        "It is not a new church or church plant. When we leave, the people stay, on fire and equipped, in their own local church.",
        "It does not go where it cannot serve. If no local church can partner in an area, the ministry holds off. We do not create spiritual orphans."]))
rtmc_msg += sec(6, "How a Revival Is Held",
    ul(["Evening services run Thursday or Friday through Saturday, held in neutral venues: event centers and meeting halls.",
        "One local host church partners with ministry of helps. THE WORD brings the worship team and the preaching.",
        "Saturday morning is outreach in the community, followed by a final evening service.",
        "Testimonies are captured as records of what God did: real, consented, and named."]))
rtmc_msg += sec(7, "The Words It Carries",
    keywords(["First love", "Lighting hearts and seats on fire for Jesus", "Revival is here, not coming", "Receive what Jesus already purchased"]))
rtmc_msg += sec(8, "How to Take Part",
    p("Host a Revival To My City in your city. Attend one near you. Then join the EVERY1 Movement. That is how the fire stays lit."))
rtmc_msg += sec_authority(9, "Brand Messaging Guide")

e1_msg = FOUNDATION
e1_msg += '      <p class="whereas">The Great Commission will not be fulfilled by pulpits alone. Every believer is the minister, sent by God everywhere they go.</p>\n'
e1_msg += MSG_LEAD
e1_msg += sec_name_standing(1, "the <strong>EVERY1 Movement</strong>, always styled EVERY1")
e1_msg += sec(2, "Place in the Journey",
    p("The EVERY1 Movement is the second movement of the journey. Its word is <strong>BURN</strong>. A cleaned heart catches fire, and fire starts fire."))
e1_msg += sec(3, "Purpose",
    p("To empower the local church to do the Great Commission and walk in God's calling. In one line: EVERY1 in the church going to EVERY1 outside of the church.")
    + plain("The EVERY1 Movement sends the church out."))
e1_msg += sec(4, "What It Is",
    p("A movement of ordinary believers who share Jesus where they already live, work, and study. You are the minister, sent by God everywhere you go.")
    + p("It is a lifestyle, not an event. Membership is simple: you have shared Jesus with at least one person recently. That is the movement."))
e1_msg += sec(5, "Who May Join",
    p("Every believer. There is no maturity requirement. When you are born again, you qualify.")
    + p("The movement carries special fire for the young and the newly saved: their fire kindles faster and hotter."))
e1_msg += sec(6, "The First Three Steps",
    ul(["Join the weekly prayer meeting, praying for the lost.",
        "Share Jesus with one person this week.",
        "Take the free personal evangelism course, offered through the School of the Local Church."]))
e1_msg += sec(7, "The Words It Carries",
    keywords(["EVERY1 in the church for EVERY1 outside the church", "You are the minister", "Fire starts fire", "A lifestyle, not an event"]))
e1_msg += sec(8, "On the Record",
    p("A future EVERY1 app is planned on the YouVersion model and will not visibly promote the parent ministry. This exception stands on record in the Brand Guide. Until the app ships, EVERY1 follows the Brand Messaging Guide in full."))
e1_msg += sec_authority(9, "Brand Messaging Guide")

slc_msg = FOUNDATION
slc_msg += '      <p class="whereas">The School began with one question asked on a Ugandan tarmac: "Will you help me train my people?" That question has been answered ever since.</p>\n'
slc_msg += MSG_LEAD
slc_msg += sec_name_standing(1, "the <strong>School of the Local Church</strong>")
slc_msg += sec(2, "Place in the Journey",
    p("The School of the Local Church is the third movement of the journey. Its word is <strong>TRAIN</strong>. A burning heart is trained to keep burning. The School gives the fire roots."))
slc_msg += sec(3, "Purpose",
    p("To train the local church to know their authority in Christ and build a real relationship with Jesus.")
    + plain("The School of the Local Church roots the fire so it lasts."))
slc_msg += sec(4, "Who It Serves",
    p("Local leaders and hungry believers who are done with shallow faith and want to go deeper. This includes pastors in places the internet does not reach, whom the ministry trains in person."))
slc_msg += sec(5, "What Is Taught",
    p("A real relationship with Jesus is built by knowing His character: who He is, how He thinks, and what He wants from you.")
    + p("The School walks each student through the purpose, mission, message, and foundations of the local church, their authority in Christ, and how to keep the fire burning for life."))
slc_msg += sec(6, "How the School Is Held",
    ul(["Enrollment is rolling and the training is self-paced video modules, roughly a year at one video a week.",
        "A live discipleship gathering is held online monthly, and the team is available for questions.",
        "Three-day intensive conferences are hosted by local churches, at home and overseas.",
        "Graduates leave still on fire, grounded in the foundations, and active in the EVERY1 Movement."]))
slc_msg += sec(7, "The Words It Carries",
    keywords(["Real relationship with Jesus", "Authority in Christ", "Fire with roots"]))
slc_msg += sec(8, "How to Take Part",
    p("Enroll at any time. Start with the free personal evangelism course."))
slc_msg += sec_authority(9, "Brand Messaging Guide")

# ============ PAGE ASSEMBLY ============

INDEX_CSS = """
  main{padding:72px 0 96px;}
  .section-label{font-size:12px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:var(--ember);margin-bottom:24px;}
  .cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px;}
  .card{display:flex;flex-direction:column;justify-content:space-between;background:var(--white);border:1px solid var(--rule);border-radius:4px;padding:30px 28px;text-decoration:none;color:var(--midnight);transition:border-color .15s ease, box-shadow .15s ease;min-height:210px;}
  .card:hover{border-color:var(--ember);box-shadow:0 10px 30px rgba(11,26,45,.1);}
  .card .stage{display:inline-block;font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--white);background:var(--word-blue);border-radius:2px;padding:4px 10px;margin-bottom:16px;align-self:flex-start;}
  .card h2{font-family:var(--serif-display);font-weight:400;font-size:25px;line-height:1.2;margin-bottom:10px;}
  .card p{font-size:14.5px;line-height:1.6;color:rgba(11,26,45,.8);}
  .card .go{margin-top:20px;font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--word-blue);}
  .card:hover .go{color:var(--ember);}
  .note{max-width:660px;margin:44px auto 0;text-align:center;font-size:14px;color:rgba(11,26,45,.75);}
"""

INITIATIVES = [
    ("revival-to-my-city", "Revival To My City", "Clean", "Stirring the local church to return to their first love."),
    ("every1", "EVERY1 Movement", "Burn", "Empowering the local church to do the Great Commission and walk in God's calling."),
    ("school-of-the-local-church", "School of the Local Church", "Train", "Training the local church to know their authority in Christ and build a real relationship with Jesus."),
]

TITLES = {
    "revival-to-my-city": "Revival To My <em>City</em>",
    "every1": "The EVERY1 <em>Movement</em>",
    "school-of-the-local-church": "School of the <em>Local Church</em>",
}

SECTIONS = {
    "documents": dict(
        active="doc",
        metaline="Initiative Messaging Document · August 2026",
        backlabel="All documents",
        index_title="Initiative Documents",
        index_h1="Initiative <em>Documents</em>",
        index_sub="One messaging document for each initiative of THE WORD FOR ALL THE WORLD, an extension of the Brand Messaging Guide. Read them on screen, or print them on letterhead. One journey, in order: Clean, Burn, Train.",
        doc_suffix="Initiative Document",
        bodies={"revival-to-my-city": rtmc_msg, "every1": e1_msg, "school-of-the-local-church": slc_msg},
    ),
}

for section, cfg in SECTIONS.items():
    doc_a = ' class="active"' if cfg["active"] == "doc" else ""
    lh_a = ' class="active"' if cfg["active"] == "lh" else ""
    for slug, name, stage, mission in INITIATIVES:
        html = HEAD.format(title=f"{name} · {cfg['doc_suffix']}", extra_css=DOC_CSS,
                           band_pad="96px 0 24px", doc_active=doc_a, lh_active=lh_a)
        html += DOC_PAGE.format(backurl=f"/{section}/", backlabel=cfg["backlabel"],
                                doctitle=TITLES[slug], metaline=cfg["metaline"],
                                body=cfg["bodies"][slug], sigrow=sigrow())
        html += FOOT
        os.makedirs(os.path.join(REPO, section, slug), exist_ok=True)
        path = os.path.join(REPO, section, slug, "index.html")
        open(path, "w").write(html)
        print(path, len(html))
    html = HEAD.format(title=cfg["index_title"], extra_css=INDEX_CSS,
                       band_pad="150px 0 64px", doc_active=doc_a, lh_active=lh_a)
    html += '\n<div class="band">\n  <span class="kicker">One Journey · Three Initiatives</span>\n'
    html += f'  <h1>{cfg["index_h1"]}</h1>\n  <p>{cfg["index_sub"]}</p>\n</div>\n'
    html += '<main>\n  <div class="wrap">\n    <div class="section-label">The Initiatives</div>\n    <div class="cards">\n'
    for slug, name, stage, mission in INITIATIVES:
        html += (f'      <a class="card" href="/{section}/{slug}/">\n        <div>\n'
                 f'          <span class="stage">{stage}</span>\n          <h2>{name}</h2>\n'
                 f'          <p>{mission}</p>\n        </div>\n'
                 f'        <div class="go">Read the document &rarr;</div>\n      </a>\n')
    html += '''    </div>
    <p class="note">Each document is kept under the ministry's own law: the institution signs its work, numbers come from the official record only, and no document changes without a written proposal, approval, and a changelog entry.</p>
  </div>
</main>
'''
    html += FOOT
    path = os.path.join(REPO, section, "index.html")
    open(path, "w").write(html)
    print(path, len(html))


# ============ SUB-BRAND GUIDES (/brand/<slug>) ============
# One brand guide per named front door. Each renders in the identity it
# describes, per Brand Guide §11: a ground, a Flame ceiling, and a register.

SUB_CSS = """
  .door{position:relative;min-height:74vh;display:flex;align-items:flex-end;background:var(--midnight);overflow:hidden;}
  .door video{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;}
  .door .scrim{position:absolute;inset:0;background:linear-gradient(180deg,rgba(11,26,45,.72) 0%,rgba(11,26,45,.45) 45%,rgba(11,26,45,.92) 100%);}
  .door .inner{position:relative;z-index:2;max-width:1020px;margin:0 auto;padding:0 32px 72px;width:100%;color:var(--parchment);}
  .door .stageword{font-size:clamp(52px,9vw,104px);font-weight:700;letter-spacing:.05em;line-height:1;}
  .door h1{font-family:var(--serif-display);font-weight:400;font-size:clamp(30px,4.4vw,48px);line-height:1.12;margin-top:10px;}
  .door .mission{margin-top:16px;max-width:560px;color:rgba(247,243,236,.9);}
  .door .endorse{margin-top:26px;padding-top:14px;border-top:1px solid rgba(247,243,236,.3);font-size:11px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:rgba(247,243,236,.85);}
  @media (prefers-reduced-motion: reduce){.door video{display:none;}}

  main{padding:72px 0 40px;}
  .bar{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:52px;}
  .bar a{font-size:11.5px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;text-decoration:none;color:var(--word-blue);}
  .bar a:hover{color:var(--ember);}
  .blk{margin-bottom:64px;}
  .lab{font-size:12px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;color:var(--ember);margin-bottom:20px;}
  h2{font-family:var(--serif-text);font-weight:400;font-size:clamp(26px,3.2vw,34px);line-height:1.2;margin-bottom:14px;}
  .lede{max-width:70ch;color:rgba(11,26,45,.85);}
  .spec{width:100%;border-collapse:collapse;margin-top:18px;background:var(--white);border:1px solid var(--rule);}
  .spec th,.spec td{text-align:left;padding:14px 16px;border-bottom:1px solid var(--rule);vertical-align:top;font-size:15px;}
  .spec tr:last-child td{border-bottom:none;}
  .spec th{width:150px;font-size:11px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:rgba(11,26,45,.8);}
  .shots{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px;margin-top:20px;}
  .shot{background:var(--white);border:1px solid var(--rule);border-radius:4px;overflow:hidden;}
  .shot img{width:100%;display:block;aspect-ratio:4/3;object-fit:cover;}
  .shot .cap{padding:14px 16px;}
  .shot .c1{font-size:13.5px;line-height:1.5;}
  .shot .c2{margin-top:8px;font-size:10.5px;font-weight:600;letter-spacing:.14em;text-transform:uppercase;color:rgba(11,26,45,.8);}
  ul.doorrules{list-style:none;max-width:72ch;margin-top:10px;}
  ul.doorrules li{position:relative;padding-left:22px;margin-bottom:14px;font-size:15.5px;line-height:1.65;}
  ul.doorrules li::before{content:"\\00b7";position:absolute;left:4px;color:var(--ember);font-weight:700;}
  .nextstep{background:var(--midnight);color:var(--parchment);border-radius:4px;padding:34px 32px;display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap;}
  .nextstep .t{font-family:var(--serif-text);font-size:23px;}
  .nextstep .s{font-size:14px;color:rgba(247,243,236,.85);margin-top:6px;max-width:52ch;}
  .nextstep a{font-size:11.5px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;text-decoration:none;color:var(--white);background:var(--ember);border-radius:3px;padding:13px 20px;white-space:nowrap;}
  .nextstep a:hover{background:#A62F1B;}

  /* each door renders in the identity it publishes (Brand Guide §11) */
  body.burn{background:var(--midnight);color:var(--parchment);}
  body.burn .lede{color:rgba(247,243,236,.88);}
  body.burn .lab{color:var(--flame);}
  body.burn .bar a{color:var(--parchment);}
  body.burn .bar a:hover{color:var(--flame);}
  body.burn .spec{background:rgba(247,243,236,.05);border-color:rgba(247,243,236,.22);}
  body.burn .spec th,body.burn .spec td{border-bottom-color:rgba(247,243,236,.18);}
  body.burn .spec th{color:rgba(247,243,236,.8);}
  body.burn .shot{background:rgba(247,243,236,.05);border-color:rgba(247,243,236,.22);}
  body.burn .shot .c2{color:rgba(247,243,236,.8);}
  body.burn .prov{color:rgba(247,243,236,.8);}
  body.burn ul.doorrules li::before{color:var(--flame);}
  body.burn .nextstep{background:rgba(247,243,236,.06);border:1px solid rgba(247,243,236,.22);}

  body.train .lab{color:var(--word-blue);}
  body.train h2{border-left:4px solid var(--word-blue);padding-left:16px;margin-left:-20px;}
  body.train .spec th{background:var(--word-blue);color:var(--parchment);}
  body.train .spec{border-color:var(--word-blue);}
  body.train ul.doorrules li::before{color:var(--word-blue);}
  body.train .nextstep{background:var(--word-blue);}

  body.clean .lab{color:var(--ember);}
  body.clean .blk{margin-bottom:82px;}
  .prov{margin-top:14px;font-size:13px;color:rgba(11,26,45,.8);max-width:74ch;}
"""

SUBS = [
    dict(
        slug="revival-to-my-city", stage="CLEAN", name="Revival To My City",
        title="Revival To My <em>City</em>",
        mission="Stirring the local church to return to their first love.",
        video="rtmc-evening-worship",
        ground="White or Parchment. The most whitespace of the three.",
        typerule="Midnight on light. DM Sans led.",
        flame="5% ceiling. The quietest door.",
        register="Before the fire. Calm, open, unhurried.",
        why="CLEAN is the first movement of the journey. A heart is cleaned before it burns, so this "
            "door is the invitation, not the intensity. Its work happens in evening services: worship, "
            "preaching, the altar call, and testimonies captured as they are given.",
        rules=[
            "<strong>Lead with air.</strong> This door carries the most whitespace in the house. Crowding it contradicts what it is for.",
            "<strong>Flame at five percent.</strong> Half the parent's ceiling. A single tick, a rule, a numeral. Never a panel.",
            "<strong>Midnight type on light ground.</strong> The evening footage is dark enough on its own; the page around it stays paper.",
            "<strong>The altar call is the call to action.</strong> Every surface ends with something the reader can do, and it is an invitation before it is information.",
        ],
        shots=[("rtmc-crowd-hands-raised","An evening congregation with hands raised during the service.","31 Jul 2026"),
               ("rtmc-preaching-evening","Preaching to the evening crowd from the open-air platform.","31 Jul 2026")],
    ),
    dict(
        slug="every1", stage="BURN", name="EVERY1 Movement",
        title="The EVERY1 <em>Movement</em>",
        mission="Empowering the local church to do the Great Commission and walk in God's calling.",
        video="every1-community-gathering",
        ground="Midnight, full bleed wherever it can be.",
        typerule="Parchment on Midnight. Ember for links and buttons.",
        flame="The full tenth. This door owns the fire.",
        register="The fire itself. Loudest, fastest, most footage.",
        why="BURN is the second movement. A cleaned heart catches fire, and fire starts fire. This door "
            "is not an event, it is a lifestyle: ordinary believers sharing Jesus where they already "
            "live, work, and study. Membership is simple, and it is measured by whether you have shared "
            "Jesus with someone recently.",
        rules=[
            "<strong>Midnight ground, full bleed.</strong> This is the only door that runs dark by default. Footage fills the frame wherever the layout allows.",
            "<strong>Flame to the full tenth.</strong> The parent's ceiling, used fully. It still never carries text: Ember does that job.",
            "<strong>Most footage, least chrome.</strong> Motion carries this door. Where a still would do for CLEAN or TRAIN, EVERY1 uses the clip.",
            "<strong>One recorded exception.</strong> The future EVERY1 app follows the YouVersion model and will not visibly promote the parent. Until it ships, EVERY1 follows this guide in full.",
        ],
        shots=[("every1-one-to-one","One believer greeting another at the front of the tent, person to person.","31 Jul 2026"),
               ("every1-ministry-in-the-tent","Serving the seated rows individually rather than from the platform.","30 Jul 2026")],
    ),
    dict(
        slug="school-of-the-local-church", stage="TRAIN", name="School of the Local Church",
        title="School of the <em>Local Church</em>",
        mission="Training the local church to know their authority in Christ and build a real relationship with Jesus.",
        video="slc-teaching-session",
        ground="Word Blue structure on Parchment.",
        typerule="Parchment on Word Blue. The most typographic door.",
        flame="5% ceiling. Structure carries it, not colour.",
        register="A building. Ordered, sequential, institutional.",
        why="TRAIN is the third movement, and the one that lasts. Fire that is not trained goes out. "
            "This door teaches believers their authority in Christ and how to build a real relationship "
            "with Jesus, starting with the free personal evangelism course.",
        rules=[
            "<strong>Structure carries the weight.</strong> Word Blue blocks, rules, and numbered sequence do the work that colour does elsewhere.",
            "<strong>The most typographic door.</strong> Sessions, modules, and steps are numbered and ordered. If it can be a sequence, it is one.",
            "<strong>Flame at five percent.</strong> A school is not a rally. The fire is in what is taught, not in the layout.",
            "<strong>Everything is a record.</strong> Course names, session numbers, and dates are stated exactly, because a school that is vague about its own curriculum is not a school.",
        ],
        shots=[("slc-attendees-taking-notes","Attendees following the teaching with open Bibles and notebooks.","30 Jul 2026"),
               ("slc-bibles-received","Bibles and the personal evangelism course handed to attendees.","31 Jul 2026")],
    ),
]

SUB_PAGE = """
<div class="door">
  <video autoplay muted loop playsinline poster="/assets/images/{video}-poster.jpg">
    <source src="/assets/videos/{video}.mp4" type="video/mp4">
  </video>
  <div class="scrim"></div>
  <div class="inner">
    <div class="stageword">{stage}</div>
    <h1>{title}</h1>
    <p class="mission">{mission}</p>
    <div class="endorse">A ministry of THE WORD FOR ALL THE WORLD</div>
  </div>
</div>

<main>
  <div class="wrap">
    <div class="bar">
      <a href="/brand/#architecture">&larr; Brand Guide &sect;11</a>
      <a href="/documents/{slug}/">Messaging document &rarr;</a>
    </div>

    <div class="blk">
      <div class="lab">Identity</div>
      <h2>What this door owns.</h2>
      <p class="lede">The three doors are told apart by temperature and proportion, not by three separate
      palettes, so the house still reads as one house. This is what {name} owns.</p>
      <table class="spec">
        <tr><th>Ground</th><td>{ground}</td></tr>
        <tr><th>Type</th><td>{typerule}</td></tr>
        <tr><th>Flame</th><td>{flame}</td></tr>
        <tr><th>Register</th><td>{register}</td></tr>
        <tr><th>Endorsement</th><td>Every surface carries the line <em>A ministry of THE WORD FOR ALL THE WORLD.</em> It is not optional.</td></tr>
      </table>
    </div>

    <div class="blk">
      <div class="lab">Place in the journey</div>
      <h2>Why this door exists.</h2>
      <p class="lede">{why}</p>
    </div>

    <div class="blk">
      <div class="lab">The ground in use</div>
      <h2>Documentary capture, from the record.</h2>
      <p class="lede">Real moments from real ministry. Nothing stock, nothing staged, nothing generated.
      Every published photograph carries a caption in the record register.</p>
      <div class="shots">
{shots}      </div>
      <p class="prov">Dates come from the capture record. The location is recorded as Sanga, Mbarara,
      Uganda in the capture folder and is pending confirmation against the official ministry record,
      so it is stated here and not yet frozen into the guide.</p>
    </div>

    <div class="blk">
      <div class="lab">Rules that differ from the parent</div>
      <h2>Where this door departs.</h2>
      <p class="lede">Everything in the Brand Guide applies here. These are the points where {name}
      is deliberately not the parent.</p>
      <ul class="doorrules">
{rules}      </ul>
    </div>

    <div class="blk">
      <div class="nextstep">
        <div>
          <div class="t">What this door says, in the words of the ministry</div>
          <div class="s">The messaging document records what {name} is, who it speaks to, and the
          language it carries. This guide governs how it looks. That one governs what it says.</div>
        </div>
        <a href="/documents/{slug}/">Messaging document &rarr;</a>
      </div>
    </div>
  </div>
</main>
"""

for d in SUBS:
    shots = ""
    for name_, cap, date in d["shots"]:
        shots += (f'        <figure class="shot">\n'
                  f'          <img src="/assets/images/{name_}.jpg" alt="{cap}">\n'
                  f'          <figcaption class="cap"><div class="c1">{cap}</div>'
                  f'<div class="c2">SLC Conference &middot; Sanga, Mbarara &middot; {date}</div></figcaption>\n'
                  f'        </figure>\n')
    rules = "".join(f"        <li>{r}</li>\n" for r in d["rules"])
    fields = {k: v for k, v in d.items() if k not in ("rules", "shots")}
    html = HEAD.format(title=f"{d['name']} · Initiative Brand Guide", extra_css=SUB_CSS,
                       band_pad="0", doc_active="", lh_active="")
    html = html.replace("<body>", f"<body class=\"{d['stage'].lower()}\">")
    html += SUB_PAGE.format(shots=shots, rules=rules, **fields)
    html += FOOT
    outdir = os.path.join(REPO, "brand", d["slug"])
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "index.html")
    open(path, "w").write(html)
    print(path, len(html))
