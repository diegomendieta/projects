import numpy as np
import pandas as pd

supports_filter = 100

'''
Indicadores disponibles: support, confidence y lift.
'''

'''
Cargamos la base de datos en una lista. Cada elemento de la lista será, a su
vez, una lista que representa una playlist. Además, hacemos que cada playlist
sea un set, para luego chequear pertenencia de manera eficiente.
'''
def load_data(path):
    data = [set(c) for c in
            np.load(f'{path}', allow_pickle=True).item().values()]
    return data


'''
Generamos un diccionario cuyas keys son las canciones y sus values son la
cantidad de veces que aparece cada canción en la base de datos.
'''
def supports_dict(data):
    supports = {}
    for playlist in data:
        for cancion in playlist:
            if cancion not in supports:
                supports[cancion] = 0
            supports[cancion] += 1
    return supports


'''
Creamos un DataFrame con las canciones y el número de apariciones para poder
operar fácilmente con ellas.
'''
def df_supports(supports):
    names = list(supports.keys())
    numbers = list(supports.values())

    dict_supports = {'name': names, 'number': numbers}
    df_supports = pd.DataFrame.from_dict(dict_supports)

    return df_supports


'''
Filtramos y sorteamos por número de apariciones. Notar que si el criterio es
que aparezcan más que el promedio, la base de datos reduce su tamaño a
18.833 canciones (alrededor de un 14% del original).
'''
def df_supports_filtered(df_supports, supports_benchmark, cota_abs=0):
    length = len(df_supports.index)
    df_supports['abs_support'] = df_supports['number'] / length
    if cota_abs:
        df_supports = df_supports[df_supports['abs_support'] > cota_abs]
    else:
        df_supports = df_supports[df_supports['number'] > supports_benchmark]
    df_supports = df_supports.sort_values(by=['number'], ascending=False)
    return df_supports


'''
Función que ordena y filtra la data, y retorna un DF.
'''
def dataset(data, cota_supports, cota_abs_support=0):
    supports = supports_dict(data)
    DataFrame = df_supports(supports)
    length = len(DataFrame.index)
    filtrado = df_supports_filtered(DataFrame, cota_supports, cota_abs_support)
    return filtrado, length


'''
Ahora, ordenamos las playlists según el número de apariciones totales.
'''
def sort_playlists(data, df_supports):

    filtered_names = df_supports['name'].unique()
    #print('Closer' in filtered_names)

    names_list = filtered_names.tolist()
    indexed_names = {}
    n = 1
    for name in names_list:
        indexed_names[name] = n
        n += 1

    l = []
    for playlist in data:
        aux = []
        for cancion in playlist:
            if cancion in indexed_names:
                tupla = (cancion, int(indexed_names[cancion]))
            else:
                #tupla = (cancion, 132920)
                continue
            aux.append(tupla)
        ordered_playlist = sorted(aux, key=lambda x: x[1])
        l.append(ordered_playlist)

    ordered_data = []
    for lista in l:
        aux = [u for (u, v) in lista]
        ordered_data.append(aux)

    return ordered_data
