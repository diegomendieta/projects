from collections import deque

'''
Basado en
https://www.techiedelight.com/0-1-knapsack-problem/

Modela el problema de la mochila.
'''
def knapsack(B, w, pi, mapping, forbidden=None):

    val_dict = {(b, i): [0, 0] for b in range(B + 1) for i in mapping.values()}

    for i in range(len(w)):
        for b in range(1, B + 1):

            if w[mapping[i]] > b or mapping[i] == forbidden:
                val_dict[b, mapping[i]] = val_dict[b, mapping[i-1]][0], 0

            else:
                x = val_dict[b, mapping[i-1]][0]
                y = pi[i] + val_dict[b-w[mapping[i]], mapping[i-1]][0]

                if x >= y:
                    val_dict[b, mapping[i]] = [x, 0]

                else:
                    val_dict[b, mapping[i]] = [y, 1]

    return val_dict


'''
Recupera la solución del problema de la mochila correspondiente a la branch
izquierda.
'''
def retrieve_sol(val_dict, B, w, i, mapping, sol=None):
    if sol is None:
        sol = deque()

    if i == -1:
        return sol

    choice = val_dict[B, mapping[i]][1]

    if choice:
        sol.appendleft(1)
        return retrieve_sol(val_dict, B-w[mapping[i]],
                                 w, i-1, mapping, sol)

    sol.appendleft(0)
    return retrieve_sol(val_dict, B, w, i-1, mapping, sol)
