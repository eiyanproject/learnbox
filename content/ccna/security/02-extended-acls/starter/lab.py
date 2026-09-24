"""Run me: python lab.py"""
from netlab import report

raise SystemExit(
    report("edge", {"EDGE": "edge.ios", "ISP": "isp.ios"}, [("PC1", "WEB"), ("PC2", "WEB"), ("PC1", "203.0.113.1")])
)
