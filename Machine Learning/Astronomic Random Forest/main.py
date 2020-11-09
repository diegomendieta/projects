from main_functions import *
from auxiliary_functions import *

"""
Esta tarea consiste en crear un Random Forest para poder predecir el atributo
'Class' a partir de las otras entradas.
"""

n_estimators = 11
max_depth = 7
min_sample_split = 100
max_features = 30
bootstrap = True

entropy_cut = 0.4

if __name__ == '__main__':
    '''
    Generamos los sets de entrenamiento y de testeo.
    '''
    train, test = preprocess('FATS_GAIA.dat', 0)
    train = normalize(train)
    test = normalize(test)

    '''
    Generamos un Random Forest a partir del set de entrenamiento.
    '''
    forest = fit(train, 'Class', n_estimators, max_depth,
                 min_sample_split, max_features, bootstrap)

    '''
    Ejecutamos el algoritmo en nuestro Forest.
    '''
    predict(test, forest)

    '''
    Escogemos un árbol para visualizar.
    '''
    tree = forest.trees[0]
    visualize(tree)
