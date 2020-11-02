from BBTree import *
from random import seed, randint
import sys
import time

################################################################################

B = 10
n = 1000

seed(0)

if n >= sys.getrecursionlimit():
    sys.setrecursionlimit(n+10)

'''
Condiciones iniciales.
v es diccionario de objetos {i: weight[i]}
s0 corresponde al arreglo de cajas iniciales, en que se usa una por objeto.
'''

v = {j: randint(1, B-1) for j in range(n)}
s0 = {j: {j} for j in v}

################################################################################

'''
Resolvemos la formulación IP (Naive) del problema de Bin Packing. Se demora
mucho.
'''

solve_ip = False
if solve_ip:

    t1 = time.time()
    ip_model, x, y = ip(B, v)
    ip_model.optimize()
    t2 = time.time()

    print(f'\nSolved IP in [{t2-t1:.3f}] seconds.')
    print(f'{int(ip_model.NodeCount)} nodes visited.')
    print(f'IP objVal: {ip_model.objVal}')
    print()

################################################################################

'''
Resolvemos la formulación de Branch and Price del problema de Bin Packing. Tiene
un comportamiento mucho mejor que el IP.
'''

bfs = True
dfs = False

t3 = time.time()

lpm, z0 = lp(s0, v)
m, z, s = rlp_left(lpm, z0, s0, B, v)

print(f'Relaxed objVal: {m.objVal}.')

block_print = True
if block_print:
    sys.stdout = open(os.devnull, 'w')

root = BBTree(m, z, s, B, v)
root.branch_and_price(dfs)

t4 = time.time()

if block_print:
    sys.stdout = sys.__stdout__

print(f'Solved Br&P in [{t4-t3:.3f}] seconds.')
print(f'{BBTree.nodes} nodes visited.')

objVal = BBTree.incumbent
sol = BBTree.best_sol
best_tree = BBTree.best_tree
s = BBTree.s

print(f'Br&Pr objVal: {objVal}')

soldict = {u for u, x in sol.items() if x.X}
built_sol = [s[c] for c in soldict]

recovering_dict = best_tree.recover_pairs()
if recovering_dict:
    recovered_boxes = recovered(recovering_dict)

    for box in built_sol:
        for newbox, crs in recovered_boxes.items():
            if newbox in box:
                box.remove(newbox)
                box.update(crs)

print(f'Solution:')
print(built_sol)
