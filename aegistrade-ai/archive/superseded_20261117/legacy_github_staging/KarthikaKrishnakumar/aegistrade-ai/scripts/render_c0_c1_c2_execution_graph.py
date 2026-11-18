"""Render the implemented C0/C1/C2 research-execution comparison.

This is intentionally generated without Graphviz so it works in the project's
standard local environment.  The labels mirror aegistrade/llm_research.py and
aegistrade/agentic.py; the shared governed action path mirrors workflow.py.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets" / "c0_c1_c2_execution_graph.png"
W, H = 2400, 1700


def font(size: int, bold: bool = False):
    names = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for name in names:
        if Path(name).exists():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


F_TITLE = font(52, True)
F_SUB = font(27)
F_HEAD = font(32, True)
F_BOX = font(24, True)
F_SMALL = font(20)
F_TINY = font(18)


img = Image.new("RGB", (W, H), "#F8FAFC")
d = ImageDraw.Draw(img)


def rounded(box, fill, outline="#CBD5E1", width=3, radius=22):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def center_text(box, title, lines=(), title_fill="#0F172A"):
    x1, y1, x2, y2 = box
    title_box = d.textbbox((0, 0), title, font=F_BOX)
    ty = y1 + 18
    d.text(((x1 + x2 - title_box[2]) / 2, ty), title, font=F_BOX, fill=title_fill)
    ty += title_box[3] + 9
    for line in lines:
        bb = d.textbbox((0, 0), line, font=F_SMALL)
        d.text(((x1 + x2 - bb[2]) / 2, ty), line, font=F_SMALL, fill="#334155")
        ty += 28


def arrow(start, end, color="#64748B", width=5, label=None):
    d.line((start, end), fill=color, width=width)
    import math
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    size = 16
    p1 = (end[0] - size * math.cos(angle - .55), end[1] - size * math.sin(angle - .55))
    p2 = (end[0] - size * math.cos(angle + .55), end[1] - size * math.sin(angle + .55))
    d.polygon((end, p1, p2), fill=color)
    if label:
        mx, my = (start[0] + end[0]) / 2, (start[1] + end[1]) / 2
        bb = d.textbbox((0, 0), label, font=F_TINY)
        d.rounded_rectangle((mx-bb[2]/2-8, my-bb[3]/2-5, mx+bb[2]/2+8, my+bb[3]/2+5), 7, fill="#F8FAFC")
        d.text((mx-bb[2]/2, my-bb[3]/2), label, font=F_TINY, fill="#475569")


d.text((80, 42), "AegisTrade AI — C0, C1 and C2 Execution Graph", font=F_TITLE, fill="#0F172A")
d.text((82, 112), "Same locked historical case and evidence tools; increasing agentic capability. No path places a live order.", font=F_SUB, fill="#475569")

# Shared input
shared = (680, 180, 1720, 285)
rounded(shared, "#E0F2FE", "#0284C7")
center_text(shared, "Locked historical research case", ("symbol + decision date + indicators + approved code route",))

cols = [(80, 760), (820, 1560), (1620, 2320)]
headers = [
    ("C0 — deterministic baseline", "0 LLM calls", "#E2E8F0", "#475569"),
    ("C1 — single-agent baseline", "1 tool-using agent; no independent LLM critic", "#FEF3C7", "#D97706"),
    ("C2 — multi-agent system", "supervisor + 3 bounded specialists", "#DCFCE7", "#16A34A"),
]
for (x1, x2), (title, sub, fill, outline) in zip(cols, headers):
    box = (x1, 345, x2, 445)
    rounded(box, fill, outline)
    center_text(box, title, (sub,))
    arrow(((shared[0]+shared[2])/2, shared[3]), ((x1+x2)/2, box[1]), outline, 4)

# C0
c0a=(145,500,695,610); c0b=(145,690,695,815); c0c=(145,895,695,1020)
rounded(c0a,"#F1F5F9"); center_text(c0a,"Technical ROUTER",("EMA Trend · EMA Pullback", "RSI Reversion · Breakout"))
rounded(c0b,"#F1F5F9"); center_text(c0b,"Deterministic retrieval",("policy RAG + company coverage report", "no semantic LLM assessment"))
rounded(c0c,"#F1F5F9"); center_text(c0c,"Code reference result",("selected route = code-approved route", "typed metrics; reproducible baseline"))
arrow((420,610),(420,690)); arrow((420,815),(420,895))

# C1
c1a=(895,500,1485,615); c1b=(895,700,1485,850); c1c=(895,935,1485,1060)
rounded(c1a,"#FFFBEB","#F59E0B"); center_text(c1a,"Single tool-using LLM agent",("market + company + policy + route tools", "shared call / token / context budgets"))
rounded(c1b,"#FFFBEB","#F59E0B"); center_text(c1b,"One typed judgement",("company assessment + strategy + citations", "ENTER / HOLD / EXIT / SCREEN"))
rounded(c1c,"#FFF7ED","#EA580C"); center_text(c1c,"Deterministic final guard",("schema · route · citation · evidence checks", "no independent LLM critic"))
arrow((1190,615),(1190,700),"#D97706"); arrow((1190,850),(1190,935),"#D97706")

# C2
c2p=(1675,485,2265,580); c2m=(1675,650,2265,775); c2s=(1675,845,2265,970); c2c=(1675,1040,2265,1165); c2g=(1675,1235,2265,1360)
rounded(c2p,"#ECFDF5","#16A34A"); center_text(c2p,"Supervisor plan",("bounded roles, tools and shared budget",))
rounded(c2m,"#ECFDF5","#16A34A"); center_text(c2m,"Market specialist",("snapshot + dated company evidence", "optional bounded historical web fallback"))
rounded(c2s,"#ECFDF5","#16A34A"); center_text(c2s,"Strategy specialist",("policy RAG + code route", "typed strategy and cited explanation"))
rounded(c2c,"#ECFDF5","#16A34A"); center_text(c2c,"Independent critic",("own policy / company observations", "accept or reject; cannot execute"))
rounded(c2g,"#F0FDF4","#15803D"); center_text(c2g,"Deterministic final guard",("typed handoffs · evidence · citations · critic", "fail closed or validated C2 research"))
for a,b in [(c2p,c2m),(c2m,c2s),(c2s,c2c),(c2c,c2g)]: arrow(((a[0]+a[2])/2,a[3]),((b[0]+b[2])/2,b[1]),"#16A34A")

# Failure paths
fail=(85,1250,1485,1360)
rounded(fail,"#FEE2E2","#DC2626")
center_text(fail,"Abstain / block / pause with an auditable reason",("no signal · insufficient or adverse evidence · invalid output · critic rejection · budget/provider failure",))
arrow((420,1020),(420,1250),"#DC2626",4,"if ineligible")
arrow((1190,1060),(1190,1250),"#DC2626",4,"if guard fails")
arrow((1675,1297),(1485,1297),"#DC2626",4,"if guard fails")

# Shared governed action path
action=(175,1450,2225,1640)
rounded(action,"#EDE9FE","#7C3AED",4)
center_text(action,"Shared governed simulated-action path (only after validated C2 research)",(
    "order proposal → deterministic risk/code critic → exact-payload human approve/edit/reject",
    "→ final freshness and risk checks → simulated broker submission → audit ledger",
    "C0/C1 experiment outputs measure baselines; they do not authorize an order.",
))
arrow((1970,1360),(1970,1450),"#7C3AED",5,"validated C2 only")

OUT.parent.mkdir(parents=True, exist_ok=True)
img.save(OUT, optimize=True)
print(OUT)
