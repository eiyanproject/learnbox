"""Run me: python lab.py"""
from netlab import report

raise SystemExit(
    report("edge", {"EDGE": "edge.ios", "ISP": "isp.ios"}, [("PC1", "WEB"), ("PC2", "WEB")])
)
