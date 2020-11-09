from simulation import *
from time import time
from random import seed
import sys
import os

'''
Seteamos una semilla para eliminar la aleatoriedad en cada iteración.
'''
semillas = True
if semillas:
    np.random.seed(0)
    seed(0)

planta = Planta()
print()

lista_dias = [1, 7, 30, 60]

for dia in lista_dias:

    printear_pasos = False
    if not printear_pasos:
        sys.stdout = open(os.devnull, 'w')  # bloqueamos prints

    inicio = time()
    planta.simular(dia * 24)

    if not printear_pasos:
        sys.stdout = sys.__stdout__  # reactivamos prints

    final = time()

    output = True
    path_output = f'resultados{dia}.txt'
    if output:
        orig_stdout = sys.stdout
        f = open(path_output, 'w')
        sys.stdout = f

    planta.mostrar_estadisticas()
    print()
    print(f'Tiempo en correr: {final-inicio:.3f} segundos.\n')

    if output:
        sys.stdout = orig_stdout
        f.close()
