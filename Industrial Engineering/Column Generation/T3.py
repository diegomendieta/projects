from gurobipy import *
import numpy as np
import time

np.random.seed(1)

'''
T3 - Programación Entera
Generación de Columnas
'''

'''
Cantidad de paquetes.
'''
m = 15

'''
Cantidad de productos.
'''
n = 30

'''
Constante de descuento.
'''
d = 0.1

'''
Stock de productos.
'''
b = list(np.random.randint(1, 10, m))

'''
Precios de productos.
'''
pr = list(-np.sort(-np.random.randint(3*m, 5*m, m)))
#print(pr)

'''
Función que implementa el modelo original, sin aplicar Dantzig-Wolfe.
'''
def original(m, n, d, b, pr, show_sol=False):

    I = range(m)
    J = range(n)
    K = range(m)

    mip = Model()
    mip.Params.OutputFlag = 0

    x = mip.addVars(I, J, vtype=GRB.BINARY, name="x")
    y = mip.addVars(I, K, J, vtype=GRB.BINARY, name="y")

    mip.setObjective(
        quicksum(
            pr[i] * (1 - d) ** k * y[i, k, j] for i in I for k in K for j in J),
        GRB.MAXIMIZE)

    mip.addConstrs(quicksum(x[i, j] for j in J) <= b[i] for i in I)
    mip.addConstrs(
        quicksum(y[i, k, j] for k in K) == x[i, j] for i in I for j in J)
    mip.addConstrs(quicksum(y[i, k, j] for i in I) <= 1 for k in K for j in J)
    mip.addConstrs(
        y[i, k, j] + y[ii, kk, j] <= 1 for i in I for ii in I for k in K for kk
        in K for j in J if i < ii and k > kk)

    mip.update()

    t1 = time.time()
    mip.optimize()
    t2 = time.time()

    print(f'Modelo Naive resuelto en {(t2-t1):.2f} segundos.')
    print(f'objVal = {mip.objVal}')
    print()

    if show_sol:
        for key, value in x.items():
            if value.X:
                print(f'{key}: {int(value.X)}')

    #val_x = {key: int(value.X) for key, value in x.items() if value.X}
    #val_y = {key: int(value.X) for key, value in y.items() if value.X}

    #return mip.objVal, val_x, val_y


def column_generation(m, n, d, b, pr, show_sol=False):

    I = range(m)
    R = range(m)

    '''
    Formulamos el problema Maestro.
    '''
    master = Model()
    master.Params.OutputFlag = 0

    '''
    Resolveremos la relajación lineal.
    '''
    w = master.addVars(R, lb=0, name='w')

    stock_constrs = {}
    for i in I:
        stock_constrs[i] = master.addConstr(w[i] <= b[i], name=f'stock[{i}]')

    pack_constr = master.addConstr(quicksum(w[p] for p in R) == n, name='pack')

    c = pr
    master_obj = quicksum(c[p] * w[p] for p in R)
    master.setObjective(master_obj, sense=GRB.MAXIMIZE)

    master.update()

    """

    val_w = {key: int(value.X) for key, value in w.items() if value.X}
    
    val_u = {key: int(value.X) for key, value in u.items() if value.X}
    val_v = {key: int(value.X) for key, value in v.items() if value.X}
    
    """

    '''
    ----------------------------------------------------------------------------
    '''

    K = range(m)

    '''
    Formulamos el problema de pricing.
    '''
    pricing = Model()
    pricing.Params.OutputFlag = 0

    u = pricing.addVars(I, K, vtype=GRB.BINARY)
    v = pricing.addVars(I, vtype=GRB.BINARY)

    c1 = pricing.addConstrs(quicksum(u[i, k] for k in K) == v[i] for i in I)
    c2 = pricing.addConstrs(quicksum(u[i, k] for i in I) <= 1 for k in K)
    c3 = pricing.addConstrs(
        u[i, k] + u[ii, kk] <= 1 for i in I for k in K for ii in I if i < ii for
        kk in K if k > kk)


    '''
    ----------------------------------------------------------------------------
    '''

    new_m = m
    t1 = time.time()

    while True:
        master.optimize()

        pi = {}
        for key in stock_constrs:
            pi[key] = stock_constrs[key].Pi

        mu = pack_constr.Pi

        pricing_obj_1 = quicksum(
            quicksum(pr[i] * ((1 - d) ** (k - 1)) * u[i, k] for k in K) for i in
            I)
        pricing_obj_2 = quicksum(pi[i] * v[i] for i in I)
        pricing_obj_3 = mu

        pricing_obj = pricing_obj_1 - pricing_obj_2 - pricing_obj_3
        pricing.setObjective(pricing_obj, sense=GRB.MAXIMIZE)

        pricing.update()

        pricing.optimize()
        pricing_objVal = pricing.objVal

        if pricing_objVal <= 0:
            master.update()
            break

        col = Column()
        for i in I:
            col.addTerms(v[i].X, stock_constrs[i])
        col.addTerms(1, pack_constr)
        #print(col)

        evaluated_cost = sum(
            sum(pr[i] * ((1 - d) ** (k - 1)) * u[i, k].X for k in K) for i in I)

        w[new_m] = master.addVar(obj=evaluated_cost, column=col, lb=0, name='w')
        master.update()
        new_m += 1

    '''
    ----------------------------------------------------------------------------
    '''

    for key, value in w.items():
        value.vtype = GRB.INTEGER

    master.update()
    master.optimize()

    t2 = time.time()

    print(f'Modelo Entero de Generación de Columnas resuelto en {(t2-t1):.2f} segundos.')
    print(f'objVal = {master.objVal}')
    print()

    if show_sol:
        for key, value in w.items():
            if value.X:
                print(f'{key}: {int(value.X)}')


show_sol = False

original(m, n, d, b, pr, show_sol)

print('---------------------------------------------------------------------\n')

column_generation(m, n, d, b, pr, show_sol)

print('---------------------------------------------------------------------\n')

print()

reverse = False

if reverse:

    print('Si revertimos el orden de precios:\n')
    pr.reverse()

    print('---------------------------------------------------------------------\n')

    original(m, n, d, b, pr, show_sol)

    print('---------------------------------------------------------------------\n')

    column_generation(m, n, d, b, pr, show_sol)

    print('---------------------------------------------------------------------\n')

print('Es claro que el modelo de Generación de Columnas es muy superior al '
      'modelo Naive, tanto en rapidez como en calidad de las soluciones.')
print()
print('Además, podemos apreciar que, al revertir el orden de precios, el modelo '
      'Naive se vuelve significativamente más lento (unas 4 veces) y con mucho')
print('peores soluciones, mientras que el modelo de Generación de Columnas, '
      'aunque también empeora, no sufre tanto en tiempo (aumenta unas 1.5 veces) ')
print('ni en calidad de las soluciones como su contraparte.')