"""Run me: python lab.py"""
from netlab import report

raise SystemExit(
    report(
        "branch",
        {"R1": "r1.ios", "R2": "r2.ios", "R3": "r3.ios"},
        [("PC1", "SRV"), ("SRV", "PC1")],
    )
)
