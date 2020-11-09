import random


def average(pair_list):
    sum_ = 0
    for val, prob in pair_list:
        sum_ += val * prob
    return sum_


def generate_demands(means, errors, month_change, T):
    demands = {}

    month = 0
    for t in range(1, T + 1):
        mean, error = means[month], errors[month]

        d_list = []
        for d in range(mean - error, mean + error + 1):
            prob = 1 / (2 * error + 1)
            pair = (d, prob)
            d_list.append(pair)

        demands[t] = d_list

        if t == month_change[month]:
            month += 1
    return demands


def print_policy(depot):
    for (t, s), x in depot.policy.items():
        print(f'{t, s}: {x}')


def simulate_demands(demands, M):
    demand_list = []
    for m in range(M):
        t = 1
        x = {}
        for d_list in demands.values():
            acc = 0
            p = random.uniform(0, 1)
            for d, prob in d_list:
                acc += prob
                if p <= acc:
                    x[t] = d
                    t += 1
                    break
        demand_list.append(x)
    return demand_list

################################################################################

'''
compare = False
if naive and reduced_space and compare:
    # Las políticas no son exactamente iguales; en algunos tiempos, diferen por
    # una unidad en el S. Es probablemente por errores de aproximación.
    for key, val in naive_sS.items():
        sS_val = sS[key]
        print(f't = {key}')
        if val != sS_val:
            print('DIFFERENT POLICIES')
        print(f'Naive: {val}')
        print(f'RedSp: {sS_val}')
'''