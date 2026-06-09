import hashlib
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import feedparser
import numpy as np
import pandas as pd

# =====================================================
# FILES
# =====================================================

ROOT = Path(__file__).resolve().parents[2]

updated_stocks_FILE = "data/processed/factor_model_rankings.csv"

OUTPUT_FILE = "data/processed/news_rankings.csv"

CACHE_FILE = ROOT / "data" / "cache" / "news_cache.parquet"

HISTORY_FILE = ROOT / "data" / "cache" / "news_history.parquet"

MAX_WORKERS = 20

# =====================================================
# LOAD STOCKS
# =====================================================

print("\nLoading Valid Stocks...")

valid_df = pd.read_csv(updated_stocks_FILE)

stocks = (
    valid_df["Symbol"]
    .astype(str)
    .str.replace(".NS", "", regex=False)
    .str.upper()
    .str.strip()
    .unique()
    .tolist()
)
PORTFOLIO_FILE = ROOT / "data" / "optimised_portfolio.csv"

portfolio_symbols = []

if PORTFOLIO_FILE.exists():
    portfolio_df = pd.read_csv(PORTFOLIO_FILE)

    portfolio_symbols = (
        portfolio_df["Symbol"].astype(str).str.replace(".NS", "", regex=False).str.upper().tolist()
    )

TOP_FACTOR_COUNT = 100

top_factor_symbols = (
    valid_df.head(TOP_FACTOR_COUNT)["Symbol"]
    .astype(str)
    .str.upper()
    .str.replace(".NS", "", regex=False)
    .tolist()
)

# =====================================================
# SENTIMENT DICTIONARIES
# =====================================================

STRONG_POSITIVE = [
    "record profit",
    "big order",
    "large deal",
    "multi year contract",
    "margin expansion",
    "guidance raised",
    "beat estimates",
    "strong outlook",
]

POSITIVE_EVENTS = {
    "big order": 5,
    "order win": 5,
    "contract": 4,
    "agreement": 4,
    "guidance raised": 5,
    "record profit": 5,
    "margin expansion": 4,
    "acquisition": 3,
    "stake purchase": 3,
    "capacity expansion": 4,
    "fii buying": 4,
    "promoter buying": 5,
}

STRONG_NEGATIVE = [
    "fraud",
    "investigation",
    "sebi action",
    "ban",
    "default",
    "loss widened",
    "missed estimates",
    "guidance cut",
    "downgrade",
]

NEGATIVE_EVENTS = {
    "fraud": -8,
    "investigation": -7,
    "sebi action": -7,
    "default": -8,
    "downgrade": -4,
    "guidance cut": -5,
    "loss widened": -5,
    "pledge": -4,
    "resignation": -3,
}

POSITIVE = ["growth", "profit", "order", "contract", "expansion", "upgrade", "bullish"]

NEGATIVE = ["loss", "decline", "weak", "penalty", "bearish"]

# =====================================================
# CATEGORY DETECTION
# =====================================================


def detect_event_score(text):

    text = text.lower()

    score = 0

    for k, v in POSITIVE_EVENTS.items():
        if k in text:
            score += v

    for k, v in NEGATIVE_EVENTS.items():
        if k in text:
            score += v

    return score


def detect_category(text):

    text = text.lower()

    if any(x in text for x in ["earnings", "results", "revenue", "q1", "q2", "q3", "q4"]):
        return "EARNINGS"

    if any(x in text for x in ["order", "contract", "deal", "agreement"]):
        return "ORDERS"

    if any(x in text for x in ["investigation", "penalty", "fraud", "sebi"]):
        return "REGULATORY"

    if any(x in text for x in ["guidance", "outlook", "forecast"]):
        return "GUIDANCE"

    if any(x in text for x in ["acquisition", "merger", "stake", "buyout"]):
        return "M&A"

    return "GENERAL"


def get_source_weight(link):

    source_map = {
        "reuters.com": 2.0,
        "bloomberg.com": 2.0,
        "economictimes.indiatimes.com": 1.5,
        "moneycontrol.com": 1.4,
        "business-standard.com": 1.4,
        "livemint.com": 1.4,
        "cnbctv18.com": 1.3,
        "ndtvprofit.com": 1.3,
    }

    link = str(link).lower()

    for domain, weight in source_map.items():
        if domain in link:
            return weight

    return 0.8


# =====================================================
# NEWS SCORE
# =====================================================


def score_headline(headline):

    h = headline.lower()

    score = 0

    for word in STRONG_POSITIVE:
        if word in h:
            score += 2

    for word in STRONG_NEGATIVE:
        if word in h:
            score -= 2

    for word in POSITIVE:
        if word in h:
            score += 1

    for word in NEGATIVE:
        if word in h:
            score -= 1

    if "but" in h or "despite" in h:
        score *= 0.5

    return score


# =====================================================
# FETCH NEWS
# =====================================================
def generate_hash(entries):

    text = "|".join([x.title for x in entries[:10]])

    return hashlib.md5(text.encode()).hexdigest()


def get_news_score(symbol):

    try:
        query = symbol.replace(".NS", "")

        rss = "https://news.google.com/rss/search?q=" + quote(f"{query} India stock")

        feed = feedparser.parse(rss)

        entries = feed.entries[:5]

        news_count = len(entries)

        headline_hash = generate_hash(entries)

        if len(entries) == 0:
            return (0, "NONE", "LOW", "GENERAL", "", 0)
        total_score = 0

        categories = []

        for i, item in enumerate(entries):
            headline = item.title

            summary = getattr(item, "summary", "")

            text = f"{headline} {summary}"

            sentiment_score = score_headline(text)

            event_score = detect_event_score(text)

            score = sentiment_score + event_score

            if i < 3:
                recency_weight = 1.5
            elif i < 6:
                recency_weight = 1.2
            else:
                recency_weight = 1.0

            source_name = getattr(item, "source", {})
            source_text = str(source_name)

            source_weight = get_source_weight(source_text)
            total_score += score * recency_weight * source_weight

            categories.append(detect_category(headline))

        if total_score >= 2:
            bias = "POSITIVE"
        elif total_score <= -2:
            bias = "NEGATIVE"
        else:
            bias = "NEUTRAL"

        impact = "LOW"

        if abs(total_score) >= 3:
            impact = "HIGH"
        elif abs(total_score) >= 2:
            impact = "MEDIUM"

        if categories:
            dominant_category = pd.Series(categories).value_counts().idxmax()
        else:
            dominant_category = "GENERAL"

        return (round(total_score, 2), bias, impact, dominant_category, headline_hash, news_count)

    except Exception as e:
        print(f"ERROR {symbol}: {e}")

        return (0, "NONE", "LOW", "GENERAL", "", 0)


if CACHE_FILE.exists():
    cache_df = pd.read_parquet(CACHE_FILE)

    cache_df["Symbol"] = (
        cache_df["Symbol"].astype(str).str.upper().str.replace(".NS", "", regex=False).str.strip()
    )

else:
    cache_df = pd.DataFrame(
        columns=[
            "Symbol",
            "HEADLINE_HASH",
            "FIRST_SEEN",
            "LAST_FETCH_TIME",
            "LAST_NEWS_CHANGE",
            "NEWS_SCORE",
            "NEWS_COUNT",
            "NEWS_BIAS",
            "NEWS_IMPACT",
            "NEWS_CATEGORY",
        ]
    )

cache_lookup = cache_df.set_index("Symbol").to_dict("index")

print("\nScanning News...")

rows = []
cache_rows = []
fresh_stocks = []

overall_start = time.time()

total_stocks = len(stocks)

# ==========================================
# CACHE CHECK
# ==========================================

for stock in stocks:
    cached = cache_lookup.get(stock)

    clean_stock = stock.replace(".NS", "").upper()

    if clean_stock in portfolio_symbols or clean_stock in top_factor_symbols:
        fresh_stocks.append(stock)

        continue

    if cached:
        age_hours = (
            datetime.now() - pd.to_datetime(cached["LAST_FETCH_TIME"])
        ).total_seconds() / 3600

        CACHE_HOURS = 1

        if age_hours < CACHE_HOURS:
            rows.append(
                {
                    "Symbol": stock,
                    "NEWS_SCORE": cached["NEWS_SCORE"],
                    "NEWS_COUNT": cached.get("NEWS_COUNT", 10),
                    "NEWS_BIAS": cached["NEWS_BIAS"],
                    "NEWS_IMPACT": cached["NEWS_IMPACT"],
                    "NEWS_CATEGORY": cached["NEWS_CATEGORY"],
                }
            )

            cache_rows.append(
                {
                    "Symbol": stock,
                    "HEADLINE_HASH": cached["HEADLINE_HASH"],
                    "FIRST_SEEN": cached.get("FIRST_SEEN"),
                    "LAST_FETCH_TIME": cached["LAST_FETCH_TIME"],
                    "LAST_NEWS_CHANGE": cached.get("LAST_NEWS_CHANGE"),
                    "NEWS_SCORE": cached["NEWS_SCORE"],
                    "NEWS_COUNT": cached["NEWS_COUNT"],
                    "NEWS_BIAS": cached["NEWS_BIAS"],
                    "NEWS_IMPACT": cached["NEWS_IMPACT"],
                    "NEWS_CATEGORY": cached["NEWS_CATEGORY"],
                }
            )

            continue

    fresh_stocks.append(stock)

print(f"\nUsing Cache : {len(stocks) - len(fresh_stocks)}")

print(f"\nFetching RSS : {len(fresh_stocks)}")

# ==========================================
# FETCH ONLY FRESH STOCKS
# ==========================================

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    futures = {executor.submit(get_news_score, stock): stock for stock in fresh_stocks}

    results = []

    completed = 0

    for future in as_completed(futures):
        stock = futures[future]

        try:
            result = future.result()

        except Exception as e:
            print(f"ERROR {stock}: {e}")

            result = (0, "NONE", "LOW", "GENERAL", "", 0)

        results.append((stock, result))

        completed += 1

        if completed % 100 == 0:
            print(f"Completed {completed}/{len(fresh_stocks)}")
for idx, (stock, result) in enumerate(results, start=1):
    score, bias, impact, category, headline_hash, news_count = result

    cached = cache_lookup.get(stock)

    news_changed = True

    if cached:
        if cached["HEADLINE_HASH"] == headline_hash:
            news_changed = False

            score = cached["NEWS_SCORE"]
            bias = cached["NEWS_BIAS"]
            impact = cached["NEWS_IMPACT"]
            category = cached["NEWS_CATEGORY"]

            first_seen = cached.get("FIRST_SEEN", datetime.now())

            last_news_change = cached.get("LAST_NEWS_CHANGE", datetime.now())

        else:
            first_seen = cached.get("FIRST_SEEN", datetime.now())

            last_news_change = datetime.now()

    else:
        first_seen = datetime.now()

        last_news_change = datetime.now()

    # --------------------------------
    # CACHE LOOKUP
    # --------------------------------

    status = "UPDATED" if news_changed else "SKIPPED"

    cache_rows.append(
        {
            "Symbol": stock,
            "HEADLINE_HASH": headline_hash,
            "FIRST_SEEN": first_seen,
            "LAST_FETCH_TIME": datetime.now(),
            "LAST_NEWS_CHANGE": last_news_change,
            "NEWS_SCORE": score,
            "NEWS_COUNT": news_count,
            "NEWS_BIAS": bias,
            "NEWS_IMPACT": impact,
            "NEWS_CATEGORY": category,
        }
    )

    if idx % 50 == 0:
        print(f"[{idx}/{len(fresh_stocks)}] {stock:<15} | {status:<8} | Score={score:<6}")

    rows.append(
        {
            "Symbol": stock,
            "NEWS_SCORE": score,
            "NEWS_COUNT": news_count,
            "NEWS_BIAS": bias,
            "NEWS_IMPACT": impact,
            "NEWS_CATEGORY": category,
        }
    )

total_runtime = round(time.time() - overall_start, 2)

print(f"\n✅ Processed {total_stocks} stocks in {total_runtime} seconds")


# =====================================================
# FINAL DF
# =====================================================

df = pd.DataFrame(rows)

cache_snapshot = pd.DataFrame(cache_rows)

df = df.merge(cache_snapshot[["Symbol", "FIRST_SEEN", "LAST_NEWS_CHANGE"]], on="Symbol", how="left")

df["Symbol"] = df["Symbol"].astype(str).str.upper().str.replace(".NS", "", regex=False).str.strip()

now = datetime.now()

# =====================================================
# NEWS DELTA
# =====================================================

delta_lookup = {}

if HISTORY_FILE.exists():
    hist = pd.read_parquet(HISTORY_FILE)

    hist = hist.sort_values(["Symbol", "TIMESTAMP"])

    hist["PREV_SCORE"] = hist.groupby("Symbol")["NEWS_SCORE"].shift(1)

    hist["PREV_DELTA"] = hist.groupby("Symbol")["NEWS_SCORE"].diff().shift(1)

    hist["NEWS_ACCELERATION"] = hist.groupby("Symbol")["NEWS_SCORE"].diff() - hist["PREV_DELTA"]

    latest = hist.groupby("Symbol").tail(1)

    delta_lookup = dict(
        zip(
            latest["Symbol"],
            (latest["NEWS_SCORE"] - latest["PREV_SCORE"]).fillna(0),
            strict=False,
        )
    )

df["NEWS_DELTA"] = df["Symbol"].map(delta_lookup).fillna(0).round(2)

acceleration_lookup = dict(
    zip(
        hist.groupby("Symbol").tail(1)["Symbol"],
        hist.groupby("Symbol").tail(1)["NEWS_ACCELERATION"].fillna(0),
        strict=False,
    )
)

df["NEWS_ACCELERATION"] = df["Symbol"].map(acceleration_lookup).fillna(0).round(2)

df["NEWS_AGE_HOURS"] = (now - pd.to_datetime(df["LAST_NEWS_CHANGE"])).dt.total_seconds() / 3600

df["NEWS_FRESHNESS"] = np.exp(-df["NEWS_AGE_HOURS"] / 48)

df["NEWS_ALPHA_RAW"] = (
    df["NEWS_SCORE"] * 0.45
    + np.log1p(df["NEWS_COUNT"]) * 0.10
    + abs(df["NEWS_DELTA"]) * 0.20
    + abs(df["NEWS_ACCELERATION"]) * 0.15
    + np.where(df["NEWS_IMPACT"] == "HIGH", 2, 0) * 0.10
)


df["PORTFOLIO_BOOST"] = np.where(
    df["Symbol"].isin(portfolio_symbols),
    5,
    0,
)

df["NEWS_ALPHA"] = df["NEWS_ALPHA_RAW"] * df["NEWS_FRESHNESS"] + df["PORTFOLIO_BOOST"]

df["NEWS_ALPHA"] = df["NEWS_ALPHA"].rank(pct=True) * 100

df = df.sort_values("NEWS_ALPHA", ascending=False)

df["PORTFOLIO_BOOST"] = np.where(
    df["Symbol"].isin(portfolio_symbols),
    5,
    0,
)

# =====================================================
# NEWS HISTORY
# =====================================================

history_snapshot = df[["Symbol", "NEWS_SCORE", "NEWS_ALPHA"]].copy()
history_snapshot = pd.merge(
    history_snapshot, cache_df[["Symbol", "HEADLINE_HASH"]], on="Symbol", how="left"
)
history_snapshot["TIMESTAMP"] = datetime.now()

if HISTORY_FILE.exists():
    old_history = pd.read_parquet(HISTORY_FILE)

    history_snapshot = pd.concat([old_history, history_snapshot], ignore_index=True)

    history_snapshot["TIMESTAMP"] = pd.to_datetime(history_snapshot["TIMESTAMP"])

    history_snapshot = history_snapshot[
        history_snapshot["TIMESTAMP"] >= pd.Timestamp.now() - pd.Timedelta(days=30)
    ]

history_snapshot.to_parquet(HISTORY_FILE, index=False)

print("\n📜 News History Updated")

# =====================================================
# SAVE
# =====================================================

cache_df = pd.DataFrame(cache_rows)

cache_df.to_parquet(CACHE_FILE, index=False)

print("\n💾 Cache Saved:")

print(CACHE_FILE)

# =====================================================
# EVENT SIGNAL
# =====================================================


def classify_event(delta):

    if delta >= 3:
        return "NEWS BREAKOUT"

    elif delta >= 1:
        return "POSITIVE CHANGE"

    elif delta <= -3:
        return "NEWS COLLAPSE"

    elif delta <= -1:
        return "NEGATIVE CHANGE"

    return "STABLE"


df["EVENT_SIGNAL"] = df["NEWS_DELTA"].apply(classify_event)

alert_df = df[df["EVENT_SIGNAL"] != "STABLE"]

df["NEWS_SHOCK"] = abs(df["NEWS_DELTA"]) > df["NEWS_DELTA"].std() * 2

df["NEWS_SHOCK"] = np.where(df["NEWS_SHOCK"], "YES", "NO")

output_cols = [
    "Symbol",
    "NEWS_SCORE",
    "NEWS_COUNT",
    "NEWS_BIAS",
    "NEWS_IMPACT",
    "NEWS_SHOCK",
    "NEWS_CATEGORY",
    "NEWS_ALPHA",
    "NEWS_DELTA",
    "NEWS_ACCELERATION",
    "EVENT_SIGNAL",
]

df = df[output_cols]

# =====================================================
# REPORT
# =====================================================

df.to_csv(OUTPUT_FILE, index=False)

print("\nNews Engine Complete")

print("\nSaved:")

print(OUTPUT_FILE)

print("\nTop News Opportunities:\n")

print(
    df[["Symbol", "NEWS_SCORE", "NEWS_BIAS", "NEWS_IMPACT", "NEWS_CATEGORY", "NEWS_ALPHA"]].head(25)
)
