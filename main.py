"""
Startup Planning Pipeline — Entry Point

Runs a parallel LangGraph pipeline with 4 research agents (using FMP MCP
and Tavily Search MCP tools) that fan-in to a report synthesis node.

Usage:
    python main.py
    python main.py --idea "Your startup idea" --industry "Healthcare" --competitors "TDOC,AMWL"
"""

import argparse
import os
import sys

from workflow import stream_startup_planner


DEFAULT_STARTUP_IDEA = """
I want to build a satellite imagery analytics company. The idea is to use AI to process
satellite images and provide actionable insights for agriculture, urban planning,
and environmental monitoring.

We'd offer an API and dashboard where customers upload coordinates or draw regions
on a map, and we return analyzed imagery with change detection, crop health scores,
deforestation alerts, and urban expansion tracking.

Key capabilities:
- Multi-spectral image analysis (NDVI, thermal, SAR)
- Change detection over time (weekly/monthly comparisons)
- AI-powered anomaly detection (illegal mining, deforestation, urban encroachment)
- Custom alerts and automated reporting
- API-first with a visual dashboard overlay

Target customers: Agricultural enterprises, government agencies, insurance companies,
environmental NGOs, mining companies, and real estate developers.

Revenue model: SaaS subscription with tiered pricing based on area coverage and
refresh frequency — $499/mo (Starter: 100 sq km), $1,999/mo (Pro: 1,000 sq km),
$4,999/mo (Enterprise: unlimited with custom SLA).
"""


def main():
    parser = argparse.ArgumentParser(description="Startup Planning Pipeline")
    parser.add_argument("--idea", type=str, default=DEFAULT_STARTUP_IDEA,
                        help="Your startup idea / pitch")
    parser.add_argument("--industry", type=str, default="Technology",
                        help="Industry sector (for FMP lookups)")
    parser.add_argument("--competitors", type=str, default="PL,MAXR,BKSY",
                        help="Comma-separated competitor tickers")
    args = parser.parse_args()

    print("=" * 80)
    print("🚀 STARTUP PLANNING PIPELINE")
    print("=" * 80)
    print(f"\n📝 STARTUP IDEA:\n{args.idea.strip()}")
    print(f"\n🏭 INDUSTRY: {args.industry}")
    print(f"🏢 COMPETITORS: {args.competitors}")
    print("\n" + "=" * 80)
    print("Launching parallel research agents...")
    print("  📊 Market Research Agent     (Tavily Search)")
    print("  🔍 Competitor Analysis Agent (FMP + Tavily Search)")
    print("  💰 Financial Projection Agent (FMP + Tavily Search)")
    print("  🏦 Funding Landscape Agent   (Tavily Search)")
    print("=" * 80 + "\n")

    chart_paths = {}

    for node_name, output in stream_startup_planner(
        startup_idea=args.idea,
        industry=args.industry,
        competitors=args.competitors,
    ):
        # Print node header
        node_labels = {
            "market_research": "📊 MARKET RESEARCH",
            "competitor_analysis": "🔍 COMPETITOR ANALYSIS",
            "financial_projection": "💰 FINANCIAL PROJECTIONS",
            "funding_landscape": "🏦 FUNDING LANDSCAPE",
            "report_synthesis": "📋 FINAL STARTUP PLAN",
        }
        label = node_labels.get(node_name, node_name.upper())
        print(f"\n{'='*80}")
        print(f"  {label} — COMPLETE")
        print(f"{'='*80}\n")

        # Print messages
        if "messages" in output:
            for msg in output["messages"]:
                content = msg.content if hasattr(msg, "content") else msg.get("content", "")
                print(content)
                print("\n" + "-" * 80 + "\n")

        # Collect chart paths
        if "chart_paths" in output and output["chart_paths"]:
            chart_paths = output["chart_paths"]

    # Summary
    print("\n" + "=" * 80)
    print("✅ STARTUP PLAN COMPLETE")
    print("=" * 80)

    if chart_paths:
        print("\n📈 Generated Charts:")
        for name, path in chart_paths.items():
            print(f"  • {name.replace('_', ' ').title()}: {path}")

    outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
    print(f"\n📁 All outputs saved to: {outputs_dir}")
    print("=" * 80)


if __name__ == "__main__":
    main()
