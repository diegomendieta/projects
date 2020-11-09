from textwrap import indent

def potencia(s):
    if not s:
        return [[]]
    return potencia(s[1:]) + [[s[0]] + x for x in potencia(s[1:])]


class Nodo:

    def __init__(self, id, padre, raiz, count=1):
        self.id = id
        self.count = count
        self.padre = padre
        self.hijos = {}
        self.find = {}
        self.raiz = raiz


    def agregar_nodo(self, id, raiz):
        if self.id == id:
            self.count += 1
            return False
        else:
            if id not in self.hijos:
                node = Nodo(id, self, raiz)
                self.hijos[id] = node
                if id not in raiz.find:
                    raiz.find[id] = []
                raiz.find[id].append(node)
            else:
                self.hijos[id].count += 1
            return True


    def __repr__(self):
        if self.hijos:
            t = f'id: {self.id}, count: {self.count}.\n'
        else:
            t = f'id: {self.id}, count: {self.count}, nodo hoja.\n'

        texto_hijos = [repr(hijo) for hijo in self.hijos.values()]
        texto_hijos = [indent(x, "  ") for x in texto_hijos]

        return t + "\n".join(texto_hijos)


class Raiz:

    def __init__(self):
        self.id = None
        self.padre = None
        self.hijos = {}
        self.count = 1
        self.raiz = self
        self.find = {}


    def print_nodes(self):
        for id in self.find:
            lista = self.find[id]
            for nodo in lista:
                print(f'{nodo.id}: {nodo.count}, con padre {nodo.padre.id}:{nodo.padre.count}')
            print()


    def agregar_nodo(self, id, raiz):
        if self.id == id:
            self.count += 1
            return False
        else:
            if id not in self.hijos:
                node = Nodo(id, self, raiz)
                self.hijos[id] = node
                if id not in raiz.find:
                    raiz.find[id] = []
                raiz.find[id].append(node)
            else:
                self.hijos[id].count += 1
            return True


    def agregar_secuencia(self, secuencia, raiz):
        indice = 0
        node = self
        while indice < len(secuencia):
            actual = secuencia[indice]
            b = node.agregar_nodo(actual, raiz)
            if b:
                node = node.hijos[actual]
            indice += 1

    '''
    Retorna una lista de todas las secuencias que finalizan con la id que
    buscamos.
    '''
    def columnas(self, id):
        columns = []
        node_list = self.find[id]
        for node in node_list:
            aux = []
            nodo = node
            n = nodo.count
            while nodo.padre.id:
                aux.append(nodo.padre.id)
                nodo = nodo.padre
            if aux:
                tupla = (aux, n)
                columns.append(tupla)
        return columns


    def cpb_dict(self, lista=[]):
        d = {}
        if not lista:
            lista = self.find
        for id in lista:
            d[id] = self.columnas(id)
        return d


    '''
    Entrega un diccionario cuyas keys son los items y sus values son los
    cfp trees con los que se relaciona la key.
    '''
    def cfp_tree(self, dict):
        d = {}
        for id, cpb in dict.items():
            n = 0
            if cpb:
                bool = True
                for items, count in cpb:
                    if bool:
                        item = set(items)
                        bool = False
                        s = item
                    else:
                        x = set(items)
                        s = s.intersection(x)
                    if s:
                        n += count
                tupla = (s, n)
                d[id] = tupla
        return d

    '''
    Recibe un diccionario con los fp trees y retorna un dict de fp.
    '''
    def fp(self, dict):
        d = {}
        for id in dict:
            itemset, count = list(dict[id][0]), dict[id][1]
            p = potencia(itemset)
            for conjunto in p:
                if conjunto:
                    l = [id]
                    l.extend(conjunto)
                    t = tuple(l)
                    d[t] = count
        return d


    def __repr__(self):
        if self.hijos:
            t = f'id: {self.id}, count: {self.count}.\n'
        else:
            t = f'id: {self.id}, count: {self.count}, nodo hoja.\n'

        texto_hijos = [repr(hijo) for hijo in self.hijos.values()]
        texto_hijos = [indent(x, "  ") for x in texto_hijos]

        return t + "\n".join(texto_hijos)


'''
raiz = Raiz()

s1 = ['K', 'E', 'M', 'O', 'Y']
s2 = ['K', 'E', 'O', 'Y']
s3 = ['K', 'E', 'M']
s4 = ['K', 'M', 'Y']
s5 = ['K', 'E', 'O']

raiz.agregar_secuencia(s1, raiz)
raiz.agregar_secuencia(s2, raiz)
raiz.agregar_secuencia(s3, raiz)
raiz.agregar_secuencia(s4, raiz)
raiz.agregar_secuencia(s5, raiz)


cpb_dict = raiz.cpb_dict()
print(cpb_dict)

print()

cfp_tree = raiz.cfp_tree(cpb_dict)
print(cfp_tree)

print()

fp = raiz.fp(cfp_tree)
print(fp)
'''
