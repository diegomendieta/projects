from params import *
from instance_generation import *
import matplotlib.pyplot as plt

# Semilla aleatoria
np.random.seed(seed)

# Conjunto de periodos. Es descendiente (corresponde a cuántos tiempos restan
# hasta el final del día)
T = range(T_, -1, -1)

# Conjunto de olas (contiene a la ola 0, correspondiente a la del fin del día)
W = range(W_, -1, -1)

# Diccionario de tiempos en que ocurre cada ola
waveTimes = {w: int((T_/(W_ +1)) * w) for w in W}
print(f'waveTimes: {waveTimes}')

# Set de nodos (no contiene al centro de distribución (nodo 0))
I = range(1, I_ + 1)

# Set de nodos
# nodes = generateNodes(I_)
# nodes = generateRandomNormalNodes(I_, stdev)
nodes = generateRandomUniformNodes(I_, 50 * alpha, 50 * alpha)
print(f'nodes: {nodes}')

# Set de aristas con sus respectivas distancias
edges = generateEdges(nodes)
for edge, dist in edges.items():
    edges[edge] = round(dist, 2)
print(f'edges: {edges}')

# Set de tiempos de servicio
serviceTimes = {i: serviceTimeDistribution(serviceTimeLow, serviceTimeHigh)
                for i in I}
serviceTimes[0] = depotServiceTime
print(f'serviceTimes: {serviceTimes}')

# Tasas de llegada de pedidos
arrRates = {i: arrivalDistribution(lbdLow, lbdHigh) for i in I}
print(f'arrRates: {arrRates}')

# Penalizaciones por no servir a un nodo
# penalties = {i: penaltyDistribution(penaltyLow, penaltyHigh) for i in I}
penalties = {i: 1 + 2 * edges[0, i] for i in I}
print(f'penalties: {penalties}\n')

plot = False
if plot:
    x, y = [], []
    for i, (x_, y_) in nodes.items():
        x.append(x_)
        y.append(y_)

    # Generamos un scatterplot para visualizar la distribución geográfica.
    fig, ax = plt.subplots()

    ax.scatter(x[0], y[0], color='red')
    ax.scatter(x[1:], y[1:], color='blue')

    for i in range(len(x)):
        ax.annotate(i, (x[i], y[i]))

    plt.show()
