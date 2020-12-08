import numpy as np

"""
IMPORTANTE: borrar archivos de generated_models cada vez que se cambien los
parámetros.
"""

# Semilla aleatoria
seed = 2022

# Horizonte de tiempo
T_ = 840

# Cantidad de olas en un día (sin contar la final). (W_ + 1) debe ser divisor de
# T_.
W_ = 6

# Cantidad de nodos en la red. Si se elige la distribución normal, debe ser
# múltiplo de 4.
I_ = 10

# Tiempo en que dejan de llegar pedidos
cutoffTime = (2/7) * T_

# Tiempo de procesamiento en centro de distribución
p = 19

# Función de distribución de las tasas de llegada
arrivalDistribution = np.random.uniform

# Manipulador de arrival rates
arrRatePonderator = 1 * (50/I_)

# Cota inferior de las tasas de llegada de solicitudes
lbdLow = (1/T_) * arrRatePonderator

# Cota superior de las tasas de llegada de solicitudes
lbdHigh = (1/T_) * arrRatePonderator

# Función de distribución de las penalizaciones
penaltyDistribution = np.random.uniform

# Cota inferior de penalizaciones por rechazar una solicitud
penaltyLow = None

# Cota superior de penalizaciones por rechazar una solicitud
penaltyHigh = None

# Función de distribución de tiempos de servicio en cada nodo
serviceTimeDistribution = np.random.uniform

# Cota inferior de tiempos de servicio
serviceTimeLow = 6

# Cota superior de tiempos de servicio
serviceTimeHigh = 6

# Tiempo de servicio en el centro de distribución
depotServiceTime = 19

# Ponderador de costo por tiempo/distancia (los últimos son considerados
# equivalentes)
gamma = 1

# Ponderador de distancia. Para manipular la proporción de la distancia entre
# nodos.
alpha = 3

# Desviación estándar para la distribución geográfica de los nodos.
stdev = 0.25

# Gap de optimalidad para política Rollout Apriori
gap = 0.005


def varDict():
    """
    Retorna un diccionario con todas las variables.
    """
    params = {
        'W_': W_,
        'I_': T_,
        'cutoffTime': cutoffTime,
        'p': p,
        'arrivalDistribution': arrivalDistribution.__name__,
        'lbdLow': lbdLow,
        'lbdHigh': lbdHigh,
        'penaltyDistribution': penaltyDistribution.__name__,
        'penaltyLow': penaltyLow,
        'penaltyHigh': penaltyHigh,
        'serviceTimeDistribution': serviceTimeDistribution.__name__,
        'serviceTimeLow': serviceTimeLow,
        'serviceTimeHigh': serviceTimeHigh,
        'depotServiceTime': depotServiceTime,
        'gamma': gamma,
        'alpha': alpha
    }
    return params
