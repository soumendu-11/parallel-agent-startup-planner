"""
LangGraph parallel research pipeline for startup planning.

Graph structure (fan-out / fan-in):

  ┌──────────────────────────────────────────────────────────────┐
  │                        START                                 │
  │                          │                                   │
  │     ┌──────────┬─────────┼──────────┬──────────┐            │
  │     ▼          ▼         ▼          ▼          │            │
  │  market    competitor  financial  funding      │            │
  │  research  analysis   projection landscape    │            │
  │     │          │         │          │          │            │
  │     └──────────┴─────────┼──────────┘          │            │
  │                          ▼                     │            │
  │                   report_synthesis             │            │
  │                          │                     │            │
  │                         END                    │            │
  └──────────────────────────────────────────────────────────────┘

All 4 research nodes run in PARALLEL to minimize latency.
Each node is a ReAct agent with access to specific MCP tools.
"""

import json
import re
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import create_react_agent

from workflow.state import StartupPlannerState
from skills import (
    MARKET_RESEARCH_SKILL,
    COMPETITOR_ANALYSIS_SKILL,
    FINANCIAL_PROJECTION_SKILL,
    FUNDING_LANDSCAPE_SKILL,
    REPORT_SYNTHESIZER_SKILL,
)
from mcp_servers import (
    get_market_research_tools,
    get_competitor_analysis_tools,
    get_financial_projection_tools,
    get_funding_landscape_tools,
)
from utils.llm import get_llm
from utils.plotting import generate_report_charts


# ── Helper: extract JSON chart data from LLM output ─────────────────

def _extract_chart_data(text: str) -> dict:
    """Extract JSON block after CHART_DATA marker."""
    pattern = r'```json\s*\n(.*?)\n\s*```'
    matches = re.findall(pattern, text, re.DOTALL)
    for match in reversed(matches):
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    return {}


# ── Research Nodes (L1 — run in parallel) ────────────────────────────

def _build_research_prompt(state: dict, skill: dict) -> str:
    """Build the task prompt for a research node."""
    idea = state["startup_idea"]
    industry = state.get("industry", "Technology")
    competitors = state.get("competitors", "")

    return f"""Analyze this startup idea thoroughly using your available tools.

## Startup Idea
{idea}

## Industry / Sector
{industry}

## Known Competitors (if any)
{competitors if competitors else "Research and identify competitors yourself."}

---

Use your tools to gather REAL data. Make multiple tool calls to build a comprehensive analysis.
Follow your output structure exactly. Include the CHART_DATA JSON block at the end."""


def market_research_node(state: dict) -> dict:
    """Market Research Analyst — uses Tavily Search for market sizing & trends."""
    llm = get_llm()
    tools = get_market_research_tools()
    agent = create_react_agent(llm, tools)

    prompt = _build_research_prompt(state, MARKET_RESEARCH_SKILL)
    result = agent.invoke({
        "messages": [
            {"role": "system", "content": MARKET_RESEARCH_SKILL["system_prompt"]},
            {"role": "user", "content": prompt},
        ]
    })

    output = result["messages"][-1].content
    tagged = f"{MARKET_RESEARCH_SKILL['emoji']} **{MARKET_RESEARCH_SKILL['title']}**\n\n{output}"

    return {
        "messages": [{"role": "assistant", "content": tagged}],
        "market_research_output": output,
    }


def competitor_analysis_node(state: dict) -> dict:
    """Competitor Intelligence Analyst — uses FMP + Tavily Search for competitive intel."""
    llm = get_llm()
    tools = get_competitor_analysis_tools()
    agent = create_react_agent(llm, tools)

    prompt = _build_research_prompt(state, COMPETITOR_ANALYSIS_SKILL)
    result = agent.invoke({
        "messages": [
            {"role": "system", "content": COMPETITOR_ANALYSIS_SKILL["system_prompt"]},
            {"role": "user", "content": prompt},
        ]
    })

    output = result["messages"][-1].content
    tagged = f"{COMPETITOR_ANALYSIS_SKILL['emoji']} **{COMPETITOR_ANALYSIS_SKILL['title']}**\n\n{output}"

    return {
        "messages": [{"role": "assistant", "content": tagged}],
        "competitor_analysis_output": output,
    }


def financial_projection_node(state: dict) -> dict:
    """Financial Projection Analyst — uses FMP for comparable financials."""
    llm = get_llm()
    tools = get_financial_projection_tools()
    agent = create_react_agent(llm, tools)

    prompt = _build_research_prompt(state, FINANCIAL_PROJECTION_SKILL)
    result = agent.invoke({
        "messages": [
            {"role": "system", "content": FINANCIAL_PROJECTION_SKILL["system_prompt"]},
            {"role": "user", "content": prompt},
        ]
    })

    output = result["messages"][-1].content
    tagged = f"{FINANCIAL_PROJECTION_SKILL['emoji']} **{FINANCIAL_PROJECTION_SKILL['title']}**\n\n{output}"

    return {
        "messages": [{"role": "assistant", "content": tagged}],
        "financial_projection_output": output,
    }


def funding_landscape_node(state: dict) -> dict:
    """Funding Landscape Analyst — uses Tavily Search for funding intel."""
    llm = get_llm()
    tools = get_funding_landscape_tools()
    agent = create_react_agent(llm, tools)

    prompt = _build_research_prompt(state, FUNDING_LANDSCAPE_SKILL)
    result = agent.invoke({
        "messages": [
            {"role": "system", "content": FUNDING_LANDSCAPE_SKILL["system_prompt"]},
            {"role": "user", "content": prompt},
        ]
    })

    output = result["messages"][-1].content
    tagged = f"{FUNDING_LANDSCAPE_SKILL['emoji']} **{FUNDING_LANDSCAPE_SKILL['title']}**\n\n{output}"

    return {
        "messages": [{"role": "assistant", "content": tagged}],
        "funding_landscape_output": output,
    }


# ── Synthesis Node (L0 — runs after all research completes) ─────────

def report_synthesis_node(state: dict) -> dict:
    """Chief Strategy Officer — synthesizes all research into final startup plan with charts."""
    llm = get_llm(temperature=0.3)

    prompt = f"""You have received research from 4 analysts. Synthesize into a complete startup plan.

## Original Startup Idea
{state["startup_idea"]}

---

## 📊 Market Research Analyst Report
{state.get("market_research_output", "No data available.")}

---

## 🔍 Competitor Intelligence Report
{state.get("competitor_analysis_output", "No data available.")}

---

## 💰 Financial Projections Report
{state.get("financial_projection_output", "No data available.")}

---

## 🏦 Funding Landscape Report
{state.get("funding_landscape_output", "No data available.")}

---

Now synthesize all findings into a cohesive startup plan following your output structure.
Include a combined CHART_DATA JSON block at the end with all chart data merged."""

    response = llm.invoke([
        {"role": "system", "content": REPORT_SYNTHESIZER_SKILL["system_prompt"]},
        {"role": "user", "content": prompt},
    ])

    report = response.content

    # Extract chart data from all outputs and the synthesis
    all_chart_data = {}
    for output_field in ["market_research_output", "competitor_analysis_output",
                         "financial_projection_output", "funding_landscape_output"]:
        field_data = _extract_chart_data(state.get(output_field, ""))
        all_chart_data.update(field_data)

    # Override with synthesizer's chart data if present
    synth_chart_data = _extract_chart_data(report)
    all_chart_data.update(synth_chart_data)

    # Generate charts
    chart_paths = {}
    if all_chart_data:
        try:
            chart_paths = generate_report_charts(all_chart_data)
        except Exception as e:
            report += f"\n\n⚠️ Chart generation error: {e}"

    tagged = f"📋 **{REPORT_SYNTHESIZER_SKILL['title']}**\n\n{report}"

    if chart_paths:
        tagged += "\n\n---\n### 📈 Generated Charts\n"
        for name, path in chart_paths.items():
            tagged += f"- **{name.replace('_', ' ').title()}**: `{path}`\n"

    return {
        "messages": [{"role": "assistant", "content": tagged}],
        "final_report": report,
        "chart_paths": chart_paths,
    }


# ── Graph Construction ────────────────────────────────────────────────

def build_startup_planner() -> object:
    """Build the parallel research → synthesis graph.

    Fan-out: START → [market_research, competitor_analysis, financial_projection, funding_landscape]
    Fan-in:  all 4 → report_synthesis → END
    """
    graph = StateGraph(StartupPlannerState)

    # Add all nodes
    graph.add_node("market_research", market_research_node)
    graph.add_node("competitor_analysis", competitor_analysis_node)
    graph.add_node("financial_projection", financial_projection_node)
    graph.add_node("funding_landscape", funding_landscape_node)
    graph.add_node("report_synthesis", report_synthesis_node)

    # Fan-out: START triggers all 4 research nodes in parallel
    graph.add_edge(START, "market_research")
    graph.add_edge(START, "competitor_analysis")
    graph.add_edge(START, "financial_projection")
    graph.add_edge(START, "funding_landscape")

    # Fan-in: all 4 research nodes feed into report synthesis
    graph.add_edge("market_research", "report_synthesis")
    graph.add_edge("competitor_analysis", "report_synthesis")
    graph.add_edge("financial_projection", "report_synthesis")
    graph.add_edge("funding_landscape", "report_synthesis")

    # End
    graph.add_edge("report_synthesis", END)

    return graph.compile()


# ── Runners ───────────────────────────────────────────────────────────


def run_startup_planner(startup_idea: str, industry: str = "Technology",
                        competitors: str = "") -> dict:
    """Run the full startup planning pipeline and return final state."""
    app = build_startup_planner()
    initial_state = {
        "messages": [{"role": "user", "content": startup_idea}],
        "startup_idea": startup_idea,
        "industry": industry,
        "competitors": competitors,
        "market_research_output": "",
        "competitor_analysis_output": "",
        "financial_projection_output": "",
        "funding_landscape_output": "",
        "final_report": "",
        "chart_paths": {},
    }
    return app.invoke(initial_state)


def stream_startup_planner(startup_idea: str, industry: str = "Technology",
                           competitors: str = ""):
    """Stream the pipeline, yielding (node_name, output) per step."""
    app = build_startup_planner()
    initial_state = {
        "messages": [{"role": "user", "content": startup_idea}],
        "startup_idea": startup_idea,
        "industry": industry,
        "competitors": competitors,
        "market_research_output": "",
        "competitor_analysis_output": "",
        "financial_projection_output": "",
        "funding_landscape_output": "",
        "final_report": "",
        "chart_paths": {},
    }
    for event in app.stream(initial_state):
        for node_name, node_output in event.items():
            yield node_name, node_output
