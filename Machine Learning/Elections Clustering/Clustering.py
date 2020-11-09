import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

'''
Seteamos una semilla.
'''
np.random.seed(0)

'''
Número de puntos por cluster a generar.
'''
N = 20

'''
Número de clusters a buscar.
'''
k = 3

'''
Criterio de detención. Si los clusters se mueven una distancia menor que delta
en una iteración, parar.
'''
delta = 0.5

'''
Pausa entre iteraciones.
'''
pausa = 1

'''
Generamos datos de modo que existan clusters.
'''
x1 = [np.random.randint(0, 21) for p in range(N)]
y1 = [np.random.randint(0, 21) for p in range(N)]

x2 = [np.random.randint(30, 51) for p in range(N)]
y2 = [np.random.randint(30, 51) for p in range(N)]

x3 = [np.random.randint(60, 81) for p in range(N)]
y3 = [np.random.randint(60, 81) for p in range(N)]

'''
Coordenadas de los puntos.
'''
x = x1+x2+x3
y = y1+y2+y3

'''
Diccionario de puntos.
'''
points = {p: (x[p], y[p]) for p in range(len(x))}

'''
Clusters.
'''
clusters = {c: (np.random.randint(0,81), np.random.randint(0, 81))
            for c in range(k)}

'''
Función que retorna la distancia euclidiana entre dos puntos.
'''
def distance(x1, y1, x2, y2):
    return np.sqrt((x1-x2)**2 + (y1-y2)**2)

'''
Función que retorna un diccionario de distancias entre puntos y clusters.
'''
def distance_to_clusters(points, clusters):
    dicc = {}
    for p in points:
        x1, y1 = points[p]
        dicc[p] = {}
        for c in clusters:
            x2, y2 = clusters[c]
            dicc[p][c] = distance(x1, y1, x2, y2)
    return dicc

'''
Función que retorna, para cada punto, el cluster más cercano, junto con la
distancia desde el punto hasta él.
'''
def assign_to_cluster(points, clusters):
    distances = distance_to_clusters(points, clusters)
    assignments = {}
    for p in points:
        l = list(distances[p].values())
        d = min(l)
        c = l.index(d)
        assignments[p] = c
    return assignments

'''
Función que retorna un diccionario cuyas keys son los clusters y sus values son
una lista con los puntos que le corresponden.
'''
def belongs_to_cluster(assignments):
    cls = {}
    for p in assignments:
        c = assignments[p]
        try:
            cls[c].append(p)
        except KeyError:
            cls[c] = []
            cls[c].append(p)
    return cls

'''
Función que calcula la nueva posición de un cluster, según los puntos que le
corresponden, y retorna un diccionario con las nuevas posiciones.
'''
def refresh_clusters(points, belongings):
    new_clusters = {}
    for cl in belongings:
        suma_x, suma_y = 0, 0
        for p in belongings[cl]:
            x, y = points[p]
            suma_x += x
            suma_y += y
        new_x, new_y = suma_x/len(belongings[cl]), suma_y/len(belongings[cl])
        new_clusters[cl] = (new_x, new_y)
    return new_clusters

'''
Función que plotea los puntos, junto con su cluster correspondiente.
'''
def cluster_plot(points, clusters, assignments, pausa):
    x, y = [], []
    for u, v in points.values():
        x.append(u)
        y.append(v)

    colours = {0: 'red', 1: 'green', 2: 'blue'}
    colour_assignments = [colours[c] for c in assignments.values()]

    fig, ax = plt.subplots(1, 1)

    plt.xlim(0, 90)
    plt.ylim(0, 90)

    ax.scatter(x, y, c=colour_assignments)
    for c in clusters:
        ax.scatter(clusters[c][0], clusters[c][1],
                    c=colours[c], marker='X', s=300)

    plt.draw()
    plt.pause(pausa)
    plt.close()

    fig.delaxes(ax)

    """

    plt.scatter(x, y, c=colour_assignments)

    for c in clusters:
        plt.scatter(clusters[c][0], clusters[c][1],
                    c=colours[c], marker='X', s=300)

    plt.show()
    
    """

'''
Función que lleva a cabo una iteración.
'''
def iterate(points, clusters, plot=True):
    assignments = assign_to_cluster(points, clusters)
    belongings = belongs_to_cluster(assignments)
    new_clusters = refresh_clusters(points, belongings)

    if plot:
        cluster_plot(points, new_clusters, assignments, pausa)
    else:
        print(new_clusters)

    return new_clusters


#clusters = {0: (10, 10), 1: (40, 40), 2: (70, 70)}

assignments = assign_to_cluster(points, clusters)
belongings = belongs_to_cluster(assignments)
cluster_plot(points, clusters, assignments, pausa)

while True:
    old_clusters = clusters
    clusters = iterate(points, old_clusters)
    if old_clusters == clusters:
        print('Done')
        break
