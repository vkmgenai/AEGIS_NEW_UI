"""Evaluation utilities. Do NOT mistake auto-generated fixtures for independent human-labelled gold."""
from __future__ import annotations
import random
from .safety import OrderProposal, RiskInputs, RiskParameters, validate_risk


def make_risk_fixtures(seed: int = 97) -> list[dict]:
    """60 boundary/negative synthetic examples for unit-test *development*, not an independent gold set."""
    rng=random.Random(seed)
    cases=[]
    for i in range(60):
        px=rng.choice([100,500,1000])
        stop=px-rng.choice([1,10,25,50])
        qty=rng.choice([1,5,10,25,50,1000])
        if i % 7 == 0: stop=px+2
        if i % 11 == 0: qty=1000
        cases.append({"id":f"RISK-{i+1:03d}","price":px,"stop":stop,"qty":qty,
                      "cash":rng.choice([100,5000,100000]),"equity":100000,
                      "purpose":"development-fuzz-fixture" if i<20 else "candidate-held-out:human-label-required"})
    return cases


def score_accepted_lessons(before: list[bool], after: list[bool]) -> dict:
    if len(before)!=len(after) or not before:
        raise ValueError("Provide aligned nonempty held-out cases")
    return {"cases":len(before),"correct_without":sum(before),"correct_with":sum(after),
            "accuracy_difference_pp":round((sum(after)-sum(before))*100/len(before),2)}
