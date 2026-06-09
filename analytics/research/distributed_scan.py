import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

from core.orchestrator import orchestrate_portfolio

ROOT_DIR = Path(__file__).resolve().parents[2]

sys.path.append(str(ROOT_DIR))

# =========================================================
# SINGLE STOCK ANALYSIS
# =========================================================

def analyze_stock(symbol):

    np.random.seed(abs(hash(symbol)) % 100000)

    score = np.random.normal(0.75, 0.20)

    return {"Symbol": symbol, "Score": score}


# =========================================================
# DISTRIBUTED SCAN
# =========================================================


def distributed_scan(symbols, workers=8):

    results = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(analyze_stock, symbol): symbol for symbol in symbols}

        for future in as_completed(futures):
            try:
                result = future.result()

                results.append(result)

            except Exception as e:
                print("SCAN ERROR:", e)

    results_df = pd.DataFrame(results)

    results_df = results_df.sort_values("Score", ascending=False)

    return results_df


# =========================================================
# INSTITUTIONAL PIPELINE
# =========================================================


def institutional_distributed_pipeline(symbols, regime="BULL_NORMAL_VOL"):

    scan_results = distributed_scan(symbols)

    ranked_symbols = scan_results["Symbol"].tolist()

    orchestration = orchestrate_portfolio(ranked_symbols, regime=regime)

    return orchestration
