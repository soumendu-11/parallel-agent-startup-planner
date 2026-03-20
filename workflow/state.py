"""Shared state definition for the startup planning pipeline."""

from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages


class StartupPlannerState(TypedDict):
    """State flowing through the parallel research → synthesis pipeline.

    The 4 research nodes run in parallel, each writing to its own output field.
    The report_synthesis node reads all 4 and produces the final plan.
    """
    messages: Annotated[list, add_messages]

    # Input
    startup_idea: str          # Founder's startup idea / pitch
    industry: str              # Industry / sector for FMP lookups
    competitors: str           # Comma-separated competitor tickers or names

    # Parallel research outputs (written independently)
    market_research_output: str
    competitor_analysis_output: str
    financial_projection_output: str
    funding_landscape_output: str

    # Final synthesis
    final_report: str
    chart_paths: dict          # {chart_name: file_path}
