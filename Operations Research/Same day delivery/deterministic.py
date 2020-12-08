from gurobipy import *
from functions import *
import json


class Deterministic:
    """
    Problema determinístico, usado como benchmark de información perfecta.
    """

    def __init__(self, prev_commitments, arrivals, penalties):
        self.prev_commitments = prev_commitments
        self.arrivals = arrivals
        self.penalties = penalties

        self.model = Model()

    def setVars(self, W):
        """
        Setea las variables del problema.
        """
        W_ = max(W)

        self.v, self.s, self.z, self.y, self.x = {}, {}, {}, {}, {}
        for w in W:
            if w < W_:
                # (2j)
                # Binaria que indica si el vehículo espera en el centro de
                # distribución hasta k.
                self.s[w] = self.model.addVar(vtype=GRB.BINARY,
                                              name=f's[{w}]')

            for k in W:
                if k < w:
                    # (2i)
                    # Binaria que indica si despacho saliente en w vuelve en k.
                    self.v[k, w] = self.model.addVar(vtype=GRB.BINARY,
                                                     name=f'v[{k},{w}]')

            if w != 0:
                # (2l)
                feasible_nodes = feasibleDispatchNodes(w)
                feasible_edges = feasibleDispatchEdges(w)

                for i in feasible_nodes:
                    # Binaria que indica si se visita i en despacho saliente en
                    # k.
                    self.y[i, w] = self.model.addVar(vtype=GRB.BINARY,
                                                     name=f'y[{i},{w}]')

                for i, j in feasible_edges:
                    # Variable entera que indica cuántas veces se cruza la
                    # arista (i, j) en el despacho saliente en w.
                    self.x[i, j, w] = self.model.addVar(vtype=GRB.INTEGER,
                                                        lb=0, ub=2,
                                                        name=f'x[{i},{j},{w}]')

        for i in I:
            # (2k)
            # Binaria que indica si i es visitado.
            self.z[i] = self.model.addVar(vtype=GRB.BINARY,
                                                     name=f'z[{i}]')

    def prevCommitmentsConstr(self):
        """
        Restricción que indica que se debe atender las solicitudes aceptadas
        anteriormente.
        """
        # (2b)
        for i in self.prev_commitments.keys():
            if self.prev_commitments[i] == float('inf'):
                continue
            h = latestPossibleDispatchWave(i, 0)
            c = quicksum(self.y[i, w] for w
                         in range(h, self.prev_commitments[i] + 1))
            self.model.addConstr(c == 1)

    def feasibleSpaceConstr(self, W):
        """
        Restricción que restringe el dominio del problema.
        """
        W_ = max(W)

        # (2c)
        for i in I:
            h = latestPossibleDispatchWave(i, 0)
            self.model.addConstr(
                self.z[i] + quicksum(self.y[i, w]
                                     for w in range(h, W_ + 1)) == 1)

        for w in W:
            if w == 0:
                continue
            # (2d)
            self.model.addConstr(
                quicksum(self.x[i, j, w] for i, j in cutSets(w, {0})) <= 2)

            # (2e)
            for S in powerset(feasibleDispatchNodes(w)):
                for i in set(S):
                    lhs = quicksum(self.x[i_, j_, w]
                                   for i_, j_ in cutSets(w, S))
                    rhs = 2 * self.y[i, w]
                    self.model.addConstr(lhs >= rhs)

            # (2f)
            lhs = quicksum(adjustedTimeSpent(i, j) * self.x[i, j, w]
                           for i, j in feasibleDispatchEdges(w))
            rhs = quicksum(
                (waveTimes[w] - waveTimes[k]) * self.v[k, w] for k in range(w))
            self.model.addConstr(lhs <= rhs)

            # (2h)
            if w != W_:
                lhs = quicksum(self.v[k, w] for k in range(w))
                rhs = quicksum(self.v[w, k]
                               for k in range(w + 1, W_ + 1)) + self.s[w]
                self.model.addConstr(lhs == rhs)

        # (2g)
        lhs = quicksum(self.s[k] for k in range(W_)) + \
              quicksum(self.v[k, W_] for k in range(W_))
        self.model.addConstr(lhs == 1)

    def setConstrs(self, W):
        self.prevCommitmentsConstr()
        self.feasibleSpaceConstr(W)

    def setObjective(self, W):
        obj = 0
        self.penalty_cost = 0
        for i in I:
            if i == 0:
                continue
            aux = maxRequests(self.arrivals, i, 0) * self.z[i]

            h = latestPossibleDispatchWave(0, i)
            for w in range(h, W_ + 1):
                aux += maxRequests(self.arrivals, i, 0) * self.y[i, w]
                aux -= maxRequests(self.arrivals, i, w) * self.y[i, w]

            obj += penalties[i] * aux
            self.penalty_cost += penalties[i] * aux

        self.routing_cost = 0
        for w in W:
            if w != 0:
                for i, j in feasibleDispatchEdges(w):
                    obj += gamma * edgeTime(i, j) * self.x[i, j, w]
                    self.routing_cost += \
                        gamma * edgeTime(i, j) * self.x[i, j, w]

        self.model.setObjective(obj, sense=GRB.MINIMIZE)
        self.model.update()

    def loadModel(self, file_name):
        self.model = read(f'{file_name}.lp')

    def saveModel(self, params_name, model_name):
        params = varDict()

        with open(f'{params_name}.json', 'w') as file:
            json.dump(params, file, indent=4)

        self.model.write(f'{model_name}.lp')

    def solve(self, show=False):
        # print('solving deterministic...')
        if show:
            self.model.Params.OutputFlag = 1
        else:
            self.model.Params.OutputFlag = 0
        self.model.optimize()
        # print(self.model.Status)
        return self.model.objVal

    def showStats(self):
        tot = len(self.arrivals)
        tot += sum([1 for c, wa in self.prev_commitments.items()
                    if wa != float('inf')])

        # print(f'Total requests: {tot}')

        print(f'Routing cost: {self.routing_cost.getValue()}')
        print(f'Penalty cost: {self.penalty_cost.getValue()}')

        rej = 0
        for i in I:
            for w in range(latestPossibleDispatchWave(0, i), W_ + 1):
                if self.y[i, w].X == 1:
                    rej += \
                        (maxRequests(self.arrivals, i, 0) -
                         maxRequests(self.arrivals, i, w))

            if self.z[i].X == 1:
                rej += maxRequests(self.arrivals, i, 0)

        print(f'Requests accepted: {tot - rej}')
        print(f'Requests rejected: {rej}')
        print(f'Fill rate: {(tot - rej)/tot:.2f}')

        travel_time = 0
        for (i, j, w), x in self.x.items():
            travel_time += x.X * adjustedTimeSpent(i, j)
        print(f'Total travel time: {travel_time}')

        print(f'Travel time / accepted requests: '
              f'{travel_time / (tot - rej):.2f}')

        avg_nodes = defaultdict(set)
        for (i, w), y in self.y.items():
            if y.X == 1:
                avg_nodes[w].add(i)

        sum_, count_ = 0, 0
        for w, nodes in avg_nodes.items():
            if nodes:
                count_ += 1
                sum_ += len(nodes)
        print(f'Average quantity of nodes on route: {sum_ / count_}')
