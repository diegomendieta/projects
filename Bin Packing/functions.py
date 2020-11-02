from collections import defaultdict
import copy

'''
Filtra todas las cajas que contengan a exactamente uno en (i, j).
'''
def filter_left(s, i, j):
    return {k: cjt for k, cjt in s.items() if not
            ((i in cjt and j not in cjt) or (j in cjt and i not in cjt))}


'''
Filtra todas las cajas que contengan a i y j al mismo tiempo.
'''
def filter_right(s, i, j):
    return {k: cjt for k, cjt in s.items() if not (i in cjt and j in cjt)}


'''
Función auxiliar usada para mostrar los resultados de un modelo.
'''
def show_soldict(z, s0):
    d = defaultdict(list)
    for c, v in z.items():
        if v.X:
            d[v.X].append(s0[c])
    print(f'z: {dict(d)}')


'''
Transforma una lista de variables obtenida por model.getVars() en un 
diccionario {name: Var}.
'''
def dictify_solution(z):
    return {int(var.VarName): var for var in z}


'''
Retorna un (i, j) tal que ambos están contenidos en una caja fraccionaria.
'''
def get_ij(s, solution):
    tentative_sets = []
    for key, val in solution.items():
        if not val.X.is_integer():
            found = s[key]
            tentative_sets.append(found)
            for fs in tentative_sets:
                intrs = fs.intersection(found)
                diff = fs.difference(found)

                if intrs and diff:
                    return next(iter(intrs)), next(iter(diff))

    raise ValueError('No se encontró un par (i, j).')


'''
Retorna un diccionario con las cajas resultantes de haber unido los objetos
i y j, y un diccionario con los pesos resultantes.
'''
def merge_vars(s, v, i, j):
    x = max(v.keys()) + 1

    ns = copy.deepcopy(s)
    for c, box in ns.items():

        if i in box and j in box:
            box.remove(i)
            box.remove(j)
            box.add(x)

    nv = copy.deepcopy(v)
    nv[x] = nv[i] + nv[j]
    del nv[i]
    del nv[j]

    return ns, nv, x


def recovered(recovering_dict):
    m = min(recovering_dict.keys())
    recovered_boxes = {}
    while recovering_dict:
        cont = recovering_dict[m]
        for s in recovering_dict.values():
            if m in s:
                s.update(cont)
                s.remove(m)
        recovered_boxes.update(recovering_dict)
        del recovering_dict[m]
        m += 1

    return recovered_boxes
