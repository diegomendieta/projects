import numpy as np
from sortedcontainers import SortedList
from params import p


class Event:
    def __init__(self, time):
        self.time = time


class Arrival(Event):
    '''
    Eventos de tipo 'llegada de solicitud'
    '''
    def __init__(self, node, time):
        super().__init__(time)
        self.node = node

    def __repr__(self):
        return f'Arrival[Node={self.node}, Time={self.time:.2f}, ' \
               f'ReleaseTime={self.time - p:.2f}]'


class DispatchDecision(Event):
    '''
    Eventos de tipo 'decisión de despacho'
    '''
    def __init__(self, time, wave):
        super().__init__(time)
        self.wave = wave

    def __repr__(self):
        return f'DispatchDecision[Wave={self.wave}, Time={self.time:.2f}]'


def generateNodes(n, xlim=1, ylim=1):
    '''
    Genera los nodos en el plano cartesiano.
    Hardcodeado para 4 normales con el centro de distribución al medio.
    '''

    means_x = [0.25 * xlim, 0.75 * xlim]
    means_y = [0.25 * ylim, 0.75 * ylim]

    cov = [[0.125, 0],
           [0, 0.125]]

    points = [np.array([xlim/2, ylim/2])]
    for x in means_x:
        for y in means_y:
            sample = np.c_[np.random.multivariate_normal([x, y], cov, int(n/4))]
            # print(sample)
            points.extend(sample)

    return dict(zip(range(len(points)), points))


def generateRandomNormalNodes(n, stdev=0.5):
    """
    Genera nodos a partir de una normal multivariada, con media 0 y desviación
    estándar 0.5. El nodo 0 está en (0, 0).
    """
    points = [np.array([0, 0])]
    cov = [
        [stdev, 0],
        [0, stdev]
    ]
    sample = np.c_[np.random.multivariate_normal([0, 0], cov, n)]
    points.extend(sample)
    return dict(zip(range(len(points)), points))


def generateRandomUniformNodes(n, xlim=1, ylim=1):
    """
    Genera nodos según una distribución uniforme.
    """
    points = [np.array([xlim/2, ylim/2])]
    for _ in range(n):
        arr = np.array([np.random.uniform(0, xlim), np.random.uniform(0, ylim)])
        points.append(arr)
    return dict(zip(range(len(points)), points))


def generateEdges(node_dict):
    '''
    Genera los costos de las aristas de la red.
    No contiene aristas (i, i).
    Contiene aristas (i, j) y (j, i).
    '''
    edge_dict = {}
    for i in node_dict.keys():
        for j in node_dict.keys():
            if i == j:
                continue

            u, v = node_dict[i], node_dict[j]
            dist = np.linalg.norm(u - v)
            edge_dict[i, j] = np.round(dist, 2)

    return edge_dict


def generateArrivals(arrival_rates, T, cutoff_time):
    '''
    Genera las llegadas de solicitudes. Retorna una SortedList de Arrivals.
    '''

    # Implementamos una lista que siempre está ordenada (funciona como heap)
    arrivals = SortedList(key=lambda x: x.time)
    for node, rate in arrival_rates.items():
        t = T
        while True:
            exp = np.round(np.random.exponential(1/rate), 2)
            t -= exp
            if t < cutoff_time:
                break
            arrivals.add(Arrival(node, t))

    return arrivals


def generateWaves(wave_times):
    """
    Genera las decisiones de despacho. Retora una SortedList de
    DispatchDecisions.
    """
    waves = SortedList(key=lambda x: x.time)
    for w, t in wave_times.items():
        waves.add(DispatchDecision(t, w))
    return waves


def generatePreviousCommitments(I, W_, prob=0.15):
    '''
    Genera un vector de compromisos iniciales.
    '''
    commitments = {}
    for i in I:
        rv = np.random.uniform(0, 1)
        if rv < prob:
            commitments[i] = W_
        else:
            commitments[i] = float('inf')
    return commitments
