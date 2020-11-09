import numpy as np
import pandas as pd
from functions import *

'''
Función que retorna un diccionario con las correspondencias entre los valores
reales (categóricos) y los numéricos correspondientes.
'''
def correspondencies(df):
    correspondencias = {}
    for col in list(df.columns):
        d, n, changed = {}, 0, False
        counts = dict(df[col].value_counts())
        for key in counts:
            if isinstance(key, int) or isinstance(key, float):
                break
            else:
                changed = True
                if key == 'NA':
                    d[key] = -1
                    continue
                d[key] = n
                n += 1
        if changed:
            correspondencias[col] = d
    return correspondencias

path = '1-Base-de-Datos-Electoral - copia.xlsx'
df = pd.read_excel(path, index_col=None,
                   usecols='B,C,F,P,R,V,W,Y,AA,AE,AG,AM,AN,AO')

df = df.fillna('NA')
correspondencias = correspondencies(df)
df = df.replace(correspondencias)

print(df)
df_dict = df.to_dict(orient='records')

"""
for row in df_dict:
    print(row)
"""

def point_dict(df):
    df_dict = df.to_dict(orient='records')
    points = {p: tuple(df_dict[p].values()) for p in range(len(df_dict))}
    return points

p = point_dict(df)
for c in p:
    print(f'{c}: {p[c]}')
