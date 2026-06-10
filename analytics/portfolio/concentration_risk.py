from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

PORTFOLIO_FILE = ROOT / "data" / "portfolio" / "optimised_portfolio.csv"

OUTPUT_FILE = ROOT / "data" / "portfolio" / "concentration_risk.csv"

portfolio = pd.read_csv(PORTFOLIO_FILE)

weights = portfolio["OPT_WEIGHT"]

top5 = weights.nlargest(5).sum()

top10 = weights.nlargest(10).sum()

hhi = (weights**2).sum()

effective_n = 1 / hhi

output = pd.DataFrame(
    {
        "Metric": [
            "Top5_Weight",
            "Top10_Weight",
            "HHI",
            "Effective_Positions",
        ],
        "Value": [
            top5,
            top10,
            hhi,
            effective_n,
        ],
    }
)

output.to_csv(OUTPUT_FILE, index=False)

print(output)
