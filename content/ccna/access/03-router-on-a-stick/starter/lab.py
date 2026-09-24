"""Run me: python lab.py"""
from netlab import report

raise SystemExit(
    report("router-on-a-stick", {"SW1": "sw1.ios", "R1": "r1.ios"}, [("PC1", "PC2"), ("PC1", "10.0.10.1"), ("PC2", "10.0.20.1")])
)
