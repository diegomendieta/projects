'''
Contiene funciones para obtener la matriz de restricciones a partir de un modelo
de gurobi.

Referencia:
https://stackoverflow.com/questions/38647230/get-constraints-in-matrix-format-from-gurobipy
'''

'''
Función que recibe una fila de la matriz de restricciones (row) y un diccionario
de la forma {variable: índice}, y retorna un generador de tuplas de la forma
(coef_i, var_n_i).
'''
def get_expr_coos(row, var_indices):
    for i in range(row.size()):
        '''
        Obtenemos la variable correspondiente a la i-ésima entrada.
        '''
        dvar = row.getVar(i)
        '''
        Yieldeamos una tupla (coef_i, var_index_i).
        '''
        yield row.getCoeff(i), var_indices[dvar]

'''
Función que recibe un modelo de gurobi y retorna un generador de tuplas de la
forma (i, j, coef_ij).
'''
def get_matrix_coo(m):
    dvars = m.getVars()
    constrs = m.getConstrs()
    var_indices = {v: i for i, v in enumerate(dvars)}
    for row_idx, constr in enumerate(constrs):
        '''
        Recorremos cada una de las filas de la matriz de restricciones.
        '''
        for coeff, col_idx in get_expr_coos(m.getRow(constr), var_indices):
            '''
            Retornamos la tupla (i, j, coef_ij)
            '''
            yield row_idx, col_idx, coeff
