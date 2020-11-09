from gurobipy import *
import numpy as np
from gurobi_functions import *

#np.random.seed(1)

'''
T2 - Programación Entera
Planos separadores en poliedro
'''

'''
Dimensión del poliedro. Además, serán 2(n + n^2) restricciones.
'''
n = 4

'''
Cantidad de vectores a generar.
'''
t = 4

'''
Parámetro que, de ser True, genera sólo vectores que cumplen con que pertenecen
al poliedro.
'''
todas_factibles = False

'''
Vectores en B = [0, n]^n
'''
vectors = [[np.round(np.random.uniform(0, n), 4)for c in range(n)]
           for j in range(t)]

#u = [1, 2, 3, 4, 5]
#print(f'u = {u}, suman = {sum(u)}')


'''
Variable que indica si es la primera vez que se genera un plano cortante.
'''
first = True

for c in range(t):

    if todas_factibles:
        r = [np.random.uniform(1, 2) for i in range(n)]
        s = sum(r)
        r = [ (n/2)*(n+1) * (i / s) for i in r]
        u = r

    else:
        u = vectors[c]

    #u = [2, 1, 3]

    print(f'u = {u}')
    print(f'Sus componentes suman {sum(u)}')

    '''
    Instanciamos el modelo.
    '''
    m = Model()

    '''
    Agregamos las variables al modelo. Esto funcionará de la siguiente manera: el
    modelo cuenta con las variables z^k y un vector u dado. Para determinar si u
    pertenece a P, se pregunta: ¿existen z^k tales que (x, z^1, ..., z^n) es
    factible en Q?
    
    El diccionario de variables z presenta keys (k, j), siendo k el k-ésimo vector
    y j la j-ésima componente del mismo.
    '''
    z = {}
    for k in range(n):
        for j in range(n):
            z[k, j] = m.addVar(lb=-GRB.INFINITY, name=f'z[{k},{j}]')

    '''
    Agregamos las restricciones al modelo.
    '''

    for k in range(n):
        m.addConstr(quicksum(z[k, j] for j in range(n)) == k + 1)

    for j in range(n):
        m.addConstr(quicksum(z[k, j] for k in range(n)) == u[j])

    for j in range(n):
        for k in range(n):
            m.addConstr(z[k, j] <= 1)
            m.addConstr(z[k, j] >= 0)

    '''
    Seteamos la función objetivo y el sentido de la optimización.
    '''
    m.setObjective(0, sense=GRB.MINIMIZE)

    '''
    Seteamos que Gurobi no printee información de todas las iteraciones y que nos
    muestre la información acerca del certificado de infactibilidad. Luego,
    corremos el modelo.
    '''
    m.Params.OutputFlag = 0
    m.Params.InfUnbdInfo = 1
    m.optimize()

    '''
    Obtenemos el número de variables y restricciones. Los necesitaremos a
    futuro.
    '''
    n_restrs = len(m.getConstrs())
    n_vars = len(z)

    #print(f'm = {n_restrs} restricciones, n = {n_vars} variables.')

    if m.status == GRB.Status.INFEASIBLE:

        print('Modelo infactible')

        '''
        Obtenemos un rayo de escape del dual. Así, generaremos un plano cortante
        Pi^T Ax <= Pi^T b tal que es desigualdad válida para P, pero imposible de
        satisfacer para el vector x.
        '''
        pi = m.FarkasDual
        #print(f'pi = {pi}, len = {len(pi)}')

        if first:
            '''
            Generamos la matriz A.
            '''
            matrix_generator = get_matrix_coo(m)
            A = [[0 for j in range(n_vars)] for i in range(n_restrs)]
            for i, j, coef in matrix_generator:
                A[i][j] = coef

            first = False

        '''
        Generamos el vector b.
        '''
        RHS = [c.RHS for c in m.getConstrs()]
        #print(f'RHS = {RHS}, len = {len(RHS)}')

        '''
        Generamos el plano cortante.
        '''
        #print()
        pi_traspuesto_A = []
        for i in range(len(pi)):
            x = 0
            new_row = []
            for j in range(n_vars):
                x = A[i][j] * pi[i]
                new_row.append(x)
            #print(new_row)
            pi_traspuesto_A.append(new_row)

        """
        print('\n\n\n\n')
        for c in pi_traspuesto_A:
            print(c)
        print('\n\n\n\n')
        """

        result = []
        for j in range(len(pi_traspuesto_A[0])):
            x = 0
            for i in range(len(pi_traspuesto_A)):
                x += pi_traspuesto_A[i][j]
            result.append(x)

        #print(result)

        #print(f'piTA = {pi_traspuesto_A}, len = {len(pi_traspuesto_A)}\n')

        dvars = m.getVars()
        var_indices = {v: i for i, v in enumerate(dvars)}

        V = f''
        for comp in range(len(result)):
            if result[comp]:
                if result[comp] < 0:
                    V += f'{result[comp]} {dvars[comp].VarName} '
                else:
                    V += f'+{result[comp]} {dvars[comp].VarName} '

        if not V:
            V = '0 '

        piTb = f'{V} = '
        for i in range(len(pi)):
            if pi[i] and RHS[i]:
                if i >= n and i <= 2*n - 1:
                    '''
                    Las componentes de u corresponden a las que van desde n hasta 2n - 1.
                    '''
                    if pi[i] < 0:
                        piTb += f'{pi[i]} u[{i-n}] '
                    else:
                        piTb += f'+{pi[i]} u[{i-n}] '
                else:
                    if pi[i] * RHS[i] < 0:
                        piTb += f'{pi[i] * RHS[i]} '
                    else:
                        piTb += f'+{pi[i] * RHS[i]} '
        print(piTb)

    else:
        print(f'u = {u} pertenece a P.')

    print('--------------------------------------------------------------')

print('\n\n')
print('-----------------------------------------------------------------------------------------------------')
print('Dado que pi^T A = 0, por el Lema de Farkas se concluye que para que '
      'Ax = b sea factible, pi^T b debe \nser igual a 0.')
print()
print('Se concluye que, al ser 0 <= u[j] <= n, el plano que los separa es que '
      'sus componentes sumen n(n+1)/2.\nSe ve que todo vector aleatorio '
      'generado de manera tal que sus componentes sumen n(n+1)/2, es '
      'factible,\ny cualquier otro en que sus componentes no sumen n(n+1)/2 es infactible. '
      'Esto se comprueba cambiando el\nparámetro todas_factibles a '
      'True.')
print('----------------------------------------------------------------------------------------------------')