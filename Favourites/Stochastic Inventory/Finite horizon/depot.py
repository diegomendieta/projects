from collections import defaultdict

class Depot:
    def __init__(self, Q, T, K, c, h, q, demands, lead_time=0):
        self.Q = Q
        self.T = T
        self.K = K
        self.c = c
        self.h = h
        self.q = q

        self.demands = demands
        self.lead_time = lead_time

        self.costs_to_go = {}
        self.policy = {}
        self.sS_policy = {}

        self.policy_class = None

    def inmediate_cost(self, s, x, d):
        '''
        Retorna el costo inmediato de una decisión x, dado un estado s y una
        realización d de la demanda.
        '''
        order = 0
        if x > 0:
            order = 1

        inventory = max(0, s + x - d)
        broken = max(0, d - s - x)

        c = self.K * order + self.c * x + self.q * broken + self.h * inventory
        return c

    def transition(self, post_s, d):
        '''
        Retorna un estado s' a partir del estado de post-decisión y la
        realización d de la demanda.
        '''
        return max(0, post_s - d)

    def naively_optimize(self, initial_inventory):
        '''
        Optimiza el problema de inventario estocástico de manera naive.
        '''
        self.costs_to_go = {}
        for s in range(self.Q + 1):
            self.costs_to_go[self.T + 1, s] = 0

        self.policy = {}
        for t in range(self.T, 0, -1):
            for s in range(self.Q+1):

                min_ = float('inf')
                decision = None
                for x in range(self.Q - s + 1):

                    cost = 0
                    for d, prob in self.demands[t]:
                        now = self.inmediate_cost(s, x, d)

                        s_next = self.transition(s + x, d)
                        future = self.costs_to_go[t+1, s_next]

                        cost += prob * (now + future)

                    if cost < min_:
                        min_ = cost
                        decision = x

                self.costs_to_go[t, s] = min_
                self.policy[t, s] = decision
        
        return self.costs_to_go[1, initial_inventory]

    def get_sS_policy(self):
        '''
        Retorna una política óptima, dada una solución al problema. Por tratarse
        de un problema de inventario estocástico, será del tipo (s, S).
        '''
        self.sS_policy, optimal_policy_s, optimal_policy_S = {}, {}, {}
        for (t, inventory), x in self.policy.items():
            if x:
                S = inventory + x
                if t in optimal_policy_S:
                    if S != optimal_policy_S[t]:
                        raise ValueError(f'Policy is not (s, S).')
                else:
                    optimal_policy_S[t] = S

            else:
                if t not in optimal_policy_s:
                    optimal_policy_s[t] = inventory

        for t in range(1, self.T+1):
            self.sS_policy[t] = (optimal_policy_s[t], optimal_policy_S[t])

        return self.sS_policy

    def reduced_space_optimize(self, initial_iventory):
        '''
        Optimiza el problema de inventario estocástico buscando dentro de el
        espacio de políticas (s, S).
        '''
        self.costs_to_go = {}
        for y in range(self.Q + 1):
            self.costs_to_go[self.T + 1, y] = 0

        loss_dict = {}
        self.sS_policy = {}
        for t in range(self.T, 0, -1):
            S = self.Q
            min_ = float('inf')

            for y in range(self.Q + 1):

                future = 0
                inmediate = self.c * y
                for d, prob in self.demands[t]:
                    inventory = max(0, y - d)
                    broken = max(0, d - y)

                    inmediate += prob * (self.h * inventory + self.q * broken)
                    future += prob * self.costs_to_go[t + 1, inventory]

                loss = inmediate + future
                loss_dict[y] = loss
                if loss < min_:
                    S = y
                    min_ = loss

            s = 0
            loss_S = loss_dict[S]
            for y in range(self.Q + 1):
                loss_y = loss_dict[y]
                if loss_y < loss_S + self.K:
                    break
                s += 1

            self.sS_policy[t] = (s, S)

            for y in range(self.Q + 1):
                if y <= s:
                    self.costs_to_go[t, y] = min_ + self.K - self.c * y
                else:
                    self.costs_to_go[t, y] = loss_dict[y] - self.c * y

        return self.costs_to_go[1, initial_iventory]

    def evaluate_policy(self, initial_inventory):
        '''
        Evalúa una política dada.
        '''
        costs_to_go = {}
        for s in range(self.Q + 1):
            costs_to_go[self.T + 1, s] = 0

        for t in range(self.T, 0, -1):
            for s in range(self.Q + 1):
                x = self.policy_class.decision(t, s)

                cost = 0
                for d, prob in self.demands[t]:
                    s_next = self.transition(s + x, d)

                    now = self.inmediate_cost(s, x, d)
                    future = costs_to_go[t + 1, s_next]

                    cost += prob * (now + future)

                costs_to_go[t, s] = cost
        return costs_to_go[1, initial_inventory]

    def simulate(self, initial_inventory, demands):
        total_cost = 0
        s = initial_inventory
        for t in range(1, self.T + 1):
            x = self.policy_class.decision(t, s)

            dem = demands[t]
            cost = self.inmediate_cost(s, x, dem)
            s = self.transition(s + x, dem)
            total_cost += cost

        return total_cost

    def perfect_information(self, initial_inventory, demands):
        costs_to_go = {(self.T+1, s): 0 for s in range(self.Q + 1)}
        for t in range(self.T, 0, -1):

            d = demands[t]
            for s in range(self.Q + 1):

                min_ = float('inf')
                for x in range(self.Q - s + 1):
                    now = self.inmediate_cost(s, x, d)
                    next_s = self.transition(s + x, d)

                    cost = now + costs_to_go[t + 1, next_s]
                    if cost < min_:
                        min_ = cost

                costs_to_go[t, s] = min_

        return costs_to_go[1, initial_inventory]

    def generate_feasible_states(self):
        feasible_states = {}
        for t in range(self.T, 0, -1):
            states_on_t = []
            for y in range(self.Q + 1):
                tup = (y, 0, 0)
                states_on_t.append(tup)

                for w in [1, 2]:
                    for p in range(self.Q + 1 - y):
                        tup = (y, w, p)
                        states_on_t.append(tup)

            feasible_states[t] = states_on_t

        return feasible_states

    def lead_time_optimize(self, initial_inventory):
        self.costs_to_go = {}
        for y in range(self.Q + 1):
            self.costs_to_go[self.T + 1, y, 0, 0] = 0
            for p in range(self.Q + 1 - y):
                for w in [1, 2]:
                    self.costs_to_go[self.T + 1, y, w, p] = 0

        feasible_states = self.generate_feasible_states()
        for t in range(self.T, 0, -1):
            states = feasible_states[t]
            for y, w, p in states:

                min_ = float('inf')
                decision = None

                if p == 0:
                    for x in range(self.Q + 1 - y):

                        # Agregar costo de hoy (fijo + quiebre + inventario)
                        fixed = self.K if x > 0 else 0
                        variable = self.c * x
                        cost = fixed + variable

                        for d, prob in self.demands[t]:
                            broken = self.q * max(0, d - y)
                            stored = self.h * max(0, y - d)
                            cost += prob * (broken + stored)

                        for (y_, w_, p_), prob in \
                                self.transitions_with_lt(t, y, w, p, x).items():

                            cost += prob * self.costs_to_go[t + 1, y_, w_, p_]

                        if cost < min_:
                            min_ = cost
                            decision = x

                # Considerando que no se puede pedir si ya hay pedido en camino
                else:

                    # Agregar costo de hoy (considerando que se pide 0)
                    cost = 0
                    for d, prob in self.demands[t]:
                        broken = self.q * max(0, d - y)
                        stored = self.h * max(0, y - d)
                        cost += prob * (broken + stored)

                    for (y_, w_, p_), prob in \
                            self.transitions_with_lt(t, y, w, p, 0).items():

                        cost += prob * self.costs_to_go[t + 1, y_, w_, p_]

                    decision = 0
                    min_ = cost

                self.costs_to_go[t, y, w, p] = min_
                self.policy[t, y, w, p] = decision

        return self.costs_to_go[1, initial_inventory, 0, 0]

    def transitions_with_lt(self, t, y, w, p, x):
        nw_arrival_prob = {0: 0.5, 1: 0.7}
        transitions = defaultdict(float)

        for d, prob in self.demands[t]:
            if w == 0:
                if d >= y:
                    transitions[x, 0, 0] += nw_arrival_prob[0] * prob
                    transitions[0, 1, x] += (1 - nw_arrival_prob[0]) * prob
                else:
                    transitions[y - d + x, 0, 0] = nw_arrival_prob[0] * prob
                    transitions[y - d, 1, x] = (1 - nw_arrival_prob[0]) * prob

            if w == 1:
                if d >= y:
                    transitions[p, 0, 0] += nw_arrival_prob[1] * prob
                    transitions[0, 2, p] += (1 - nw_arrival_prob[1]) * prob
                else:
                    transitions[y + p - d, 0, 0] = nw_arrival_prob[1] * prob
                    transitions[y - d, 2, p] = (1 - nw_arrival_prob[1]) * prob

            if w == 2:
                if d >= y:
                    transitions[p, 0, 0] += prob
                else:
                    transitions[y + p - d, 0, 0] = prob

        return transitions




