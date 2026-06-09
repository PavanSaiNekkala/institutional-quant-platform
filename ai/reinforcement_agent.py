import random

# =========================================================
# Q-LEARNING AGENT
# =========================================================


class QLearningAgent:
    def __init__(self, actions, alpha=0.1, gamma=0.95, epsilon=0.10):

        self.actions = actions

        self.alpha = alpha

        self.gamma = gamma

        self.epsilon = epsilon

        self.q_table = {}

    # =====================================================
    # STATE INITIALIZATION
    # =====================================================

    def initialize_state(self, state):

        if state not in self.q_table:
            self.q_table[state] = {action: 0 for action in self.actions}

    # =====================================================
    # ACTION SELECTION
    # =====================================================

    def choose_action(self, state):

        self.initialize_state(state)

        if random.uniform(0, 1) < self.epsilon:
            return random.choice(self.actions)

        return max(self.q_table[state], key=self.q_table[state].get)

    # =====================================================
    # Q UPDATE
    # =====================================================

    def update_q(self, state, action, reward, next_state):

        self.initialize_state(next_state)

        old_q = self.q_table[state][action]

        next_max = max(self.q_table[next_state].values())

        new_q = old_q + self.alpha * (reward + self.gamma * next_max - old_q)

        self.q_table[state][action] = new_q


# =========================================================
# MARKET ENVIRONMENT
# =========================================================


def market_environment(returns):

    env = []

    for r in returns:
        if r > 0.01:
            env.append("BULL")

        elif r < -0.01:
            env.append("BEAR")

        else:
            env.append("SIDEWAYS")

    return env
