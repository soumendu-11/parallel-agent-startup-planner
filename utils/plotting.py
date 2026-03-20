"""Chart generation utilities for startup planning reports."""

import os
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def _style_chart(ax, title: str):
    """Apply consistent styling to charts."""
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(labelsize=10)


def generate_market_size_chart(market_data: dict) -> str:
    """Generate TAM/SAM/SOM funnel chart.

    market_data: {"tam": float, "sam": float, "som": float, "unit": str}
    """
    fig, ax = plt.subplots(figsize=(8, 5))

    labels = ["TAM\n(Total Addressable)", "SAM\n(Serviceable Addressable)", "SOM\n(Serviceable Obtainable)"]
    values = [market_data.get("tam", 100), market_data.get("sam", 30), market_data.get("som", 5)]
    unit = market_data.get("unit", "$B")
    colors = ["#4A90D9", "#7BC67E", "#F5A623"]

    bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1], height=0.6, edgecolor="white", linewidth=2)
    for bar, val in zip(bars, values[::-1]):
        ax.text(bar.get_width() + max(values) * 0.02, bar.get_y() + bar.get_height() / 2,
                f"{val} {unit}", va="center", fontsize=12, fontweight="bold")

    _style_chart(ax, "Market Sizing Analysis")
    ax.set_xlabel(f"Market Size ({unit})", fontsize=11)
    ax.set_xlim(0, max(values) * 1.3)

    path = os.path.join(OUTPUT_DIR, "market_size.png")
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def generate_financial_projection_chart(projections: dict) -> str:
    """Generate revenue/cost projection chart.

    projections: {"years": [1,2,3,4,5], "revenue": [...], "costs": [...], "unit": str}
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    years = projections.get("years", [1, 2, 3, 4, 5])
    revenue = projections.get("revenue", [0.5, 2, 5, 12, 25])
    costs = projections.get("costs", [1.5, 2.5, 3.5, 5, 8])
    unit = projections.get("unit", "$M")

    x = np.arange(len(years))
    width = 0.35

    bars1 = ax.bar(x - width / 2, revenue, width, label="Revenue", color="#4A90D9", edgecolor="white")
    bars2 = ax.bar(x + width / 2, costs, width, label="Costs", color="#E74C3C", edgecolor="white", alpha=0.8)

    # Profit/loss line
    profit = [r - c for r, c in zip(revenue, costs)]
    ax.plot(x, profit, "o--", color="#2ECC71", linewidth=2, markersize=8, label="Net Profit/Loss", zorder=5)
    ax.axhline(y=0, color="gray", linestyle="-", linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels([f"Year {y}" for y in years])
    ax.set_ylabel(f"Amount ({unit})", fontsize=11)
    ax.legend(fontsize=10, loc="upper left")
    _style_chart(ax, "5-Year Financial Projections")

    for bar in bars1:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                f"{bar.get_height():.1f}", ha="center", fontsize=9)

    path = os.path.join(OUTPUT_DIR, "financial_projections.png")
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def generate_competitor_landscape_chart(competitors: dict) -> str:
    """Generate competitor positioning scatter chart.

    competitors: {"names": [...], "market_share": [...], "growth_rate": [...]}
    """
    fig, ax = plt.subplots(figsize=(10, 7))

    names = competitors.get("names", ["Competitor A", "Competitor B", "Our Startup"])
    market_share = competitors.get("market_share", [30, 25, 5])
    growth_rate = competitors.get("growth_rate", [5, 8, 40])

    colors = ["#E74C3C"] * (len(names) - 1) + ["#4A90D9"]
    sizes = [s * 30 + 100 for s in market_share]

    scatter = ax.scatter(market_share, growth_rate, s=sizes, c=colors, alpha=0.7, edgecolors="white", linewidth=2)

    for i, name in enumerate(names):
        ax.annotate(name, (market_share[i], growth_rate[i]),
                    textcoords="offset points", xytext=(10, 10),
                    fontsize=10, fontweight="bold" if i == len(names) - 1 else "normal")

    ax.set_xlabel("Market Share (%)", fontsize=11)
    ax.set_ylabel("Growth Rate (%)", fontsize=11)
    _style_chart(ax, "Competitive Landscape")

    path = os.path.join(OUTPUT_DIR, "competitor_landscape.png")
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def generate_funding_timeline_chart(funding: dict) -> str:
    """Generate funding rounds timeline chart.

    funding: {"rounds": ["Pre-seed", "Seed", ...], "amounts": [...], "timelines": [...]}
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    rounds = funding.get("rounds", ["Pre-seed", "Seed", "Series A"])
    amounts = funding.get("amounts", [0.5, 2.5, 10])
    unit = funding.get("unit", "$M")

    colors = ["#F39C12", "#E67E22", "#D35400", "#C0392B", "#8E44AD"]
    bars = ax.bar(rounds, amounts, color=colors[:len(rounds)], edgecolor="white", linewidth=2, width=0.5)

    for bar, amt in zip(bars, amounts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + max(amounts) * 0.02,
                f"{amt} {unit}", ha="center", fontsize=12, fontweight="bold")

    _style_chart(ax, "Funding Roadmap")
    ax.set_ylabel(f"Amount ({unit})", fontsize=11)

    path = os.path.join(OUTPUT_DIR, "funding_timeline.png")
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def generate_report_charts(chart_data: dict) -> dict:
    """Generate all charts from structured data. Returns dict of chart_name -> file_path.

    chart_data should contain keys: market_size, financial_projections, competitors, funding
    Each value is a dict matching the respective chart function's expected input.
    """
    paths = {}

    if "market_size" in chart_data:
        paths["market_size"] = generate_market_size_chart(chart_data["market_size"])

    if "financial_projections" in chart_data:
        paths["financial_projections"] = generate_financial_projection_chart(chart_data["financial_projections"])

    if "competitors" in chart_data:
        paths["competitors"] = generate_competitor_landscape_chart(chart_data["competitors"])

    if "funding" in chart_data:
        paths["funding"] = generate_funding_timeline_chart(chart_data["funding"])

    return paths
