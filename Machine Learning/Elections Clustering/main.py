from functions import *
from time import time

'''
Seteamos una semilla.
'''
np.random.seed(0)

'''
Número de clusters a buscar.
'''
k = 15

'''
Criterio de detención. Si los clusters se mueven una distancia menor que delta
en una iteración, parar.
'''
delta = 0.0001

'''
Path de la Base de Datos Electoral.
'''
path_electoral = '1-Base-de-Datos-Electoral.xlsx'

'''
Path de la Base de Datos de Comunas.
'''
path_comunas = 'Comunas_Lat-Long.csv'

'''
Tamaño de la muestra a tomar. Si es cero, no se toma muestra.
'''
sample_size = 0

'''
Booleano que indica si se muestran las iteraciones de k-means o no.
'''
show_iters = False

'''
String que indica cargo a buscar.
'''
cargo = 'Presidente'

'''
String que indica nombre del primer candidato a buscar.
'''
candidato_1 = 'Michelle Bachelet Jeria'

'''
String que indica nombre del primer candidato a buscar.
'''
candidato_2 = 'Sebastian Piñera Echenique'

'''
--------------------------------------------------------------------------------
'''

t1 = time()

df_dict = load_candidate_dict(path_electoral, sample_size)
comunas_dict = load_latlong_dict(path_comunas)

t2 = time()

print(f"El algoritmo se demoró {t2-t1:.2f} segundos en cargar las BD's.")
print()

df = df_dict[cargo][candidato_1]
# (cargo, comuna, nombrecand1, siglapart_text, votot)
print(f'DataFrame: tipo {type(df)}')
print(df)
print()

t2 = time()

original_points = original_point_dict(df)
print('Original points: ')
print(original_points)

print()

correspondencias = correspondencies(df)
print('Correspondencias: ')
print(correspondencias)

print()

for clase in correspondencias:
    df[clase] = df[clase].fillna(-1)
    df[clase] = df[clase].replace(correspondencias[clase])

for clase in df.columns:
    if clase not in correspondencias:
        df[clase] = df[clase].fillna(-1)

for clase in df.columns:
    if df[clase].min() != df[clase].max():
        df[clase] = (df[clase] - df[clase].min())/(df[clase].max() - df[clase].min())

t3 = time()

print(f'El algoritmo se demoró {t3-t2:.2f} segundos en preprocesar la BD.')

print()

cols = list(df.columns)
dim = len(cols)
#La tercera columna indica región, la cuarta comuna, y la octava partido.

lb_dict = {col: 0 for col in df.columns}
ub_dict = {col: 1 for col in df.columns}

t4 = time()

clusters = random_clusters(k, dim, lb_dict, ub_dict)
points = point_dict(df)

print('Clusters: ')
print(clusters)

print()

print('Points: ')
print(points)

print()

final_clusters = k_means(points, clusters, dim, delta, k, show_iters)
assignments = assign_to_cluster(points, final_clusters)
belongings = belongs_to_cluster(assignments, k)

t5 = time()

print(f'El algoritmo se demoró {t5-t4:.2f} segundos en llevar a cabo.')

print()

print('Coordenadas de clusters: ')
for c in final_clusters:
    print(f'{c}: {list(final_clusters[c])}')
print()

print('Pertenencias a clusters: ')
for c in belongings:
    print(f'{c}: {belongings[c]}')
print()

print('Tamaños de clusters: ')
for c in belongings:
    print(f'{c}: {len(belongings[c])}')
print()

#show_results(belongings, original_points)
