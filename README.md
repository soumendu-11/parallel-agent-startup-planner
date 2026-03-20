# LangGraph Startup Planner — Parallel Agent Pipeline with MCP Tools

A LangGraph pipeline that runs **4 specialized AI research agents in parallel** using FMP (Financial Modeling Prep) and Tavily Search as MCP tool providers, then synthesizes findings into a comprehensive startup plan with charts.

**Default use case:** Satellite imagery analytics startup.

## Architecture

```
                    ┌──────────────┐
                    │    START     │
                    └──────┬───────┘
       ┌──────────┬────────┼────────┬──────────┐   ← PARALLEL (fan-out)
       ▼          ▼        ▼        ▼          │
   Market    Competitor  Financial  Funding     │
   Research  Analysis    Projection Landscape   │
       │          │        │        │          │
       └──────────┴────────┼────────┘──────────┘   ← FAN-IN
                           ▼
                  Report Synthesis
                    (with charts)
                           │
                          END
```

All 4 research agents execute **concurrently** via LangGraph's fan-out, reducing total latency by ~2.5x compared to sequential execution.

## Hierarchical Skills

| Level | Role | MCP Tools |
|-------|------|-----------|
| **L0** (Synthesis) | Chief Strategy Officer | None — synthesizes all L1 outputs |
| **L1** (Research) | Market Research Analyst | Tavily Web Search, Tavily News Search |
| **L1** (Research) | Competitor Intelligence Analyst | FMP Profile, FMP Income, FMP Ratios, FMP Screener, Tavily Search |
| **L1** (Research) | Financial Projection Analyst | FMP Profile, FMP Income, FMP Ratios, FMP Market Index, Tavily Search |
| **L1** (Research) | Funding Landscape Analyst | Tavily Web Search, Tavily News Search |

## Project Structure

```
├── main.py                  # CLI entry point
├── mcp_servers.py           # MCP tool definitions (5 FMP + 2 Tavily Search)
├── requirements.txt         # Python dependencies
├── .env                     # API keys (git-ignored)
├── .env.example             # Template for .env
├── .gitignore
├── README.md
├── skills/                  # Hierarchical agent skill definitions
│   ├── __init__.py
│   ├── market_research.py       # L1 — Market Research Analyst
│   ├── competitor_analysis.py   # L1 — Competitor Intelligence Analyst
│   ├── financial_projection.py  # L1 — Financial Projection Analyst
│   ├── funding_landscape.py     # L1 — Funding Landscape Analyst
│   └── report_synthesizer.py    # L0 — Chief Strategy Officer
├── workflow/                # LangGraph parallel pipeline
│   ├── __init__.py
│   ├── state.py             # StartupPlannerState TypedDict
│   └── graph.py             # Fan-out/fan-in graph + node functions
├── utils/                   # Shared utilities
│   ├── __init__.py
│   ├── llm.py               # Azure OpenAI LLM config (from .env)
│   └── plotting.py          # matplotlib chart generators (4 chart types)
├── notebook/
│   └── startup_planner.ipynb  # Interactive notebook with visualizations
└── outputs/                 # Generated reports + PNG charts (git-ignored)
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API keys** — copy `.env.example` to `.env` and fill in:
   ```
   # Azure OpenAI
   AZURE_API_KEY=your_key
   AZURE_ENDPOINT=https://your-resource.openai.azure.com/
   DEPLOYMENT_NAME=gpt-4o
   API_VERSION=2025-01-01-preview

   # FMP (Free: 250 calls/day) — https://site.financialmodelingprep.com/register
   FMP_API_KEY=your_fmp_key

   # Tavily Search (Free: 1,000 searches/month) — https://app.tavily.com/sign-in
   TAVILY_API_KEY=your_tavily_key
   ```

3. **Run the pipeline:**
   ```bash
   python main.py
   python main.py --idea "Your startup idea" --industry "Healthcare" --competitors "TDOC,AMWL"
   ```

4. **Or use the notebook:**
   ```bash
   jupyter notebook notebook/startup_planner.ipynb
   ```

## How It Works

1. **Fan-out**: LangGraph launches all 4 research nodes simultaneously
2. **Parallel research**: Each agent uses its assigned MCP tools (FMP for financials, Tavily for web/news) to gather real data
3. **Fan-in**: Once all 4 complete, the L0 synthesis node receives all outputs
4. **Synthesis**: The Chief Strategy Officer combines findings into a cohesive startup plan
5. **Charts**: Structured `CHART_DATA` JSON from each agent is extracted and rendered as matplotlib PNGs

## Output

The pipeline produces:
- A comprehensive Markdown startup plan (8 sections)
- 4 PNG charts: Market Size, Financial Projections, Competitive Landscape, Funding Roadmap
- All saved to `outputs/`
