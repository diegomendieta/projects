from RandomForest import *
from DecisionTree import *

'''
Crea un Random Forest a partir de la base de datos.
'''
def fit(data, target='Class', n_estimators=0, max_depth=0,
        min_sample_split=0, max_features=0, bootstrap=False):

    forest = RandomForest(data, target, n_estimators, max_depth,
                          min_sample_split, max_features, bootstrap)

    return forest

'''
Entrega una predicción a partir de un conjunto de datos y un Random Forest.
'''
def predict(data, random_forest):
    prediction = random_forest.forest_predict_data(data)
    return prediction

'''
Genera una visualización de un Árbol de Decisión.
'''
def visualize(tree):
    tree.visualize()