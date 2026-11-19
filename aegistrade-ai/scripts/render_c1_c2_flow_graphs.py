"""Render the implemented AegisTrade C1 and C2 research graphs.

C2 is a compiled LangGraph in ``aegistrade.agentic``. C1 deliberately uses a
single bounded specialist loop rather than pretending to have multiple agent
nodes. These diagrams therefore show the real control flow, tool loops and
deterministic gates instead of an invented agent topology.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets"
W, H = 1800, 1500


def font(size: int, bold: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


TITLE = font(48, True)
SUB = font(25)
NODE = font(25, True)
SMALL = font(19)
TINY = font(17)


def canvas(title: str, subtitle: str):
    image = Image.new("RGB", (W, H), "#F8FAFC")
    draw = ImageDraw.Draw(image)
    draw.text((70, 42), title, font=TITLE, fill="#0F172A")
    draw.text((72, 108), subtitle, font=SUB, fill="#475569")
    return image, draw


def centered(draw, box, text, font_obj, fill="#0F172A"):
    x1, y1, x2, y2 = box
    bounds = draw.multiline_textbbox((0, 0), text, font=font_obj, spacing=6, align="center")
    tw, th = bounds[2] - bounds[0], bounds[3] - bounds[1]
    draw.multiline_text(((x1 + x2 - tw) / 2, (y1 + y2 - th) / 2), text, font=font_obj, fill=fill, spacing=6, align="center")


def node(draw, box, label, fill="#FEF08A", outline="#52525B", oval=True, font_obj=NODE):
    if oval:
        draw.ellipse(box, fill=fill, outline=outline, width=4)
    else:
        draw.rounded_rectangle(box, radius=22, fill=fill, outline=outline, width=4)
    centered(draw, box, label, font_obj)


def arrow(draw, start, end, color="#334155", width=5, label=None, dashed=False):
    x1, y1 = start
    x2, y2 = end
    if dashed:
        length = math.hypot(x2 - x1, y2 - y1)
        ux, uy = (x2 - x1) / length, (y2 - y1) / length
        distance = 0
        while distance < length - 22:
            segment = min(15, length - 22 - distance)
            draw.line((x1 + ux * distance, y1 + uy * distance, x1 + ux * (distance + segment), y1 + uy * (distance + segment)), fill=color, width=width)
            distance += 26
    else:
        draw.line((start, end), fill=color, width=width)
    angle = math.atan2(y2 - y1, x2 - x1)
    size = 18
    points = [end, (x2 - size * math.cos(angle - .55), y2 - size * math.sin(angle - .55)), (x2 - size * math.cos(angle + .55), y2 - size * math.sin(angle + .55))]
    draw.polygon(points, fill=color)
    if label:
        bx = draw.textbbox((0, 0), label, font=TINY)
        tw, th = bx[2] - bx[0], bx[3] - bx[1]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        draw.rounded_rectangle((mx - tw / 2 - 8, my - th / 2 - 5, mx + tw / 2 + 8, my + th / 2 + 5), radius=7, fill="#F8FAFC")
        draw.text((mx - tw / 2, my - th / 2), label, font=TINY, fill="#475569")


def footer(draw, text):
    draw.line((70, 1430, 1730, 1430), fill="#CBD5E1", width=2)
    draw.text((70, 1450), text, font=TINY, fill="#64748B")


def render_c1():
    image, draw = canvas("AegisTrade C1 — Single-Agent Baseline", "One tool-using agent completes the same evidence-review task as C2; there is no independent LLM critic.")
    start = (720, 175, 1080, 265)
    plan = (665, 335, 1135, 445)
    agent = (585, 525, 1215, 675)
    tools = (80, 525, 450, 675)
    typed = (585, 785, 1215, 915)
    guard = (585, 1025, 1215, 1165)
    blocked = (80, 1240, 600, 1360)
    end = (1180, 1240, 1700, 1360)
    node(draw, start, "__start__", "#CDECF5")
    node(draw, plan, "Code-built plan\n(shared case and budget)", "#DBEAFE", oval=False)
    node(draw, agent, "single agent\nmarket + company + policy + route", "#FEF08A")
    node(draw, tools, "read-only tools\nmarket · company · policy · strategy", "#EDE9FE", oval=False, font_obj=SMALL)
    node(draw, typed, "SingleJudgement\ntyped hand-off", "#FDE68A", oval=False)
    node(draw, guard, "deterministic final guard\nschema · evidence · citations · route", "#DCFCE7", oval=False, font_obj=SMALL)
    node(draw, blocked, "BLOCKED / ABSTAIN\nauditable reason", "#FECACA")
    node(draw, end, "__end__\nvalidated C1 result", "#FDBA74")
    arrow(draw, (900, 265), (900, 335))
    arrow(draw, (900, 445), (900, 525))
    arrow(draw, (585, 590), (450, 590), "#7C3AED", label="tool call", dashed=True)
    arrow(draw, (450, 630), (585, 630), "#7C3AED", label="observation", dashed=True)
    arrow(draw, (900, 675), (900, 785))
    arrow(draw, (900, 915), (900, 1025))
    arrow(draw, (585, 1095), (340, 1240), "#DC2626", label="fails")
    arrow(draw, (1215, 1095), (1440, 1240), "#16A34A", label="passes")
    draw.text((80, 735), "The same agent may make a bounded schema/evidence correction and reuse observed tool results.", font=SMALL, fill="#475569")
    footer(draw, "Source: aegistrade/agentic.py · C1 branch · fixed tools, model family and inference ceiling used for the C1/C2 comparison")
    path = OUT / "c1_single_agent_flow.png"
    image.save(path, optimize=True)
    return path, image


def render_c2():
    image, draw = canvas("AegisTrade C2 — Multi-Agent LangGraph", "Supervisor plan → market specialist → strategy specialist → independent critic → deterministic final guard.")
    start = (720, 165, 1080, 245)
    plan = (650, 300, 1150, 405)
    market = (650, 475, 1150, 580)
    strategy = (650, 650, 1150, 755)
    critic = (650, 825, 1150, 930)
    guard = (600, 1020, 1200, 1145)
    tools = (1270, 475, 1720, 930)
    blocked = (80, 1240, 650, 1360)
    end = (1150, 1240, 1720, 1360)
    node(draw, start, "__start__", "#CDECF5")
    node(draw, plan, "supervisor plan\ntyped objective, steps and shared budget", "#DBEAFE", oval=False, font_obj=SMALL)
    node(draw, market, "market specialist\nsnapshot + dated company evidence", "#FEF08A", font_obj=SMALL)
    node(draw, strategy, "strategy specialist\npolicy RAG + code-approved route", "#FEF08A", font_obj=SMALL)
    node(draw, critic, "independent critic\nre-observes evidence; accept or reject", "#FEF08A", font_obj=SMALL)
    node(draw, guard, "deterministic final guard\ntyped hand-offs · evidence · dates · citations · route · critic", "#DCFCE7", oval=False, font_obj=SMALL)
    node(draw, tools, "bounded read-only tools\n\nmarket_snapshot\ncompany_evidence\nsearch_dated_web\nsearch_policy\ncheck_strategy\n\nTools never size or submit orders.", "#EDE9FE", oval=False, font_obj=SMALL)
    node(draw, blocked, "BLOCKED / ABSTAIN / PAUSE\nauditable failure category", "#FECACA", font_obj=SMALL)
    node(draw, end, "__end__\nvalidated C2 research", "#FDBA74")
    arrow(draw, (900, 245), (900, 300))
    arrow(draw, (900, 405), (900, 475))
    arrow(draw, (900, 580), (900, 650))
    arrow(draw, (900, 755), (900, 825))
    arrow(draw, (900, 930), (900, 1020))
    for y in (525, 700, 875):
        arrow(draw, (1150, y), (1270, y), "#7C3AED", label="read", dashed=True)
    arrow(draw, (600, 1085), (365, 1240), "#DC2626", label="fails / critic rejects")
    arrow(draw, (1200, 1085), (1435, 1240), "#16A34A", label="passes")
    footer(draw, "Source: aegistrade/agentic.py · compiled StateGraph nodes: plan, market, strategy, critic · deterministic validation follows graph output")
    path = OUT / "c2_multi_agent_langgraph_flow.png"
    image.save(path, optimize=True)
    return path, image


def comparison(c1, c2):
    scale = 0.64
    left = c1.resize((int(W * scale), int(H * scale)), Image.Resampling.LANCZOS)
    right = c2.resize((int(W * scale), int(H * scale)), Image.Resampling.LANCZOS)
    margin = 35
    image = Image.new("RGB", (left.width + right.width + margin * 3, left.height + margin * 2), "#E2E8F0")
    image.paste(left, (margin, margin))
    image.paste(right, (left.width + margin * 2, margin))
    path = OUT / "c1_c2_flow_comparison.png"
    image.save(path, optimize=True)
    return path


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    c1_path, c1 = render_c1()
    c2_path, c2 = render_c2()
    combined = comparison(c1, c2)
    print(c1_path)
    print(c2_path)
    print(combined)


if __name__ == "__main__":
    main()
