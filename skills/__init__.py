"""
Skills module — hierarchical startup planning analyst personas.

Hierarchy:
  L0 (Synthesis): Report Synthesizer (CSO)
  L1 (Research):  Market Research | Competitor Analysis | Financial Projection | Funding Landscape
"""

from skills.market_research import MARKET_RESEARCH_SKILL
from skills.competitor_analysis import COMPETITOR_ANALYSIS_SKILL
from skills.financial_projection import FINANCIAL_PROJECTION_SKILL
from skills.funding_landscape import FUNDING_LANDSCAPE_SKILL
from skills.report_synthesizer import REPORT_SYNTHESIZER_SKILL

# All skills indexed by name for lookup
SKILLS_REGISTRY = {
    s["name"]: s
    for s in [
        MARKET_RESEARCH_SKILL,
        COMPETITOR_ANALYSIS_SKILL,
        FINANCIAL_PROJECTION_SKILL,
        FUNDING_LANDSCAPE_SKILL,
        REPORT_SYNTHESIZER_SKILL,
    ]
}

__all__ = [
    "MARKET_RESEARCH_SKILL",
    "COMPETITOR_ANALYSIS_SKILL",
    "FINANCIAL_PROJECTION_SKILL",
    "FUNDING_LANDSCAPE_SKILL",
    "REPORT_SYNTHESIZER_SKILL",
    "SKILLS_REGISTRY",
]
