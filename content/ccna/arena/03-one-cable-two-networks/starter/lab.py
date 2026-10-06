"""Run me: python lab.py"""
from netlab import report

raise SystemExit(
    report(
        "router-on-a-stick",
        {"SW1": "sw1.ios", "R1": "r1.ios"},
        [("PC1", "PC2"), ("PC2", "PC1")],
    )
)
