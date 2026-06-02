import pandas as pd
import feedparser
import numpy as np
from datetime import datetime

# =====================================================
# FILES
# =====================================================

VALID_STOCKS_FILE = "data/valid_stocks.xlsx"

OUTPUT_FILE = "data/news_rankings.csv"

# =====================================================
# LOAD STOCKS
# =====================================================

print("\nLoading Valid Stocks...")

valid_df = pd.read_excel(
    VALID_STOCKS_FILE
)

stocks = (
    valid_df["Stock"]
    .dropna()
    .astype(str)
    .unique()
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
    "strong outlook"
]

STRONG_NEGATIVE = [
    "fraud",
    "investigation",
    "sebi action",
    "ban",
    "default",
    "loss widened",
    "missed estimates",
    "guidance cut",
    "downgrade"
]

POSITIVE = [
    "growth",
    "profit",
    "order",
    "contract",
    "expansion",
    "upgrade",
    "bullish"
]

NEGATIVE = [
    "loss",
    "decline",
    "weak",
    "penalty",
    "bearish"
]

# =====================================================
# CATEGORY DETECTION
# =====================================================

def detect_category(text):

    text = text.lower()

    if any(
        x in text
        for x in [
            "earnings",
            "results",
            "revenue",
            "q1",
            "q2",
            "q3",
            "q4"
        ]
    ):
        return "EARNINGS"

    if any(
        x in text
        for x in [
            "order",
            "contract",
            "deal",
            "agreement"
        ]
    ):
        return "ORDERS"

    if any(
        x in text
        for x in [
            "investigation",
            "penalty",
            "fraud",
            "sebi"
        ]
    ):
        return "REGULATORY"

    if any(
        x in text
        for x in [
            "guidance",
            "outlook",
            "forecast"
        ]
    ):
        return "GUIDANCE"

    if any(
        x in text
        for x in [
            "acquisition",
            "merger",
            "stake",
            "buyout"
        ]
    ):
        return "M&A"

    return "GENERAL"

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

    if (
        "but" in h
        or
        "despite" in h
    ):
        score *= 0.5

    return score

# =====================================================
# FETCH NEWS
# =====================================================

def get_news_score(symbol):

    try:

        query = symbol.replace(
            ".NS",
            ""
        )

        rss = (
            f"https://news.google.com/rss/search?"
            f"q={query}+India+stock"
        )

        feed = feedparser.parse(rss)

        entries = feed.entries[:10]

        if len(entries) == 0:

            return (
                0,
                "NONE",
                "LOW",
                0
            )

        total_score = 0

        categories = []

        for i, item in enumerate(entries):

            headline = item.title

            score = score_headline(
                headline
            )

            if i < 3:
                weight = 1.5
            elif i < 6:
                weight = 1.2
            else:
                weight = 1.0

            total_score += (
                score * weight
            )

            categories.append(
                detect_category(
                    headline
                )
            )

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

        dominant_category = (
            pd.Series(categories)
            .value_counts()
            .idxmax()
        )

        return (
            round(total_score, 2),
            bias,
            impact,
            dominant_category
        )

    except:

        return (
            0,
            "NONE",
            "LOW",
            "GENERAL"
        )

# =====================================================
# PROCESS ALL STOCKS
# =====================================================

print("\nScanning News...")

rows = []

for stock in stocks:

    score, bias, impact, category = (
        get_news_score(
            stock
        )
    )

    rows.append({

        "Symbol":
            stock,

        "NEWS_SCORE":
            score,

        "NEWS_BIAS":
            bias,

        "NEWS_IMPACT":
            impact,

        "NEWS_CATEGORY":
            category

    })

# =====================================================
# FINAL DF
# =====================================================

df = pd.DataFrame(rows)

df["NEWS_ALPHA"] = (

    df["NEWS_SCORE"]

    .rank(
        pct=True
    )

    * 100

).round(2)

df = df.sort_values(

    "NEWS_ALPHA",

    ascending=False

)

# =====================================================
# SAVE
# =====================================================

df.to_csv(

    OUTPUT_FILE,

    index=False

)

# =====================================================
# REPORT
# =====================================================

print("\nNews Engine Complete")

print("\nSaved:")

print(OUTPUT_FILE)

print("\nTop News Opportunities:\n")

print(

    df[
        [
            "Symbol",
            "NEWS_SCORE",
            "NEWS_BIAS",
            "NEWS_IMPACT",
            "NEWS_CATEGORY",
            "NEWS_ALPHA"
        ]
    ]

    .head(25)

)
