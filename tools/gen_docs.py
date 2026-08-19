#!/usr/bin/env python3
"""Generate the initiative messaging documents (/documents)."""
import os

NL = chr(10)
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
  .sitenav .logo.cobrand img{{height:44px;}}
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
{navlogo}
    <div class="links">
      <a href="/">Home</a>
      <a href="/brand/">Brand Guide</a>
      <a href="/brand/messaging/">Messaging</a>
      <a href="/documents/"{doc_active}>Documents</a>
      <a href="/letterhead/"{lh_active}>Letterhead</a>
      <a href="/signatures/">Signatures</a>
      <a href="/assets/">Assets</a>
    </div>
  </div>
</nav>
"""

# The nav mark. A door that has its own approved mark carries the co-brand lockup
# instead of the parent alone, which is how that door shows its endorsement rather
# than stating it in a line of type. Brand Guide §11.
NAV_PARENT = """    <a class="logo" href="/" aria-label="THE WORD FOR ALL THE WORLD, portal home">
      <img src="/assets/logos/the-word/the-word-horizontal-reversed.svg" alt="THE WORD FOR ALL THE WORLD">
    </a>"""

NAV_COBRAND = """    <a class="logo cobrand" href="/" aria-label="Revival To My City, a ministry of THE WORD FOR ALL THE WORLD">
      <img src="/assets/logos/rtmc/rtmc-cobrand.svg" alt="THE WORD FOR ALL THE WORLD and Revival To My City">
    </a>"""


FOOT = """
<footer>
  <div class="wrap">
    <a href="/" aria-label="THE WORD FOR ALL THE WORLD, portal home"><img src="/assets/logos/the-word/the-word-horizontal-reversed.svg" alt="THE WORD FOR ALL THE WORLD"></a>
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
      <img src="/assets/logos/the-word/the-word-horizontal.svg" alt="THE WORD FOR ALL THE WORLD">
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
    ("Joel Zimmer", "Approved and Recorded", "/assets/signatures/joel-zimmer.svg"),
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
        html = HEAD.format(title=f"{name} · {cfg['doc_suffix']}", extra_css=DOC_CSS, navlogo=NAV_PARENT,
                           band_pad="96px 0 24px", doc_active=doc_a, lh_active=lh_a)
        html += DOC_PAGE.format(backurl=f"/{section}/", backlabel=cfg["backlabel"],
                                doctitle=TITLES[slug], metaline=cfg["metaline"],
                                body=cfg["bodies"][slug], sigrow=sigrow())
        html += FOOT
        os.makedirs(os.path.join(REPO, section, slug), exist_ok=True)
        path = os.path.join(REPO, section, slug, "index.html")
        open(path, "w").write(html)
        print(path, len(html))
    html = HEAD.format(title=cfg["index_title"], extra_css=INDEX_CSS, navlogo=NAV_PARENT,
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

  /* BURN leads with its own mark rather than a serif line. The stage word drops to a
     label so the mark is the largest thing on the door, and the endorsement line is set
     on the surface because the approved forms do not carry one. */
  .door .markline{margin-top:8px;}
  .door .markline img{width:min(520px,80%);height:auto;display:block;}
  body.burn .door .stageword{font-size:clamp(13px,1.6vw,16px);font-weight:700;letter-spacing:.22em;line-height:1;color:rgba(247,243,236,.85);}

  .tickrule{display:flex;align-items:center;justify-content:center;gap:12px;margin:26px 0 0;max-width:430px;}
  .tickrule .ln{flex:1;border-top:1px solid currentColor;opacity:.55;}
  .tickrule .tk{width:32px;border-top:3px solid var(--flame);}

  /* CLEAN takes the framed-panel treatment: type never sits straight on the footage */
  body.clean .door{align-items:center;min-height:82vh;}
  body.clean .door .inner{padding:96px 32px;}
  body.clean{background:var(--white);}
  body.clean .door .panel{background:var(--white);border:1px solid var(--midnight);color:var(--midnight);
    max-width:730px;margin:0 auto;padding:clamp(38px,5vw,60px) clamp(28px,4.5vw,56px);text-align:center;}
  body.clean .door .stageword{font-size:clamp(32px,4.6vw,52px);letter-spacing:.08em;}
  body.clean .door h1{margin-top:12px;}
  body.clean .door .mission{margin:16px auto 0;color:rgba(11,26,45,.85);}
  body.clean .door .tickrule{margin-left:auto;margin-right:auto;}
  body.clean .door .endorse{border-top:none;margin-top:22px;padding-top:0;color:rgba(11,26,45,.8);}
  body.clean .blk{margin-bottom:96px;}
  body.clean .nextstep{background:var(--white);border:1px solid var(--midnight);color:var(--midnight);}
  body.clean .nextstep .s{color:rgba(11,26,45,.85);}
  body.clean .nextstep a{background:none;color:var(--word-blue);padding:0;border-bottom:2px solid var(--flame);border-radius:0;}
  body.clean .nextstep a:hover{background:none;color:var(--ember);}
  body.clean .docbar a,body.clean .shot .c2{color:rgba(11,26,45,.8);}
  body.clean .docbar a{border-bottom:1px solid rgba(11,26,45,.3);padding-bottom:2px;}
  body.clean .docbar a:hover{color:var(--ember);border-bottom-color:var(--ember);}

  .marks{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:18px;margin-top:22px;}
  .mark{border:1px solid var(--rule);border-radius:4px;overflow:hidden;background:var(--white);}
  .mark .art{display:flex;align-items:center;justify-content:center;padding:26px 22px;min-height:150px;background:var(--parchment);}
  .mark .art.dark{background:var(--midnight);}
  .mark img{max-width:100%;height:auto;display:block;}
  .mark .lbl{border-top:1px solid var(--rule);padding:12px 16px;font-size:12.5px;line-height:1.5;}
  .mark .lbl b{display:block;font-size:10.5px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:rgba(11,26,45,.8);margin-bottom:4px;}
  .warn{margin-top:18px;background:var(--parchment);border-left:3px solid var(--ember);padding:16px 20px;font-size:14px;line-height:1.65;max-width:74ch;}

  /* CLEAN leads with the mark on white; the footage follows as its own band */
  /* CLEAN's hero is white, so the chrome inverts to Midnight ink over it */
  body.clean .sitenav .links a{color:rgba(11,26,45,.8);}
  body.clean .sitenav .links a:hover{color:var(--ember);}
  body.clean .sitenav .links a.active{color:var(--midnight);border-bottom-color:rgba(11,26,45,.45);}

  .markhero{background:var(--white);padding:clamp(84px,11vw,150px) 32px clamp(64px,8vw,104px);text-align:center;}
  .markhero img{width:min(660px,86%);height:auto;display:block;margin:0 auto;}
  .markhero .mission{margin:34px auto 0;max-width:520px;font-size:17px;color:rgba(11,26,45,.85);}
  .filmband{position:relative;height:min(58vh,520px);overflow:hidden;background:var(--midnight);}
  .filmband video,.filmband img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;}
  @media (prefers-reduced-motion: reduce){.filmband video{display:none;}}
  .filmcap{background:var(--white);padding:16px 32px 0;text-align:center;font-size:11px;font-weight:600;
    letter-spacing:.14em;text-transform:uppercase;color:rgba(11,26,45,.8);}

  main{padding:72px 0 40px;}
  .docbar{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:52px;}
  .docbar a{font-size:11.5px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;text-decoration:none;color:var(--word-blue);}
  .docbar a:hover{color:var(--ember);}
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
  body.burn .docbar a{color:var(--parchment);}
  body.burn .docbar a:hover{color:var(--flame);}
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

  /* TRAIN opens in the identity it describes: Word Blue structure on Parchment */
  body.train .trainhero{background:var(--word-blue);color:var(--parchment);padding:clamp(150px,17vw,200px) 0 clamp(56px,7vw,84px);}
  body.train .trainhero .stageword{font-size:clamp(40px,6vw,72px);font-weight:700;letter-spacing:.06em;line-height:1;}
  body.train .trainhero h1{font-family:var(--serif-display);font-weight:400;font-size:clamp(30px,4.4vw,48px);line-height:1.12;margin-top:10px;}
  body.train .trainhero .mission{margin-top:16px;max-width:560px;color:rgba(247,243,236,.9);}
  body.train .trainhero .tickrule{justify-content:flex-start;margin:26px 0 0;}
  body.train .trainhero .endorse{display:inline-block;margin-top:26px;padding-top:14px;border-top:1px solid rgba(247,243,236,.3);font-size:11px;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:rgba(247,243,236,.85);}
  body.train .filmcap{background:var(--parchment);}

  /* the city instance lockup demo (CLEAN) */
  .lockupdemo{background:var(--white);border:1px solid var(--rule);border-radius:4px;padding:44px 30px;text-align:center;margin-top:20px;}
  .lockupdemo img{width:min(420px,80%);height:auto;}
  .lockupdemo .cityline{margin-top:18px;font-size:15px;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--midnight);}

  /* channel facts · read like an ingredients panel · the parent's card lives in Brand Guide §12 */
  .chanwrap{display:grid;grid-template-columns:minmax(250px,440px);gap:16px;margin-top:20px;}
  .chanfacts{background:var(--white);border:2px solid var(--midnight);border-radius:4px;padding:20px 18px 14px;color:var(--midnight);}
  .chanfacts .cfname{font-size:17px;font-weight:800;letter-spacing:.02em;line-height:1.25;}
  .chanfacts .cfserv{font-size:10.5px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;color:rgba(11,26,45,.72);margin:6px 0 10px;}
  .chanfacts .cfbar{border-top:7px solid var(--midnight);}
  .chanfacts table{width:100%;border-collapse:collapse;margin:0;background:none;border:none;}
  .chanfacts td{padding:8px 0;border-bottom:1px solid var(--rule);font-size:13.5px;vertical-align:baseline;}
  .chanfacts tr:last-child td{border-bottom:none;}
  .chanfacts .cfp{font-weight:700;padding-right:10px;}
  .chanfacts .cfh{text-align:right;font-weight:500;word-break:break-word;}
  .chanfacts .cfh.mut{color:rgba(11,26,45,.62);font-weight:400;font-style:italic;}
  .chanfacts .cffoot{border-top:4px solid var(--midnight);margin-top:2px;padding-top:10px;font-size:9.5px;font-weight:600;letter-spacing:.12em;text-transform:uppercase;color:rgba(11,26,45,.72);}
"""

SUBS = [
    dict(
        slug="revival-to-my-city", stage="CLEAN", name="Revival To My City",
        title="Revival To My <em>City</em>",
        mission="Stirring the local church to return to their first love.",
        video="rtmc-city-gathering",
        ground="White or Parchment. The most whitespace of the three.",
        typerule="Midnight on light. DM Sans led.",
        flame="5% ceiling. The quietest door.",
        register="Before the fire. Calm, open, unhurried.",
        avatar="The bare mark, Midnight on White. The tick rule survives a circular crop; the endorsement line does not have to.",
        handle="@revivaltomycity, recorded in the Channels section of this guide.",
        kindhead="An event brand.",
        kindtext="Revival To My City lives on posters, dates, and city names. Its real design system "
                 "is not a page, it is the city instance: how the mark locks up with a city and a "
                 "date, the poster, the stage backdrop, the countdown graphic. The name itself is "
                 "built for this, because \"My City\" becomes each city's own sentence, and most "
                 "people will meet this brand on a poster before they meet it in a room.",
        capture=[
            "<strong>Night altar calls.</strong> The room responding: hands, tears, the front filling.",
            "<strong>The city by day.</strong> Streets, markets, and skylines of the host city, so each instance can open with its own place.",
            "<strong>The host church serving.</strong> Local people running their own room: ministry of helps, prayer teams, setup.",
            "<strong>The empty venue.</strong> The room before anyone arrives, for the countdown and the record.",
        ],
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
        avatar="The 1 glyph in Flame, on its own Midnight plate. Published, and the only avatar this door uses.",
        handle="@every1movement, recorded in the Channels section of this guide.",
        kindhead="A movement brand.",
        kindtext="EVERY1 lives on phones and in other people's feeds. It carries the loosest rules "
                 "of the three, the strongest single glyph, and assets designed to be given away. "
                 "The full-bleed Midnight, the footage, and the pace are the right instincts; the "
                 "participation layer below is what makes it a movement.",
        capture=[
            "<strong>One-to-one, away from any stage.</strong> Two people and a Bible: workplaces, campuses, doorways, bus stops.",
            "<strong>The handoff.</strong> A believer giving something: a Bible, a meal, their time.",
            "<strong>Vertical first.</strong> Every key moment captured 9:16 alongside the horizontal frame, because this door is watched on phones.",
        ],
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
        typerule="Parchment on Word Blue. The most typographic door, with the recorded serif allowance for credentials.",
        flame="5% ceiling. Structure carries it, not colour.",
        register="A building. Ordered, sequential, institutional.",
        avatar="The seal, Parchment on Word Blue, once it is approved. Until then, the parent wordmark on Word Blue.",
        handle="@schoolofthelocalchurch, recorded in the Channels section of this guide.",
        kindhead="An institution.",
        kindtext="The School is credential-grade design: a seal, a certificate, a numbering system, "
                 "and the recorded serif allowance. A school signals permanence through type and "
                 "structure, so structure here is stated exactly, never implied.",
        capture=[
            "<strong>The classroom.</strong> Teaching sessions, open Bibles, pens moving.",
            "<strong>The materials.</strong> The course books and Bibles as objects, received and used.",
            "<strong>The credential moment.</strong> Graduates with certificates, named and consented, for the record.",
        ],
        why="TRAIN is the third movement, and the one that lasts. Fire that is not trained goes out. "
            "This door teaches believers their authority in Christ and how to build a real relationship "
            "with Jesus, starting with the free personal evangelism course.",
        rules=[
            "<strong>Structure carries the weight.</strong> Word Blue blocks, rules, and numbered sequence do the work that colour does elsewhere.",
            "<strong>The serif allowance.</strong> The only door that sets type in the parent's serif: credential and course titles, certificates, and diploma text, per Brand Guide &sect;11. Everything else stays DM Sans.",
            "<strong>The seal.</strong> The only door that carries one. Single colour, the School's own credentials only, never another door's work, never decoration.",
            "<strong>The most typographic door.</strong> Sessions, modules, and steps are numbered and ordered. If it can be a sequence, it is one.",
            "<strong>Flame at five percent.</strong> A school is not a rally. The fire is in what is taught, not in the layout.",
            "<strong>Everything is a record.</strong> Course names, session numbers, and dates are stated exactly, because a school that is vague about its own curriculum is not a school.",
        ],
        shots=[("slc-attendees-taking-notes","Attendees following the teaching with open Bibles and notebooks.","30 Jul 2026"),
               ("slc-bibles-received","Bibles and the personal evangelism course handed to attendees.","31 Jul 2026")],
    ),
]

# The published forms each door carries, in the order they are shown.
# `dir` is the folder under assets/logos/; a door absent from here has no approved
# mark and falls through to MARKSTATE instead.
MARKS = {
 "revival-to-my-city": ("rtmc", "A serif, and a bracket that is a blank to be filled.",
  "The wordmark is three faces converted to outlines: the swash <b>R</b> is Hello Paris, <b>EVIVAL</b> "
  "is ITC New Baskerville, and <b>TO MY CITY</b> is DM Sans, the house sans. The R&rsquo;s leg sweeps "
  "out and cradles the rest of the word, and that gesture is the mark. The Word Blue brackets around "
  "<b>MY CITY</b> are not decoration, they are a blank: this door&rsquo;s identity is the city instance, "
  "and the mark says so on its face.",
  "Hello Paris and ITC New Baskerville are licensed faces, not house fonts, and are installed nowhere. "
  "Nobody can re-set this mark, extend it, or add a word to it.",
  "Set in Hello Paris, ITC New Baskerville, and DM Sans, converted to outlines.", [
   ("rtmc-primary",          False, "Primary lockup",     "The mark. The default everywhere the name is introduced."),
   ("rtmc-primary-reversed", True,  "Reversed",           "Midnight grounds and footage carrying a scrim. One colour: the brackets go white, because Word Blue disappears on Midnight."),
   ("rtmc-cobrand",          False, "Co-brand lockup",    "THE WORD beside the door, divided by a hairline. This is how this door carries its endorsement, by showing the parent rather than stating it."),
   ("rtmc-cobrand-reversed", True,  "Co-brand, reversed", "The same lockup on Midnight and on scrimmed footage."),
   ("rtmc-primary-black",    False, "One colour",         "Embroidery, engraving, newsprint, and any vendor who asks for pure black."),
  ]),
 "every1": ("every1", "One word, and the 1 that leaves it.",
  "Heavy caps with the numeral drawn as its own shape, standing at a quarter again the cap height of "
  "EVERY and carrying the only Flame on the mark. The 1 is the same drawing in every form, which is "
  "what lets it leave the wordmark and still be the movement. Every form is vector, so it scales "
  "without limit and recolours by changing one fill value.",
  "Do not re-set it in another face, do not stretch it, and do not redraw the numeral by hand. The "
  "approved forms carry no endorsement line, so the surface sets that line itself.",
  "Set in DM Sans at weight 900, converted to outlines.", [
   ("every1-wordmark",          False, "Wordmark",            "The default wherever the name is introduced on a light ground."),
   ("every1-wordmark-reversed", True,  "Wordmark, reversed",  "Midnight grounds and footage carrying a scrim, which is where this door lives."),
   ("every1-vision",            False, "Vision lockup",       "The wordmark with the vision above and below, both lines tracked to its exact width."),
   ("every1-vision-reversed",   True,  "Vision lockup, reversed", "The same lockup for Midnight and for scrimmed footage."),
   ("every1-glyph",             True,  "The 1 glyph",         "The avatar. Stickers, watermarks, profile marks, and the planned app, with the parent invisible."),
   ("every1-app-icon",          False, "App icon",            "The glyph on its own Midnight plate, with the safe area the rounded corners need."),
  ]),
}


def marks_block(slug):
    dirname, head_line, lede, dont, setin, forms = MARKS[slug]
    rows = []
    for name, dark, label, note in forms:
        cls = "art dark" if dark else "art"
        rows.append('        <figure class="mark">')
        rows.append(f'          <div class="{cls}"><img src="/assets/logos/{dirname}/{name}.svg" alt="{label}"></div>')
        rows.append(f'          <figcaption class="lbl"><b>{label}</b>{note}</figcaption>')
        rows.append('        </figure>')
    head = [
        '    <div class="blk">',
        '      <div class="lab">The mark</div>',
        f'      <h2>{head_line}</h2>',
        f'      <p class="lede">{lede}</p>',
        '      <div class="marks">',
    ]
    tail = [
        '      </div>',
        f'      <div class="warn"><strong>{setin}</strong> '
        'The mark is artwork, not live text, so it never needs the font installed and never reflows. '
        f'{dont} If a size or colour you need does not exist, request it.</div>',
        '    </div>',
        '',
    ]
    return NL.join(head + rows + tail) + NL


# Door-specific system blocks, inserted after "Place in the journey".
# Each door is a different species of brand (Brand Guide §11), so each carries
# a different asset system: the event brand gets the city instance, the
# movement brand gets the participation layer, the institution gets the
# credential system.
EXTRAS = {
    "revival-to-my-city": """    <div class="blk">
      <div class="lab">The city instance</div>
      <h2>The unit of this identity.</h2>
      <p class="lede">Revival To My City is met on a poster before it is met in a room, so the unit of
      this identity is not a page. It is the city instance: the mark, a city, and a date, locked up
      as one announcement.</p>
      <div class="lockupdemo">
        <img src="/assets/logos/rtmc/rtmc-primary.svg" alt="Revival To My City, whose bracketed field holds the city name">
        <div class="cityline">[City] &middot; [Month Year]</div>
      </div>
      <p class="prov">The mark already carries the blank. <b>MY CITY</b> sits inside Word Blue brackets
      because it is the field a city fills: Kampala, Mbarara, Jinja. Replacing those two words is the
      only permitted change to the artwork, it is made once per instance from the record, and it is set
      in DM Sans to match the line it replaces. The date line beneath is letterspaced DM Sans caps. The
      lockup is never redrawn per city, and no other word in the mark ever moves.</p>
      <ul class="doorrules">
        <li><strong>The poster.</strong> The mark or the stage word, the city and date line, one action, and the endorsement, which is either the co-brand lockup or the line set beneath. Footage runs full bleed behind the Midnight scrim with White or Parchment type only, or the poster stays paper with Midnight type. The mark itself carries no Flame, so the 5% ceiling is spent on the surface: a rule, a numeral, one tick, and nothing more.</li>
        <li><strong>The stage backdrop.</strong> The reversed mark and the city line, nothing else. The room provides the colour.</li>
        <li><strong>The countdown.</strong> The poster reduced: mark, city and date line, and the days remaining as the only numeral on the surface.</li>
        <li><strong>The record.</strong> Every city instance is entered into the record, city, venue, dates, and host church, before anything is printed.</li>
      </ul>
    </div>

""",
    "every1": """    <div class="blk">
      <div class="lab">The participation layer</div>
      <h2>Assets designed to be given away.</h2>
      <p class="lede">A movement's identity lives on its people's own feeds, or it is not a movement.
      These assets exist to leave official hands.</p>
      <ul class="doorrules">
        <li><strong>The 1 is the glyph.</strong> The mark leads with the numeral, and the numeral is published on its own: an app icon, a profile badge, a sticker, a shape simple enough to survive at sixty pixels with no endorsement line in frame.</li>
        <li><strong>Share cards ride along.</strong> Every official EVERY1 surface ships with a version a member can post themselves: square and vertical, footage behind the scrim, one line of Parchment type.</li>
        <li><strong>The loosest rules in the house.</strong> Official surfaces follow this guide. What a member does with the badge on their own feed is not audited; it is the movement working.</li>
        <li><strong>The app icon comes first.</strong> The planned app follows the YouVersion model, so the glyph carries the whole identity with the parent invisible. It was drawn before the app was built, not after, and it is published here already.</li>
      </ul>
    </div>

""",
    "school-of-the-local-church": """    <div class="blk">
      <div class="lab">The credential system</div>
      <h2>Structure, stated exactly.</h2>
      <p class="lede">"Structure carries it" is measurable here, not a mood. The School's structure is
      a numbering system, a certificate, and the recorded serif allowance.</p>
      <ul class="doorrules">
        <li><strong>The serif allowance.</strong> Credential and course titles in DM Serif Display, diploma text in DM Serif Text, recorded in Brand Guide &sect;11. The only door permitted the parent's serif. Body copy, labels, and interfaces stay DM Sans.</li>
        <li><strong>The numbering system.</strong> Courses are numbered from SLC 101 upward, and inside a course the unit reads Module 04 &middot; Session 3. If it can be a sequence, it is one, and the numbers are stated exactly, because a school that is vague about its own curriculum is not a school.</li>
        <li><strong>The certificate.</strong> Letterhead paper, the student's name in serif, the course number and name, the completion date from the record, the two signatures, and the seal. Nothing else.</li>
        <li><strong>The wax.</strong> A presented credential may carry the physical seal, pressed in deep Ember-red wax or blind embossed. Wax is for the School's own credentials only.</li>
      </ul>
    </div>

""",
}

# Each door's channel facts card. The parent's card lives in Brand Guide §12;
# a door's card lives here, beside the identity it belongs to. Platforms a
# door does not list are carried by the parent's accounts.
CHANNELS = {
    "revival-to-my-city": dict(
        kind="Event brand · CLEAN",
        rows=[
            ("Home", "a named page under theword.world", True),
            ("Instagram", "@revivaltomycity", False),
            ("Facebook", "revivaltomycity", False),
            ("X", "@revivaltomycity", False),
            ("YouTube", "carried by the parent", True),
            ("TikTok", "carried by the parent", True),
        ],
    ),
    "every1": dict(
        kind="Movement brand · BURN",
        rows=[
            ("Home", "a named page under theword.world", True),
            ("Instagram", "@every1movement", False),
            ("TikTok", "@every1movement", False),
            ("YouTube", "@every1movement", False),
            ("Facebook", "every1movement", False),
            ("X", "@every1movement", False),
            ("App", "planned · YouVersion model", True),
        ],
    ),
    "school-of-the-local-church": dict(
        kind="Institution · TRAIN",
        rows=[
            ("Home", "a named page under theword.world", True),
            ("YouTube", "@schoolofthelocalchurch", False),
            ("Instagram", "@schoolofthelocalchurch", False),
            ("Facebook", "schoolofthelocalchurch", False),
            ("X", "carried by the parent", True),
            ("TikTok", "carried by the parent", True),
        ],
    ),
}


def channels_block(name: str, slug: str) -> str:
    chan = CHANNELS[slug]
    rows = ""
    for platform, handle, muted in chan["rows"]:
        cls = "cfh mut" if muted else "cfh"
        rows += f'          <tr><td class="cfp">{platform}</td><td class="{cls}">{handle}</td></tr>\n'
    return (
        '    <div class="blk">\n'
        '      <div class="lab">Channels</div>\n'
        '      <h2>Where this door is found.</h2>\n'
        '      <p class="lede">One label per platform, read the way an ingredients panel is read. This\n'
        '      door opens an account only on the platforms its kind of brand needs, so no channel goes\n'
        "      quiet. Anything not listed is carried by the parent, whose own channel facts live in\n"
        '      Brand Guide &sect;12.</p>\n'
        '      <div class="chanwrap">\n'
        '        <div class="chanfacts">\n'
        f'          <div class="cfname">{name}</div>\n'
        f'          <div class="cfserv">{chan["kind"]}</div>\n'
        '          <div class="cfbar"></div>\n'
        '          <table>\n'
        f"{rows}"
        '          </table>\n'
        '          <div class="cffoot">A ministry of THE WORD FOR ALL THE WORLD</div>\n'
        '        </div>\n'
        '      </div>\n'
        '      <p class="prov">These handles are the recorded standard, not a claim that every account\n'
        '      exists. Registration status is pending confirmation against the account record. A handle\n'
        '      that cannot be secured on a platform comes back here through a changelog entry, never as\n'
        '      an improvised variant.</p>\n'
        '    </div>\n'
        '\n'
    )


# Mark status for the doors whose mark is commissioned but not yet approved.
# Rendered in the {marks} slot that a door with published forms fills from MARKS.
MARKSTATE = {
    "school-of-the-local-church": """    <div class="blk">
      <div class="lab">The seal</div>
      <h2>Commissioned, not yet approved.</h2>
      <p class="lede">The School's mark is its academic seal, recorded in Brand Guide &sect;11: a shield
      bearing the Lion of Judah, ringed with the School's name, drawn in a single colour, with masters
      for print, blind emboss, and wax. It is ecclesiastical, not governmental, and it is the only seal
      in the house. It never appears on another door's work, and never as decoration to make a page
      feel official.</p>
      <div class="warn"><strong>Until the seal is approved and published here, the School's surfaces
      carry the parent wordmark beside the stage word TRAIN, and certificates close with the two
      signatures and the letterhead rule alone.</strong> No one draws an interim seal.</div>
    </div>

""",
}


DOOR_HERO = """<div class="door">
  <video autoplay muted loop playsinline poster="/assets/images/{video}-poster.jpg">
    <source src="/assets/videos/{video}.mp4" type="video/mp4">
  </video>
  <div class="scrim"></div>
  <div class="inner">
    <div class="panel">
      <div class="stageword">{stage}</div>
      <h1>{title}</h1>
      <p class="mission">{mission}</p>
      <div class="tickrule"><span class="ln"></span><span class="tk"></span><span class="ln"></span></div>
      <div class="endorse">A ministry of THE WORD FOR ALL THE WORLD</div>
    </div>
  </div>
</div>
"""

MARK_HERO = """<div class="markhero">
  <img src="/assets/logos/rtmc/rtmc-primary.svg" alt="Revival To My City">
  <p class="mission">{mission}</p>
</div>
<div class="filmband">
  <video autoplay muted loop playsinline poster="/assets/images/{video}-poster.jpg">
    <source src="/assets/videos/{video}.mp4" type="video/mp4">
  </video>
</div>
<div class="filmcap">Sanga, Mbarara &middot; 30 Jul 2026</div>
"""

MARK_DOOR_HERO = """<div class="door">
  <video autoplay muted loop playsinline poster="/assets/images/{video}-poster.jpg">
    <source src="/assets/videos/{video}.mp4" type="video/mp4">
  </video>
  <div class="scrim"></div>
  <div class="inner">
    <div class="panel">
      <div class="stageword">{stage}</div>
      <h1 class="markline"><img src="/assets/logos/every1/every1-wordmark-reversed.svg" alt="{name}"></h1>
      <p class="mission">{mission}</p>
      <div class="tickrule"><span class="ln"></span><span class="tk"></span><span class="ln"></span></div>
      <div class="endorse">A ministry of THE WORD FOR ALL THE WORLD</div>
    </div>
  </div>
</div>
"""

TRAIN_HERO = """<div class="trainhero">
  <div class="wrap">
    <div class="stageword">{stage}</div>
    <h1>{title}</h1>
    <p class="mission">{mission}</p>
    <div class="tickrule"><span class="ln"></span><span class="tk"></span><span class="ln"></span></div>
    <div class="endorse">A ministry of THE WORD FOR ALL THE WORLD</div>
  </div>
</div>
<div class="filmband">
  <video autoplay muted loop playsinline poster="/assets/images/{video}-poster.jpg">
    <source src="/assets/videos/{video}.mp4" type="video/mp4">
  </video>
</div>
<div class="filmcap">Sanga, Mbarara &middot; 30 Jul 2026</div>
"""


SUB_PAGE = """
{hero}
<main>
  <div class="wrap">
    <div class="docbar">
      <a href="/brand/#architecture">&larr; Brand Guide &sect;11</a>
      <a href="/documents/{slug}/">Messaging document &rarr;</a>
    </div>

    <div class="blk">
      <div class="lab">What kind of brand this is</div>
      <h2>{kindhead}</h2>
      <p class="lede">{kindtext}</p>
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
        <tr><th>Avatar</th><td>{avatar}</td></tr>
        <tr><th>Handle</th><td>{handle}</td></tr>
        <tr><th>Endorsement</th><td>Every surface carries the line <em>A ministry of THE WORD FOR ALL THE WORLD.</em> It is not optional.</td></tr>
      </table>
    </div>

    <div class="blk">
      <div class="lab">Place in the journey</div>
      <h2>Why this door exists.</h2>
      <p class="lede">{why}</p>
    </div>

{extras}    <div class="blk">
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
      <div class="lab">The capture brief</div>
      <h2>What this door still needs shot.</h2>
      <p class="lede">Today all three doors draw from one conference, so the three guides read as three
      views of one event. Three ministries need three libraries. These are the shots this door records
      next, and the brief is recorded as a gap in the asset record.</p>
      <ul class="doorrules">
{capture}      </ul>
    </div>

{marks}{channels}    <div class="blk">
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
    capture = "".join(f"        <li>{c}</li>\n" for c in d["capture"])
    fields = {k: v for k, v in d.items() if k not in ("rules", "shots", "capture")}
    fields["marks"] = marks_block(d["slug"]) if d["slug"] in MARKS else MARKSTATE.get(d["slug"], "")
    fields["extras"] = EXTRAS.get(d["slug"], "")
    fields["channels"] = channels_block(d["name"], d["slug"])
    if d["slug"] == "revival-to-my-city":
        tmpl = MARK_HERO
    elif d["slug"] == "school-of-the-local-church":
        tmpl = TRAIN_HERO
    elif d["slug"] == "every1":
        tmpl = MARK_DOOR_HERO
    else:
        tmpl = DOOR_HERO
    invert_nav = d["slug"] == "revival-to-my-city"
    fields["hero"] = tmpl.format(**fields)
    fields["capture"] = capture
    html = HEAD.format(title=f"{d['name']} · Initiative Brand Guide", extra_css=SUB_CSS,
                       navlogo=NAV_COBRAND if d["slug"] == "revival-to-my-city" else NAV_PARENT,
                       band_pad="0", doc_active="", lh_active="")
    html = html.replace("<body>", f"<body class=\"{d['stage'].lower()}\">")
    if invert_nav:
        html = html.replace("/assets/logos/the-word/the-word-horizontal-reversed.svg",
                            "/assets/logos/the-word/the-word-horizontal.svg", 1)
    html += SUB_PAGE.format(shots=shots, rules=rules, **fields)
    html += FOOT
    outdir = os.path.join(REPO, "brand", d["slug"])
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "index.html")
    open(path, "w").write(html)
    print(path, len(html))
