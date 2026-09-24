"""Run me: python lab.py"""
from netlab import report

raise SystemExit(
    report("switched", {"SW1": "sw1.ios"}, [("PC1", "PC3"), ("PC2", "PC4"), ("PC1", "PC2")])
)
