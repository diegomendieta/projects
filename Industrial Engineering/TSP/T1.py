from gurobipy import *
import numpy as np

np.random.seed(1)

'''
T1 - Programación Entera
TSP
'''

'''
Función que retorna el conjunto potencia de una lista.
'''
def subconjuntos(l):
    if not l:
        return [[]]
    return subconjuntos(l[1:]) + [[l[0]] + x for x in subconjuntos(l[1:])]


'''
Función que, dado un conjunto, retorna una lista con todos los pares posibles de
elementos del conjunto.
'''
def pares(l):
    return [(u, v) for u in l for v in l if v > u]


'''
Función que, tomando una lista V de todos los vértices, retorna todas las
aristas que tienen sólo un vertice en U.
'''
def E(U, V):
    lista = [(u, v) for u in U for v in V if v not in U]
    ordered = []
    for u, v in lista:
        if u > v:
            ordered.append((v, u))
        else:
            ordered.append((u, v))
    return ordered


'''
Se definen los parámetros
'''
N = 10
K = 100

'''
Se crea una lista con todos los vértices.
'''
V = [c for c in range(N)]
#print(V)

'''
Se crea una lista con todos los subconjuntos posibles que cumplan condición de
no ser iguales al original y tener 2 o más elementos.
'''
S = subconjuntos([c for c in range(N)])
S = [c for c in S if len(c) >= 2 and len(c) != N]
#print(S)

'''
Se crean los modelos.
'''
m1, m2, m3, m4 = Model(), Model(), Model(), Model()

'''
Se definen las variables. Notar que las variables representan flujo en una
arista (u, v). Se cumple siempre, para efectos de modelación, u < v.
'''
x1, x2, x3, x4 = {}, {}, {}, {}
for u in range(N):
    for v in range(N):
        #if u != v and (v, u) not in x1:
        if u < v:
            x1[u, v] = m1.addVar(lb=0, ub=1)
            x2[u, v] = m2.addVar(lb=0, ub=1)
            x3[u, v] = m3.addVar(lb=0, ub=1)
            x4[u, v] = m4.addVar(lb=0, ub=1)
            #x[u, v] = (u, v)

'''
R1: Suma de todas las aristas incidentes en cada vertice debe ser igual a 2.
'''
for u in range(N):
    m1.addConstr(
        quicksum(x1[u, v] for v in range(N) if (u, v) in x1) + quicksum(
            x1[v, u] for v in range(N) if (v, u) in x1) == 2)
    m2.addConstr(
        quicksum(x2[u, v] for v in range(N) if (u, v) in x2) + quicksum(
            x2[v, u] for v in range(N) if (v, u) in x2) == 2)


'''
R2: Eliminación de ciclos.
'''
for U in S:
    m1.addConstr(quicksum(x1[u, v] for u in U for v in U if v > u) <= len(U) - 1)
    m3.addConstr(quicksum(x3[u, v] for u in U for v in U if v > u) <= len(U) - 1)


'''
R3: Restricciones de conectividad.
'''
for U in S:
    P, H = pares(U), E(U, V)
    if not len(H):
        continue
    m2.addConstr(quicksum(x2[u, v] for u, v in H) >= 2)
    m4.addConstr(quicksum(x4[u, v] for u, v in H) >= 2)


'''
R4: Suma de todos los flujos debe ser igual a N.
'''
#m3.addConstr(quicksum(x3[u, v] for u in range(N) for v in range(N) if v > u))
#m4.addConstr(quicksum(x4[u, v] for u in range(N) for v in range(N) if v > u))

m3.addConstr(quicksum(x3[u, v] for (u, v) in x3) == N)
m4.addConstr(quicksum(x4[u, v] for (u, v) in x4) == N)


'''
Hasta acá tenemos las restricciones respectivas.
'''

m1.update()
m2.update()
m3.update()
m4.update()

m1.Params.OutputFlag = 0
m2.Params.OutputFlag = 0
m3.Params.OutputFlag = 0
m4.Params.OutputFlag = 0

'''
Iteramos para K funciones objetivo distintas.
'''
z1, z2, z3, z4 = [], [], [], []
for iter in range(K):
    costs = {(u, v): np.random.randint(5, 11) for u in range(N) for v in
             range(N) if u < v}
    obj1 = quicksum(
        x1[u, v] * costs[u, v] for u in range(N) for v in range(N) if u < v)
    obj2 = quicksum(
        x2[u, v] * costs[u, v] for u in range(N) for v in range(N) if u < v)
    obj3 = quicksum(
        x3[u, v] * costs[u, v] for u in range(N) for v in range(N) if u < v)
    obj4 = quicksum(
        x4[u, v] * costs[u, v] for u in range(N) for v in range(N) if u < v)

    m1.setObjective(obj1, sense=GRB.MINIMIZE)
    m2.setObjective(obj2, sense=GRB.MINIMIZE)
    m3.setObjective(obj3, sense=GRB.MINIMIZE)
    m4.setObjective(obj4, sense=GRB.MINIMIZE)

    m1.update()
    m2.update()
    m3.update()
    m4.update()

    m1.optimize()
    m2.optimize()
    m3.optimize()
    m4.optimize()

    z1.append(m1.objVal)
    z2.append(m2.objVal)
    z3.append(m3.objVal)
    z4.append(m4.objVal)

    if iter == 0:
        m1.printAttr('X')
        m2.printAttr('X')
        m3.printAttr('X')
        m4.printAttr('X')

'''
Printeamos las listas con los resultados obtenidos para cada modelo.
'''
print(z1)
print(z2)
print(z3)
print(z4)
