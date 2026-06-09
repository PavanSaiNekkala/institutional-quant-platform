import numpy as np
import pandas as pd

# =========================================================
# REALIZED VOLATILITY
# =========================================================


def realized_volatility(returns, window=20):

    rv = returns.rolling(window).std() * np.sqrt(252)

    return rv


# =========================================================
# VOL TARGET SCALER
# =========================================================


def volatility_target_scaler(returns, target_volatility=0.15, window=20, max_leverage=2.0):

    realized_vol = realized_volatility(returns, window)

    scaling_factor = target_volatility / (realized_vol + 1e-9)

    scaling_factor = scaling_factor.clip(upper=max_leverage)

    scaled_returns = returns * scaling_factor.shift(1)

    return (scaled_returns, scaling_factor)


# =========================================================
# DYNAMIC EXPOSURE
# =========================================================


def dynamic_exposure(realized_vol, low_vol=0.10, high_vol=0.30):

    exposure = []

    for vol in realized_vol:
        if np.isnan(vol):
            exposure.append(np.nan)

        elif vol < low_vol:
            exposure.append(1.5)

        elif vol > high_vol:
            exposure.append(0.5)

        else:
            exposure.append(1.0)

    return pd.Series(exposure, index=realized_vol.index)
