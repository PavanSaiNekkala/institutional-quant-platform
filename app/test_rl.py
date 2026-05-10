import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

import numpy as np

from ai.reinforcement_agent import (
    QLearningAgent,
    market_environment
)

# =====================================================
# RETURNS
# =====================================================

np.random.seed(42)

returns = np.random.normal(

    0,

    0.02,

    100
)

states = market_environment(

    returns
)

# =====================================================
# RL AGENT
# =====================================================

actions = [

    "BUY",
    "SELL",
    "HOLD"
]

agent = QLearningAgent(

    actions
)

# =====================================================
# TRAIN LOOP
# =====================================================

for i in range(len(states) - 1):

    state = states[i]

    next_state = states[i + 1]

    action = agent.choose_action(

        state
    )

    reward = returns[i]

    agent.update_q(

        state,

        action,

        reward,

        next_state
    )

# =====================================================
# OUTPUT
# =====================================================

print("\nREINFORCEMENT LEARNING Q-TABLE\n")

for state, values in agent.q_table.items():

    print(

        f"\nSTATE: {state}"
    )

    print(values)