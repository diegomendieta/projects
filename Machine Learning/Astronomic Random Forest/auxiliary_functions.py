import numpy as np
import pandas as pd
import time

'''
Divide la base de datos en un set de entrenamiento y uno de testeo, retornando
un tupla (df_train, df_test).

Basado en:
https://stackoverflow.com/questions/24147278/how-do-i-create-test-and-train-
samples-from-one-dataframe-with-pandas
'''
def preprocess(bd_path, seed=0):
    df = pd.read_csv(bd_path)
    if seed:
        train = df.sample(frac=0.8, random_state=seed)
    else:
        train = df.sample(frac=0.8)
    test = df.drop(train.index)
    return train, test


'''
Normaliza las columnas de un DataFrame, de forma que todos los floats queden
entre 0 y 1.

Basado en:
https://stackoverflow.com/questions/26414913/normalize-columns-of-pandas
-data-frame
'''
def normalize(df):
    copy = df.copy()
    for col in df.columns:
        if df[col].dtype == object:
            continue
        max = df[col].max()
        min = df[col].min()
        if not (max - min):
            continue
        copy[col] = (df[col] - min)/(max - min)
    return copy


'''
Retorna un diccionario que indica cuántas entradas hay de cada valor de un
atributo en un DataFrame.
'''
def attr_count(df, attr='Class'):
    return dict(df[attr].value_counts())


'''
Retorna el valor de un atributo determinado que más se repite.
'''
def most_repeated(df, attr='Class'):
    stats = attr_count(df, attr)
    m = max(stats, key=stats.get)
    return m


'''
Calcula la entropia en un DataFrame.
'''
def df_entropy(df, attr='Class'):
    d = attr_count(df, attr)
    props = {key: d[key]/len(df) for key in d}
    s = 0
    for val in props.values():
        if val == 0:
            continue
        s -= val * np.log2(val)
    return s


'''
Retorna dict de entropías según división por distintos atributos.
'''
def entropy_gain_dict(df):
    s_actual = df_entropy(df)
    d = {}
    for attr in df.columns:
        if attr == 'Class':
            continue
        df1, df2, mean = divide(df, attr)
        aux = (len(df1)*df_entropy(df1) + len(df2)*df_entropy(df2))/len(df)
        aux = s_actual - aux
        d[attr] = aux
    return d


'''
Retorna tupla (attr, S) por el cual conviene dividir el DataFrame.

Sacado de:
https://stackoverflow.com/questions/268272/getting-key-with-maximum
-value-in-dictionary
'''
def convenient_tuple(df):
    stats = entropy_gain_dict(df)
    m = max(stats, key=stats.get)
    return m, stats[m]


'''
Divide un DataFrame en dos (mayores o menores que la media), según un atributo.
'''
def divide(df, attr):
    mean = df[attr].mean()
    df1 = df[df[attr] <= mean]
    df2 = df[df[attr] > mean]
    return df1, df2, mean

import networkx as nx

'''
Sacado de https://stackoverflow.com/questions/29586520/can-one-get-hierarchical-
graphs-from-networkx-with-python-3
'''
def hierarchy_pos(G, root=None, width=1., vert_gap = 0.2, vert_loc = 0, xcenter = 0.5):
    if not nx.is_tree(G):
        raise TypeError('cannot use hierarchy_pos on a graph that is not a tree')

    if root is None:
        if isinstance(G, nx.DiGraph):
            root = next(iter(nx.topological_sort(G)))
        else:
            root = np.random.choice(list(G.nodes))

    def _hierarchy_pos(G, root, width=1., vert_gap = 0.2,
                       vert_loc = 0, xcenter = 0.5, pos = None, parent = None):
        if pos is None:
            pos = {root:(xcenter,vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        children = list(G.neighbors(root))
        if not isinstance(G, nx.DiGraph) and parent is not None:
            children.remove(parent)
        if len(children)!=0:
            dx = width/len(children)
            nextx = xcenter - width/2 - dx/2
            for child in children:
                nextx += dx
                pos = _hierarchy_pos(G,child, width = dx, vert_gap = vert_gap,
                                    vert_loc = vert_loc-vert_gap, xcenter=nextx,
                                    pos=pos, parent = root)
        return pos

    return _hierarchy_pos(G, root, width, vert_gap, vert_loc, xcenter)


################################################################################

if __name__ == '__main__':

    '''

    train, test = preprocess('FATS_GAIA.dat')
    df = test.head(100)
    df = normalize(df)

    inicio = time.time()
    print(entropy_gain_dict(df))
    print(convenient_tuple(df))
    final = time.time() - inicio
    print(f'El algoritmo demoró {final:.2f} segundos en realizarse.\n')
    
    '''

    print(np.random.choice([1, 2, 3, 4, 5]))
    import random
    print(random.choice([1, 2, 3, 4, 5]))


################################################################################