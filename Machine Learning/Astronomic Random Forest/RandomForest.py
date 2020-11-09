from DecisionTree import*
import numpy as np

'''
Clase que define un Random Forest
'''
class RandomForest:
    def __init__(self, train, target, n_estimators, max_depth,
                 min_sample_split, max_features, bootstrap):
        self.trees = []
        self.target = target
        self.train = train
        self.initialize(n_estimators, max_depth, min_sample_split,
                        max_features, bootstrap)


    def initialize(self, n_estimators, max_depth,
                   min_sample_split, max_features, bootstrap):

        for iteracion in range(n_estimators):

            inicio = time.time()

            if bootstrap:
                size = np.random.randint(round(len(self.train)/4),
                                         3*round(len(self.train)/4))
            else:
                size = len(self.train)

            k = np.random.randint(max_features/2, max_features+1)
            attrs = set(np.random.choice(self.train.columns, k, replace=False))
            attrs.add(self.target)
            df = self.train.sample(n=size)

            for col in df.columns:
                if col not in attrs:
                    del df[col]

            tree = DecisionTree(df, 0, max_depth, min_sample_split)
            self.trees.append(tree)

            final = time.time() - inicio
            print(f'Árbol {iteracion+1} creado en {final:.2f} segundos.')


    def forest_predict_row(self, df_row, attr='Class'):
        predictions = {}
        for tree in self.trees:
            result = tree.predict_row(df_row)
            if result not in predictions:
                predictions[result] = 1
            else:
                predictions[result] += 1
        #print(predictions)
        return most_repeated(self.train, attr)


    def forest_predict_data(self, df):
        aciertos, total = 0, 0
        for index, row in df.iterrows():
            if row['Class'] == self.forest_predict_row(row):
                aciertos += 1
            total += 1

        accuracy = aciertos / total
        print(f'La efectividad es de un {(accuracy*100):.2f}%.')
        return accuracy


if __name__ == '__main__':

    train, test = preprocess('FATS_GAIA.dat')

    train = normalize(train.sample(n=160000, random_state=0))
    test = normalize(test.sample(n=10000, random_state=0))

    """
    train = normalize(train)
    test = normalize(test)
    """

    n_estimators = 13
    max_depth = 7
    min_sample_split = round(len(train)/(2**(max_depth+3)))
    max_features = 25
    bootstrap = True
    params = (n_estimators, max_depth, min_sample_split, max_features, bootstrap)

    inicio = time.time()
    forest = RandomForest(train, *params)
    final = time.time() - inicio
    print(f'El Forest demoró {final:.2f} segundos en armarse.\n')

    inicio = time.time()
    forest.forest_predict_data(test)
    final = time.time() - inicio
    print(f'El algoritmo demoró {(final):.2f} segundos en realizarse.\n')