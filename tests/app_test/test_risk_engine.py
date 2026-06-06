import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import numpy as np
import pandas as pd

from risk.drawdown import (
    calculate_drawdown,
    maximum_drawdown,
    rolling_max_drawdown,
    underwater_curve,
    recovery_time
)

from risk.var import (
    historical_var,
    conditional_var
)

from risk.stress_test import (
    stress_test_portfolio
)

from risk.exposure import (
    calculate_exposure
)

from risk.performance import (
    rolling_volatility,
    rolling_sharpe,
    rolling_cagr,
    rolling_returns
)

from risk.vol_target import (
    realized_volatility,
    volatility_target_scaler,
    dynamic_exposure
)
# =====================================================
# SAMPLE RETURNS
# =====================================================

returns = pd.Series(

    np.random.normal(

        0.001,

        0.02,

        252
    )
)

equity_curve = (

    100000 *

    (1 + returns)

    .cumprod()
)

# =====================================================
# DRAWDOWN
# =====================================================

drawdown = calculate_drawdown(

    equity_curve
)

max_dd = maximum_drawdown(

    equity_curve
)

print("\nMAX DRAWDOWN")

print(max_dd)

# =====================================================
# VAR
# =====================================================

var95 = historical_var(

    returns
)

cvar95 = conditional_var(

    returns
)

print("\nVAR 95%")

print(var95)

print("\nCVAR 95%")

print(cvar95)

# =====================================================
# STRESS TEST
# =====================================================

stress = stress_test_portfolio(

    equity_curve.iloc[-1]
)

print("\nSTRESS TEST")

print(stress)

# =====================================================
# EXPOSURE
# =====================================================

weights = {

    "RELIANCE.NS": 0.25,

    "TCS.NS": 0.20,

    "INFY.NS": 0.15,

    "HDFCBANK.NS": 0.40
}

exposure = calculate_exposure(

    weights
)

print("\nEXPOSURE")

print(exposure)

# =====================================================
# ROLLING DRAWDOWN
# =====================================================

rolling_dd = rolling_max_drawdown(

    equity_curve,

    window=60
)

print("\nROLLING MAX DRAWDOWN")

print(rolling_dd.tail())

# =====================================================
# UNDERWATER CURVE
# =====================================================

underwater = underwater_curve(

    equity_curve
)

print("\nUNDERWATER CURVE")

print(underwater.tail())

# =====================================================
# RECOVERY TIME
# =====================================================

recovery = recovery_time(

    equity_curve
)

print("\nRECOVERY PERIODS")

print(recovery)

# =====================================================
# ROLLING VOLATILITY
# =====================================================

rv = rolling_volatility(

    returns,

    window=60
)

print("\nROLLING VOLATILITY")

print(rv.tail())

# =====================================================
# ROLLING SHARPE
# =====================================================

rs = rolling_sharpe(

    returns,

    window=60
)

print("\nROLLING SHARPE")

print(rs.tail())

# =====================================================
# ROLLING CAGR
# =====================================================

rc = rolling_cagr(

    equity_curve,

    window=120
)

print("\nROLLING CAGR")

print(rc.tail())

# =====================================================
# ROLLING RETURNS
# =====================================================

rr = rolling_returns(

    returns,

    window=21
)

print("\nROLLING RETURNS")

print(rr.tail())

# =====================================================
# REALIZED VOLATILITY
# =====================================================

realized_vol = realized_volatility(

    returns,

    window=20
)

print("\nREALIZED VOLATILITY")

print(realized_vol.tail())

# =====================================================
# VOL TARGETING
# =====================================================

scaled_returns, scaling_factor = (

    volatility_target_scaler(

        returns,

        target_volatility=0.15
    )
)

print("\nVOL TARGET SCALING")

print(scaling_factor.tail())

# =====================================================
# DYNAMIC EXPOSURE
# =====================================================

exposure = dynamic_exposure(

    realized_vol
)

print("\nDYNAMIC EXPOSURE")

print(exposure.tail())
