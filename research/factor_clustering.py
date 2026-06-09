import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage

# =========================================================
# GENERATE FACTORS
# =========================================================


def generate_factors(prices):

    df = pd.DataFrame()

    returns = prices.pct_change()

    df["momentum_20"] = prices / prices.shift(20)

    df["momentum_50"] = prices / prices.shift(50)

    df["volatility_20"] = returns.rolling(20).std()

    df["volatility_50"] = returns.rolling(50).std()

    ma20 = prices.rolling(20).mean()

    ma50 = prices.rolling(50).mean()

    df["mean_reversion_20"] = (prices - ma20) / ma20

    df["mean_reversion_50"] = (prices - ma50) / ma50

    return df.dropna()


# =========================================================
# CLUSTER FACTORS
# =========================================================


def cluster_factors(factors, threshold=1.0):

    corr = factors.corr()

    distance = 1 - corr.abs()

    linkage_matrix = linkage(distance, method="ward")

    clusters = fcluster(linkage_matrix, threshold, criterion="distance")

    cluster_df = pd.DataFrame({"Factor": corr.columns, "Cluster": clusters})

    return cluster_df, corr


# =========================================================
# CLUSTER SUMMARY
# =========================================================


def cluster_summary(cluster_df):

    summary = cluster_df.groupby("Cluster")["Factor"].apply(list)

    return summary
