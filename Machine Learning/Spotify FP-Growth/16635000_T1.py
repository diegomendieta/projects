from arbol import Raiz, potencia
from funciones import dataset, load_data, sort_playlists

'''
Una cota de 15 corre en un tiempo razonable y genera 28 Frequent Patterns. Esta
corresponde a un abs_support de 0.000113
'''
cota_support = 15
cota_abs_support = 0


"""
'''
Cargamos los datos desde la BD.
'''
data = load_data('spotify.npy')

'''
Generamos un DataFrame filtrado por una cota de supports y ordenado
decrecientemente.
'''
DataFrame = dataset(data, cota_support, cota_abs_support)
#DataFrame = dataset(data, 0)
#print(DataFrame.describe())
'''
Descripción de abs_support:
- Promedio: 0.000037
- Min:      0.000008
- Max:      0.005439
- 75%:      0.000023
'''

'''
Ordenamos cada playlist según el número de apariciones (soporte) de las
canciones, desechando aquellas que no cumplan con la cota.
'''
sorted_playlists = sort_playlists(data, DataFrame)

'''
Armamos el árbol.
'''
arbol = Raiz()
for playlist in sorted_playlists:
    arbol.agregar_secuencia(playlist, arbol)
"""


'''
Generamos los Frequent Patterns. Esta función retorna un diccionario cuyas keys
son los FP y los values respectivos son la cantidad de veces que aparece
el conjunto en la base de datos.
'''
def fp(arbol):
    cpb_dict = arbol.cpb_dict()
    cfp_tree = arbol.cfp_tree(cpb_dict)
    fp = arbol.fp(cfp_tree)
    return fp


'''
Filtra un diccionario generado por generate, según distintos criterios.
'''
def filter_dict(dict, confidence, lift):
    retorno = {tupla: values for tupla, values in dict.items() if
               (values[1] >= confidence and values[2] >= lift)}
    return retorno


'''
Aplicamos el algoritmo a la base de datos.
'''
def fit(data, DataFrame):

    #data = load_data(path)
    #DataFrame = dataset(data, cota_support, cota_abs_support)
    sorted_playlists = sort_playlists(data, DataFrame)

    arbol = Raiz()
    for playlist in sorted_playlists:
        arbol.agregar_secuencia(playlist, arbol)

    frequent_patterns = fp(arbol)

    return frequent_patterns


'''
Generamos las reglas de asociación pertinentes.
'''
def generate(path, support=0, abs_support=0, confidence=0, lift=0):

    data = load_data(path)
    DataFrame, length = dataset(data, support, abs_support)

    frequent_patterns = fit(data, DataFrame)
    #print(frequent_patterns)

    '''
    Creamos un diccionario cuyas keys son un conjunto de canciones X, y los
    values correspondientes son una lista de la forma [Y, conf(X->Y)]
    '''
    d = {}
    for fp, n in frequent_patterns.items():
        subconjuntos = potencia(fp)
        for sub in subconjuntos:
            if not sub:
                continue
            if len(sub) == 1:
                soporte = int(DataFrame.loc[DataFrame['name'] == sub[0], 'number'].values)
                #print(soporte)
                cjto_nuevo = list(fp)
                cjto_nuevo.remove(sub[0])
                confianza = float(n/soporte)
                #print(f'sub: {sub}, cjto_nuevo: {cjto_nuevo}')

                if len(cjto_nuevo) == 1:
                    soporte_nuevo = int(DataFrame.loc[DataFrame['name'] == cjto_nuevo[0], 'number'].values)
                else:
                    if tuple(cjto_nuevo) not in frequent_patterns:
                        continue
                    soporte_nuevo = frequent_patterns[tuple(cjto_nuevo)]

                lifte = (confianza / soporte_nuevo) * length
                #print(f'conf: {confianza}, soporte_nuevo: {soporte_nuevo}, lifte: {lifte}')

                d[tuple(sub)] = [cjto_nuevo, confianza, lifte]
            else:
                tupla = tuple(sub)
                if tupla not in frequent_patterns:
                    continue
                y = tuple(set(fp) - set(sub))
                soporte_x = frequent_patterns[tuple(sub)]
                confianza = float(n/soporte_x)

                if len(y) == 1:
                    soporte_nuevo = int(DataFrame.loc[DataFrame['name'] == y[0], 'number'].values)
                else:
                    if tuple(y) not in frequent_patterns:
                        continue
                    soporte_nuevo = frequent_patterns[tuple(y)]

                lifte = (confianza / soporte_nuevo) * length
                d[tupla] = [y, confianza, lifte]

    retorno = filter_dict(d, confidence, lift)
    return retorno


d = generate('spotify.npy', 15, 0, 1, 0)
for element in d:
    print(f'{element}: {d[element]}')
print('\n\n\n')

d = generate('spotify.npy', 15, 0, 0, 3000)
for element in d:
    print(f'{element}: {d[element]}')

