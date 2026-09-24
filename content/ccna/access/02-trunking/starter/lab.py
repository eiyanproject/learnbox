"""Run me: python lab.py"""
from netlab import report

raise SystemExit(
    report("two-switches", {"SW1": "sw1.ios", "SW2": "sw2.ios"}, [("PC1", "PC3"), ("PC2", "PC4"), ("PC1", "PC2")])
)
