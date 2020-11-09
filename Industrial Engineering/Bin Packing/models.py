from gurobipy import *
from knapsack import *
from functions import *


'''
Retorna un modelo de programación entera, junto con sus diccionarios de 
variables. Representa la solución naive.
'''
def ip(B, v):

    m = Model()
    n = len(v)

    x = m.addVars(n, n, vtype=GRB.BINARY)
    y = m.addVars(n, vtype=GRB.BINARY)

    for k in range(n):
        m.addConstr(quicksum(v[i] * x[i, k] for i in range(n)) <= B)

        for i in range(n):
            m.addConstr(x[i, k] <= y[k])

    for i in range(n):
        m.addConstr(quicksum(x[i, k] for k in range(n)) == 1)

    m.setObjective(quicksum(y[k] for k in range(n)), sense=GRB.MINIMIZE)

    m.Params.OutputFlag = 0
    m.update()

    return m, x, y


'''
Retorna una formulación lineal del problema de Bin Packing para un grupo de 
cajas dado.
'''
def lp(S, v):
    # print(f'LP with n = [{len(v)}] and len(S) = [{len(S)}].')

    m = Model()

    z = {}
    for key in S.keys():
        z[key] = m.addVar(lb=0, name=f'{key}')

    constr = {}
    for i in v.keys():
        constr[i] = m.addConstr(quicksum(z[s] for
                                         s, cjt in S.items() if i in cjt) == 1,
                                name=f'{i}')

    m.setObjective(quicksum(z[s] for s in S), sense=GRB.MINIMIZE)

    m.Params.OutputFlag = 0
    m.update()

    return m, z


'''
Retorna los parámetros para crear el árbol que será el hijo izquierdo.
'''
def divide_left(s, B, v, i, j):

    print(f'Merging {i} and {j}.')
    s0 = filter_left(s, i, j)
    ns, nv, x = merge_vars(s0, v, i, j)

    m, z = lp(ns, nv)
    m1, z1, s1 = rlp_left(m, z, ns, B, nv)

    return m1, z1, s1, nv, x


'''
Retorna los parámetros para crear el árbol que será el hijo derecho.
'''
def divide_right(s, B, v, i, j):

    print(f'Filtering {i} and {j}.')
    ns = filter_right(s, i, j)
    nv = copy.deepcopy(v)

    m, z = lp(ns, v)
    m2, z2, s2 = rlp_right(m, z, ns, B, v, i, j)

    return m2, z2, s2, nv


'''
Retorna la resolución de la Generación de Columnas del hijo izquierdo.
'''
def rlp_left(lpmodel, z, S, B, v):
    ns = copy.deepcopy(S)

    n = len(v)
    new_n = max(S.keys()) + 1

    '''
    print(f'RLP LEFT with n = [{n}] and len(S) = [{len(S)}].')
    print(f'S: {S}')
    print()
    '''

    mapping = {key: num for key, num in zip(range(len(v)), v.keys())}
    mapping[-1] = -1

    iteration = 0
    while True:

        lpmodel.optimize()
        lpmodel.update()

        if lpmodel.status == 3 or lpmodel.status == 4:
            return lpmodel, {}, ns

        pi = lpmodel.Pi

        val_dict = knapsack(B, v, pi, mapping)

        zk = val_dict[B, mapping[n - 1]][0]
        sol = retrieve_sol(val_dict, B, v, n - 1, mapping)

        r = round(1 - zk, 3)
        if r >= -0.0001:
            lpmodel.update()
            break

        col = Column()
        for i in range(len(sol)):
            col.addTerms(sol[i], lpmodel.getConstrByName(f'{mapping[i]}'))

        ns[new_n] = {mapping[c] for c in range(len(sol)) if sol[c] != 0}
        z[new_n] = lpmodel.addVar(obj=1, column=col, lb=0, name=f'{new_n}')

        '''
        if iteration == 0:
            print(f'Lens: sol[{len(sol)}], v[{len(v)}], mapping[{len(mapping)}]')
            print(f'v {v}')
            print(f'Pi:', {mapping[c]: pi[c] for c in range(n) if sol[c]})
            print(f'sol:', {mapping[c]: sol[c] for c in range(n) if sol[c]})
            print(f'v:', {mapping[c]: v[mapping[c]] for c in range(n) if sol[c]})
            print(f'ns: {ns[new_n]}')
        '''

        lpmodel.update()

        new_n += 1
        iteration += 1

    z = dictify_solution(lpmodel.getVars())

    return lpmodel, z, ns


'''
Retorna la resolución de la Generación de Columnas del hijo derecho.
'''
def rlp_right(lpmodel, z, S, B, v, i, j):
    ns = copy.deepcopy(S)

    n = len(v)
    new_n = max(S.keys()) + 1

    '''
    print(f'RLP RIGHT with n = [{n}] and len(S) = [{len(S)}].')
    print(f'S: {S}')
    print()
    '''

    mapping = {key: num for key, num in zip(range(len(v)), v.keys())}
    mapping[-1] = -1

    iteration = 0
    while True:

        lpmodel.optimize()
        lpmodel.update()

        if lpmodel.status == 3 or lpmodel.status == 4:
            return lpmodel, {}, ns

        pi = lpmodel.Pi

        val_dict_forbidding_i = knapsack(B, v, pi, mapping, i)
        zki = val_dict_forbidding_i[B, mapping[n - 1]][0]

        val_dict_forbidding_j = knapsack(B, v, pi, mapping, j)
        zkj = val_dict_forbidding_j[B, mapping[n - 1]][0]

        zk = zki if zki > zkj else zkj

        if zki > zkj:
            sol = retrieve_sol(val_dict_forbidding_i, B, v, n - 1, mapping)

        else:
            sol = retrieve_sol(val_dict_forbidding_j, B, v, n - 1, mapping)

        r = round(1 - zk, 3)
        if r >= -0.0001:
            lpmodel.update()
            break

        col = Column()
        for i in range(len(sol)):
            col.addTerms(sol[i], lpmodel.getConstrByName(f'{mapping[i]}'))

        ns[new_n] = {mapping[c] for c in range(len(sol)) if sol[c] != 0}
        z[new_n] = lpmodel.addVar(obj=1, column=col, lb=0, name=f'{new_n}')

        lpmodel.update()

        new_n += 1
        iteration += 1

    z = dictify_solution(lpmodel.getVars())

    return lpmodel, z, ns
