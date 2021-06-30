from system import *
from time import time
from policies import *

'''
Generamos una instancia.
'''
commitment_prob = 0.15

prev_commitments = generatePreviousCommitments(I, W_, commitment_prob)
arrivals = generateArrivals(arrRates, T_, cutoffTime)
waves = generateWaves(waveTimes)

instance = waves + arrivals
# print(instance)
print(f'Compromisos iniciales: {prev_commitments}')

analysis = instanceAnalysis(instance)
print(f'Solicitudes totales a cada nodo: {dict(analysis)}')

'''
Seteamos la política e instanciamos el sistema.
'''
# policy = Myopic()
policy = Apriori()
# policy = RolloutApriori()
system = System(nodes, edges, penalties, policy)

'''
Corremos la simulación.
'''
tic = time()
system.simulate(T_, prev_commitments, W_, instance)
toc = time()

print(f'Simulated instance with {type(policy).__name__} policy '
      f'in {toc-tic:.2f} seconds.')
system.showStats()
