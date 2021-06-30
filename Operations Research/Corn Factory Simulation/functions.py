import numpy as np
from random import shuffle, sample
from parameters import *



################################################################################
'''
Funciones auxiliares.
'''

def distribucion_llegadas():
    return np.random.exponential(1/tasa_llegada)

def cantidad_hibridos():
    return np.random.randint(tipos_hibrido_minimo, tipos_hibrido_maximo + 1)


def asignacion_hibridos_gmo(ctd_llegadas, ctd_hibridos):
    tipos = sample([c for c in range(1, cantidad_total_tipos_hibrido+1)],
                   ctd_hibridos)
    tipos.extend([tipos[c] for c in np.random.randint(len(tipos),
                                                      size=ctd_llegadas -
                                                           ctd_hibridos)])
    shuffle(tipos)
    gmo = np.random.choice([True, False], ctd_llegadas,
                           p=[probabilidad_gmo, 1 - probabilidad_gmo])
    return list(zip(tipos, gmo))


def tiempos_llegadas(cantidad_tipos_hibrido):
    while True:
        tiempo = 0
        tiempos_entre_llegadas = []
        while True:
            tiempo_hasta_nueva_llegada = distribucion_llegadas()
            tiempo += tiempo_hasta_nueva_llegada
            if tiempo > duracion_turno:
                break
            tiempos_entre_llegadas.append(tiempo_hasta_nueva_llegada)
        if len(tiempos_entre_llegadas) >= cantidad_tipos_hibrido:
            break
    return tiempos_entre_llegadas


################################################################################
'''
Funciones que efectivamente se ocupan.
'''

'''
Retorna una lista de tuplas de formato (hibrido, gmo, tiempo_llegada)
'''
def llegadas():
    ctd = cantidad_hibridos()
    tiempos_llegada = tiempos_llegadas(ctd)
    asignaciones = asignacion_hibridos_gmo(len(tiempos_llegada), ctd)
    return [{'tipo': u, 'gmo': v, 'tiempo_entre_llegadas': w} for (u, v), w
            in zip(asignaciones, tiempos_llegada)]

'''
Función que asigna la humedad inicial a un lote.
'''
def humedad_lote():
    return np.random.randint(humedad_inicial_minima * 100,
                             (humedad_inicial_maxima * 100) + 1) / 100

'''
Función que asigna un peso en toneladas a un lote.
'''
def carga_camion():
    return np.random.uniform(carga_minima, carga_maxima)

'''
Función que retorna el tiempo de limpieza por tipo de híbrido en una linea de
descarga.
'''
def limpieza_hibrido_descarga():
    return np.random.triangular(tiempo_limpieza_descarga_low,
                                tiempo_limpieza_descarga_mid,
                                tiempo_limpieza_descarga_high)

def limpieza_hibrido_desgrane():
    return np.random.uniform(tiempo_limpieza_desgrane_low,
                             tiempo_limpieza_desgrane_high)


################################################################################

if __name__ == '__main__':
    np.random.seed(0)
    l = llegadas()
    suma = 0
    for c in l:
        suma += c['tiempo_entre_llegadas']
        print(suma)
