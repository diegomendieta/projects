from auxiliary_functions import *
import networkx as nx
import matplotlib.pyplot as plt

'''
Clase que define un Árbol de Decisión.
'''
class DecisionTree:

    id = 1

    def __init__(self, df, depth, max_depth=float('inf'), min_sample_split=0,
                 padre=None):
        self.df = df
        self.depth = depth

        self.hoja = False
        self.padre = padre
        self.izq = None
        self.der = None

        self.max_depth = max_depth
        self.min_sample_split = min_sample_split

        self.division_attr = None
        self.division_number = None

        self.identity = DecisionTree.id
        DecisionTree.id += 1

        self.dict_hijos = {}

        self.initialize()


    def initialize(self):

        self.entropy = df_entropy(self.df)

        if (self.depth >= self.max_depth)\
            or (len(self.df) <= self.min_sample_split)\
            or (not self.entropy):
            self.hoja = True
            return

        attr, s = convenient_tuple(self.df)
        df1, df2, mean = divide(self.df, attr)

        self.division_attr = attr
        self.division_number = mean

        self.izq = DecisionTree(df1, self.depth + 1,
                                self.max_depth, self.min_sample_split, self)
        self.der = DecisionTree(df2, self.depth + 1,
                                self.max_depth, self.min_sample_split, self)

    '''
    def visualize(self):
        s = df_entropy(self.df)
        print(f'Nodo a profundidad {self.depth}, con entropía {s:.5f}.')
        #print(self.df)
        #print()
        print('-' * 80)
        if not self.hoja:
            self.izq.visualize()
            self.der.visualize()
    '''

    '''
    Crea un diccionario en que se tienen todas las conexiones del árbol.
    '''
    def create_dict(self, raiz):
        if not self.hoja:
            raiz.dict_hijos[self.identity] = []

            label_izq = f'{self.division_attr} <= {self.division_number:.2f}'
            tupla_izq = (self.izq.identity, label_izq)
            raiz.dict_hijos[self.identity].append(tupla_izq)

            label_der = f'{self.division_attr} > {self.division_number:.2f}'
            tupla_der = (self.der.identity, label_der)
            raiz.dict_hijos[self.identity].append(tupla_der)

            self.izq.create_dict(raiz)
            self.der.create_dict(raiz)


    def visualize(self):

        if not self.dict_hijos:
            self.create_dict(self)

        G = nx.Graph()
        labels = {}
        for padre in self.dict_hijos:
            for hijo, label in self.dict_hijos[padre]:
                G.add_edge(padre, hijo)
                tupla = (padre, hijo)
                labels[tupla] = label

        pos = hierarchy_pos(G, 1)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
        nx.draw(G, pos=pos, with_labels=True)
        plt.show()

    def predict_row(self, df_row, attr='Class'):
        if self.hoja:
            return most_repeated(self.df, attr)
        val = df_row[self.division_attr]
        if val <= self.division_number:
            return self.izq.predict_row(df_row, attr)
        else:
            return self.der.predict_row(df_row, attr)


    def predict_data(self, df):
        aciertos, total = 0, 0
        for index, row in df.iterrows():
            if row['Class'] == self.predict_row(row):
                aciertos += 1
            total += 1

        accuracy = aciertos/total
        print(f'La efectividad es de un {(accuracy*100):.2f}%.')
        return accuracy


################################################################################


if __name__ == '__main__':


    train, test = preprocess('FATS_GAIA.dat')

    train = normalize(train.sample(n=800, random_state=0))
    test = normalize(test.sample(n=200, random_state=0))

    """
    train = normalize(train)
    test = normalize(test)
    """

    #print(f'train: {len(train)}, test: {len(test)}\n')

    params = (3, 10)
    inicio = time.time()
    tree = DecisionTree(train, 0, *params)
    final = time.time() - inicio
    print(f'El árbol demoró {final:.2f} segundos en armarse.\n')

    '''
    inicio = time.time()
    tree.predict_data(test)
    final = time.time() - inicio
    print(f'El algoritmo demoró {final:.2f} segundos en realizarse.\n')
    #tree.visualize()
    '''

    tree.visualize()

################################################################################