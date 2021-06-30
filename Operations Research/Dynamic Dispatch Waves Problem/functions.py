from instance import *
from functools import reduce
from collections import defaultdict


def upcomingWaves(t):
    '''
    Retorna las olas por venir en t o después.
    '''
    return [w for w in W if waveTimes[w] <= t]


def upcomingWavesZero(t):
    '''
    Retorna las olas por venir en t o después, más la ola en t=0.
    '''
    return upcomingWaves(t) + [0]


def edgeTime(i, j):
    '''
    Retorna el tiempo que se demora el vehículo en recorrer la arista (i, j).
    '''
    # return gamma * edges[i, j]
    return edges[i, j]


def latestPossibleDispatchWave(i, j):
    '''
    Retorna la última ola de despacho en la que es factible visitar i y j.
    '''
    total_time = edgeTime(i, j) + serviceTimes[i] + serviceTimes[j]
    total_time += serviceTimes[0] if (i > 0 and j > 0) else 0
    total_time += edgeTime(0, i) if i > 0 else 0
    total_time += edgeTime(0, j) if j > 0 else 0

    for w in sorted(W, reverse=False):
        wt = waveTimes[w]
        if wt - total_time >= 0:
            return w
    raise Exception('Hay aristas que no es factible recorrer')


def feasibleDispatchNodes(w):
    return {i for i in I if w >= latestPossibleDispatchWave(0, i)}


def feasibleDispatchEdges(w):
    return {(i, j) for i, j in edges if w >= latestPossibleDispatchWave(i, j)}


def cutSets(w, S):
    '''
    Retorna los conjuntos {(i, j)} en feasibleDispatchEdges(w) tales que i está
    en S y j no está en S.
    '''
    e = feasibleDispatchEdges(w)
    return [(i, j) for i, j in e if (i in S and j not in S)]


def adjustedTimeSpent(i, j):
    '''
    Retorna el tiempo aproximado de servicio entre los nodos i y j.
    '''
    return edgeTime(i, j) + 0.5 * serviceTimes[i] + 0.5 * serviceTimes[j]


def maxRequests(arrivals, i, w):
    '''
    Retorna la cantidad de solicitudes que llegan hasta w.
    '''
    wave_time = waveTimes[w]
    counter = 0
    for arr in reversed(arrivals):
        if arr.time < wave_time:
            break
        if arr.node == i:
            counter += 1
    return counter


# https://thepythonguru.com/python-builtin-functions/reduce/
def powerset(lst):
    """
    Retorna el conjunto potencia de un conjunto.
    """
    return reduce(lambda rslt, x: rslt + [subset + [x] for subset in rslt],
                  lst, [[]])


def releaseWave(t):
    """
    Retorna la ola en que una solicitud es liberada.
    """
    for w in sorted(waveTimes.keys(), reverse=True):
        wt = waveTimes[w]
        if t - p >= wt:
            return w
    raise Exception('Tiempo de liberación de solicitud infactible.')


def expectedNumberOfRequests(i, w, t=T_):
    """
    Retorna la cantidad esperada de solicitudes hacia i desde t en adelante,
    liberadas en la ola w
    """
    return arrRates[i] * max(0, t - max(cutoffTime, waveTimes[w] + p))


def instanceAnalysis(instance):
    """
    Retorna un diccionario con la cantidad de solicitudes que llegan hacia cada
    nodo en una instancia.
    """
    arrivals = defaultdict(int)
    for event in instance:
        if isinstance(event, Arrival):
            arrivals[event.node] += 1
    return {key: arrivals[key] for key in sorted(arrivals.keys())}
