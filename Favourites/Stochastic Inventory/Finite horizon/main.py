from depot import *
from policies import *
from functions import generate_demands, simulate_demands
from time import time
import numpy as np
import scipy.stats

################################################################################

# ¿Es S de (s, S) único?

Q = 200
T = 52
K = 1600
c = 20
h = 4
q = 75

y = 30

M = 30
confidence = 0.975

means = [15, 16, 25, 18, 29, 20, 20, 19, 18, 17, 25, 40]
errors = [4, 6, 7, 5, 4, 10, 10, 4, 2, 1, 10, 15]
month_change = [4, 8, 13, 17, 22, 26, 30, 35, 39, 44, 48, 52]

demands = generate_demands(means, errors, month_change, T)
lead_time = 0

################################################################################

depot = Depot(Q, T, K, c, h, q, demands, lead_time)

'''
Se resuelve la formulación naive del DP.
'''
naive = True
if naive:
    t1 = time()
    naive_cost = depot.naively_optimize(y)
    naive_sS = depot.get_sS_policy()
    t2 = time()

    print('Naive optimization')
    print(f'Solved in {t2-t1:.2f} seconds.')
    print(f'Cost: {naive_cost:.2f}.\n')

    show_whole_policy = False
    if show_whole_policy:
        print(f'Policy: {depot.policy}\n')

    print_latex_policy = False
    if print_latex_policy:
        for t, (s, S) in naive_sS.items():
            print(f'\item t = {t}: {s, S}')

'''d
Se resuelve el DP buscando en un espacio de políticas (s, S). El costo difiere
en un porcentaje mínimo debido a problemas de aproximación al calcular las
esperanzas de los costos.
'''
reduced_space = True
if reduced_space:
    t3 = time()
    cost = depot.reduced_space_optimize(y)
    sS = depot.sS_policy
    t4 = time()

    print('Reduced space optimization')
    print(f'Policy determined in {t4-t3:.2f} seconds.')
    print(f'Cost: {cost:.2f}.\n')
    print(f'Policy: {sS}\n')

    print('-'*80)
    print()

'''
Evalúa la política (s, S) encontrada en el apartado anterior. Se observa que
los costos de las dos resoluciones anteriores coinciden.
'''
sS_pol = True
if sS_pol:
    t17 = time()
    policy = SSPolicy(depot, sS)
    t18 = time()

    depot.policy_class = policy
    t19 = time()
    sS_cost = depot.evaluate_policy(y)
    t20 = time()

    print('(s, S) policy')
    print(f'Created policy in {t18 - t17:.2f} seconds.')
    print(f'Evaluated policy in {t20 - t19:.2f} seconds.')
    print(f'Cost: {sS_cost:.2f}.\n')

'''
Evalúa la política conservadora.
'''
conservative = True
if conservative:
    t5 = time()
    policy = ConservativePolicy(depot)
    t6 = time()

    depot.policy_class = policy
    t7 = time()
    conservative_cost = depot.evaluate_policy(y)
    t8 = time()

    print('Conservative policy')
    print(f'Created policy in {t6 - t5:.2f} seconds.')
    print(f'Evaluated policy in {t8 - t7:.2f} seconds.')
    print(f'Cost: {conservative_cost:.2f}.\n')

'''
Evalúa la política newsvendor.
'''
newsvendor = True
if newsvendor:
    t9 = time()
    policy = NewsvendorPolicy(depot)
    t10 = time()

    depot.policy_class = policy
    t11 = time()
    newsvendor_cost = depot.evaluate_policy(y)
    t12 = time()

    print('Newsvendor policy')
    print(f'Created policy in {t10 - t9:.2f} seconds.')
    print(f'Evaluated policy in {t12 - t11:.2f} seconds.')
    print(f'Cost: {newsvendor_cost:.2f}.\n')

'''
Evalúa la política del futuro promedio.
'''
avg_future = True
if avg_future:
    t13 = time()
    policy = AvgFuturePolicy(depot)
    t14 = time()

    depot.policy_class = policy
    t15 = time()
    avg_future_cost = depot.evaluate_policy(y)
    t16 = time()

    print('Average future policy')
    print(f'Created policy in {t14 - t13:.2f} seconds.')
    print(f'Evaluated policy in {t16 - t15:.2f} seconds.')
    print(f'Cost: {avg_future_cost:.2f}.\n')

'''
Lleva a cabo la simulación y calcula un intervalo de confianza para la 
diferencia entre el caso con información pefecta y el DP.
'''
simulation = True
if simulation:
    demand_list = simulate_demands(demands, M)
    policy = SSPolicy(depot, sS)
    depot.policy_class = policy

    t = scipy.stats.t.ppf(confidence, M - 1)

    t1 = time()

    diff_list = []
    cost_list = []
    pi_list = []
    for dem in demand_list:
        cost = depot.simulate(y, dem)
        pi = depot.perfect_information(y, dem)

        cost_list.append(cost)
        pi_list.append(pi)

        diff = cost - pi
        diff_list.append(diff)

    t2 = time()
    print(f'Simulated in {t2 - t1:.2f} seconds.')

    cost_arr = np.array(cost_list)
    mean_cost = np.mean(cost_arr)
    print(f'Mean (s, S): {mean_cost:.2f}')

    pi_arr = np.array(pi_list)
    mean_pi = np.mean(pi_arr)
    print(f'Mean PI: {mean_pi:.2f}')

    arr = np.array(diff_list)
    mean = np.mean(arr)
    std = np.std(arr)
    print(f'Mean diffs: {mean:.2f} \nStd diffs: {std:.2f}')

    conf_low = mean - t * std
    conf_high = mean + t * std
    print(f'Confidence interval: [{conf_low:.2f}, {conf_high:.2f}]')

'''
Modela el problema considerando un lead time estocástico.
'''
lead_time_problem = True
if lead_time_problem:
    t3 = time()
    cost = depot.lead_time_optimize(y)
    t4 = time()

    print(f'Policy determined in {t4 - t3:.2f} seconds.')
    print(f'Cost: {cost:.2f}.\n')
    for state, plc in depot.policy.items():
        if plc:
            print(f'{state}: {plc}')
