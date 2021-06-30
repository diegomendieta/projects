from tsp import *
import numpy as np

np.random.seed(0)
N = range(11)

nodes = set()
for c in N:
    nodes.add(c)

edges = {}
for u in nodes:
    for v in nodes:
        if u != v:
            edges[u, v] = np.random.randint(1, 11)

t = TSP()
t.setVars(nodes)
t.setConstrs()
t.setObjective(edges)

objVal, x = t.solve()
print(objVal)
print([(u, v) for (u, v), val in x.items() if val.X])
