from gurobipy import *
from functions import powerset


class TSP:
    def __init__(self):
        self.model = Model()

    def setVars(self, pending_nodes):
        self.x, self.nodes = {}, []

        for u in pending_nodes:
            self.nodes.append(u)

            for v in pending_nodes:
                if u < v:
                    self.x[u, v] = self.model.addVar(vtype=GRB.BINARY)

    def flowConstr(self):
        """
        Restricción que setea que la suma de las aristas incidentes en cada
        vértice es igual a 2.
        """
        for u in self.nodes:
            c1 = quicksum(self.x[u, v] for v in self.nodes if (u, v) in self.x)
            c2 = quicksum(self.x[v, u] for v in self.nodes if (v, u) in self.x)
            self.model.addConstr(c1 + c2 == 2)

    def subtourEliminationConstr(self):
        """
        Restricción que elimina los subtours.
        """
        S = [subset for subset in powerset(self.nodes)
             if 2 <= len(subset) < len(self.nodes)]
        for U in S:
            c = quicksum(self.x[u, v] for u in U for v in U if v > u)
            self.model.addConstr(c <= len(U) - 1)

    def setConstrs(self):
        """
        Setea las restricciones del problema.
        """
        self.flowConstr()
        self.subtourEliminationConstr()

    def setObjective(self, edges):
        obj = quicksum(edges[u, v] * self.x[u, v] for u, v in self.x.keys())
        self.model.setObjective(obj, sense=GRB.MINIMIZE)
        self.model.update()

    def solve(self, show=False):
        if not show:
            self.model.Params.OutputFlag = 0
        self.model.optimize()
        print(f'Status: {self.model.Status}')
        return self.model.objVal, self.x
