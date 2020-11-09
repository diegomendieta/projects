from functions import average


class Policy:
    def __init__(self, depot):
        self.depot = depot
        self.policy = self.create_policy()

    def decision(self, t, s):
        return self.policy[t, s]

    def create_policy(self):
        raise NotImplementedError


class ConservativePolicy(Policy):
    def __init__(self, depot):
        super().__init__(depot)

    def create_policy(self):
        policy = {}
        for t in range(1, self.depot.T + 1):
            for s in range(self.depot.Q + 1):
                policy[t, s] = self.depot.Q - s
        return policy


class NewsvendorPolicy(Policy):
    def __init__(self, depot):
        super().__init__(depot)

    def create_policy(self):
        policy = {}
        for t in range(1, self.depot.T + 1):
            for s in range(self.depot.Q + 1):

                min_ = float('inf')
                decision_ = None
                for x in range(self.depot.Q - s + 1):
                    cost = 0
                    for d, prob in self.depot.demands[t]:
                        c = self.depot.inmediate_cost(s, x, d)
                        cost += c

                    if cost < min_:
                        decision_ = x
                        min_ = cost

                policy[t, s] = decision_
        return policy


class AvgFuturePolicy(Policy):
    def __init__(self, depot):
        super().__init__(depot)

    def create_policy(self):
        costs_to_go = {}
        for s in range(self.depot.Q + 1):
            costs_to_go[self.depot.T + 1, s] = 0

        policy = {}
        for t in range(self.depot.T, 0, -1):

            demand = int(average(self.depot.demands[t]))
            for s in range(self.depot.Q + 1):

                min_ = float('inf')
                decision = None
                new_state = None
                for x in range(self.depot.Q - s + 1):
                    s_next = self.depot.transition(s + x, demand)
                    cost = self.depot.inmediate_cost(s, x, demand)
                    cost += costs_to_go[t + 1, s_next]

                    if cost < min_:
                        decision = x
                        min_ = cost

                policy[t, s] = decision
                costs_to_go[t, s] = min_
        return policy


class SSPolicy(Policy):
    def __init__(self, depot, sS):
        self.sS = sS
        super().__init__(depot)

    def create_policy(self):
        policy = {}
        for t in range(1, self.depot.T + 1):
            small, big = self.sS[t]
            for s in range(self.depot.Q + 1):
                if s < small:
                    policy[t, s] = big - s
                else:
                    policy[t, s] = 0
        return policy
