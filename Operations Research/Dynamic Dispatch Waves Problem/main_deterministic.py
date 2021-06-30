from deterministic import *
from time import time

load = False
save = False

file_name = 'deterministic'
params_name = 'params'

if load:
    '''
    Cargamos el modelo.
    '''
    deterministic = Deterministic(None, None, None)
    deterministic.loadModel(file_name)

else:
    '''
    Generamos una instancia.
    '''
    prev_commitments = generatePreviousCommitments(I, W_)
    arrivals = generateArrivals(arrRates, T_, cutoffTime)

    # print(f'Arrivals: {arrivals}\n')

    '''
    Generamos un nuevo modelo.
    '''
    deterministic = Deterministic(prev_commitments, arrivals, penalties)
    deterministic.setVars(W)
    deterministic.setConstrs(W)
    deterministic.setObjective(W)

if save:
    '''
    Guardamos el modelo.
    '''
    deterministic.saveModel(params_name, file_name)

'''
Optimizamos el modelo determinístico.
'''
tic = time()
objVal = deterministic.solve()
toc = time()

print()
print(f'Deterministic model solved in {toc-tic:.2f} seconds.')
print(f'Total cost: {objVal:.2f}')
deterministic.showStats()

print()
plan_dict = {w: set() for i, w in deterministic.y}
for (i, w), val in deterministic.y.items():
    if val.X:
        plan_dict[w].add(i)
print(f'Plan: {plan_dict}')
