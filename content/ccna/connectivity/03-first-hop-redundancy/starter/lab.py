"""Run me: python lab.py"""
from netlab import report

raise SystemExit(
    report("redundant", {"R1": "r1.ios", "R2": "r2.ios", "CORE": "core.ios"}, [("PC1", "192.168.1.254"), ("PC1", "SRV")])
)
