import numpy as np
import pandas as pd

'''
Función que carga la base de datos y retorna un diccionario de forma:
{cargo: {candidato: df}}.
https://stackoverflow.com/questions/19790790/splitting-dataframe-into-
multiple-dataframes
'''
def load_candidate_dict(path, sample_size=0):
    df = pd.read_excel(path, index_col=None,
                       usecols='C,T,Y,AF,AM')

    #(cargo, comuna, nombrecand1, siglapart_text, votot)

    if sample_size:
        df = df.sample(sample_size)

    grouped = list(df.groupby(['cargo']))
    df_dict = {cargo: df for (cargo, df) in grouped}

    for cargo, df in df_dict.items():
        grouped = list(df.groupby(['nombrecand1']))
        df_dict[cargo] = {cand: df for (cand, df) in grouped}

    return df_dict

'''
Función que retorna un diccionario cuyas keys son las comunas y sus values son
una tupla (latitud, longitud).
'''
def load_latlong_dict(path):
    with open(path, 'r', encoding='UTF-8') as file:
        file.readline()
        dict_comunas = {}
        for linea in file:
            linea = linea.strip().split(',')
            comuna, lat, long = linea[0], float(linea[1]), float(linea[2])
            dict_comunas[comuna] = (lat, long)

    return dict_comunas


'''
Función que retorna un diccionario con las correspondencias entre los valores
reales (categóricos) y los numéricos correspondientes.
'''
def correspondencies(df):
    correspondencias = {}
    for col in list(df.columns):
        if df[col].dtype != object:
            continue
        d, n = {}, 0
        values = list(df[col].unique())
        for key in values:
            d[key] = n
            n += 1
        correspondencias[col] = d
    return correspondencias

'''
Función que retorna un diccionario cuyas keys son los puntos y sus values son
arrays con las coordenadas correspondientes.
'''
def point_dict(df):
    df_dict = df.to_dict(orient='records')
    print('df.to_dict: ')
    print(df_dict)

    print()

    points = {p: np.array(tuple(df_dict[p].values()))
              for p in range(len(df_dict))}
    return points

'''
Función que almacenará los valores originales de los puntos.
'''
def original_point_dict(df):
    df_dict = df.to_dict(orient='records')
    points = {p: (tuple(df_dict[p].values())) for p in range(len(df_dict))}
    return points

'''
Función que retorna "k" puntos aleatorios, correspondientes a los clusters.
'''
def random_clusters(k, dim, lb_dict=None, ub_dict=None):
    if lb_dict and ub_dict:
        clusters = {}
        for p in range(k):
            arr = [np.random.uniform(lb_dict[col], ub_dict[col])
                   for col in lb_dict]
            clusters[p] = np.around(np.array(arr), 2)
    else:
        clusters = {p: np.random.uniform(0, 1000, size=dim) for p in range(k)}
    return clusters

'''
Función que calcula la distancia entre dos puntos (dados en forma de arrays).
#https://stackoverflow.com/questions/1401712/how-can-the-euclidean-distance-be-
calculated-with-numpy
'''
def distance(p1, p2):
    return np.sqrt(np.sum((p1-p2)**2))

'''
Función que retorna un diccionario de distancias entre puntos y clusters.
'''
def distance_to_clusters(points, clusters):
    dicc = {}
    for p in points:
        arr_p = points[p]
        dicc[p] = {}
        for c in clusters:
            arr_c = clusters[c]
            dicc[p][c] = distance(arr_p, arr_c)
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
def belongs_to_cluster(assignments, k):
    cls = {}
    for p in assignments:
        c = assignments[p]
        try:
            cls[c].append(p)
        except KeyError:
            cls[c] = []
            cls[c].append(p)
    for c in range(k):
        if c not in cls:
            cls[c] = []
    return cls

'''
Función que calcula la nueva posición de un cluster, según los puntos que le
corresponden, y retorna un diccionario con las nuevas posiciones.
'''
def refresh_clusters(points, belongings, dim):
    new_clusters = {}
    for cl in belongings:
        suma = [0] * dim
        for p in belongings[cl]:
            arr_p = points[p]
            for n in range(dim):
                suma[n] += arr_p[n]
        try:
            promedios = [suma[n]/len(belongings[cl]) for n in range(dim)]
        except ZeroDivisionError:
            promedios = [0.0001] * dim
        new_clusters[cl] = np.array(promedios)
    return new_clusters

'''
Función que lleva a cabo una iteración, reposicionando los clusters.
'''
def iterate(points, clusters, dim, k):
    assignments = assign_to_cluster(points, clusters)
    belongings = belongs_to_cluster(assignments, k)
    new_clusters = refresh_clusters(points, belongings, dim)
    return new_clusters

'''
Función que echa a andar el algoritmo.
'''
def k_means(points, clusters, dim, delta, k, show_iters):
    iters = 0
    suma = 0
    while True:
        if show_iters and suma:
            if suma:
                print(f'Iteración n° {iters}.', end=' ')
                print(f'Distancia de movimiento: {suma:.3f}.')
            iters += 1
        old_clusters = clusters
        clusters = iterate(points, clusters, dim, k)
        distancias = [distance(old_clusters[c], clusters[c])
                      for c in clusters]
        suma = sum(distancias)
        if suma <= delta:
            return clusters

'''
Función que muestra resultados.
'''
def show_results(belongings, point_dict):
    results = {}
    for cluster in belongings:
        results[cluster] = {}
        points = belongings[cluster]
        #print(f'Cluster {cluster}:')
        for p in points:
            point = point_dict[p]
            # (cargo, comuna, nombrecand1, siglapart_text, votot)
            cargo, comuna, cand, partido, votos = point
            if region not in results[cluster]:
                results[cluster][region] = {}
            if partido not in results[cluster][region]:
                results[cluster][region][partido] = 0
            results[cluster][region][partido] += 1
        #print()
        print(f'Cluster {cluster}: ')
        for region in results[cluster]:
            s = sorted(results[cluster][region].items(),
                       key=lambda x: x[1], reverse=True)
            print(f'[{region}]: {s}')
        print()
    #return results