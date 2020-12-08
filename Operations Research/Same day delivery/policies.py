from tsp import *
from deterministic import *


class Policy:
    def initPlan(self, nodes, edges):
        """
        Retorna un plan de despacho inicial, de tipo {w: {r1, ..., rj}}
        """
        raise NotImplementedError

    def arrivalUpdate(self, plan, t, a, w, i, b, penalties, pending):
        """
        Actualiza el plan de despacho debido a una llegada de solicitud.
        """
        raise NotImplementedError

    def dispatchUpdate(self, plan, t, a, w):
        """
        Actualiza el plan de despacho debido a una decisión de despacho.
        """
        raise NotImplementedError


class Myopic(Policy):
    # Agregar que borre los archivos previamente generados
    previous_models = set()

    def initPlan(self, nodes, edges):
        if len(nodes) > 2:
            t = TSP()
            t.setVars(nodes.union({0}))
            t.setConstrs()
            t.setObjective(edges)
            objVal, _ = t.solve()

            del t

            trip_time = objVal

        elif len(nodes) == 1:
            for i in nodes:
                if i != 0:
                    trip_time = edgeTime(0, i)
                    trip_time += edgeTime(i, 0)

        else:
            trip_time = 0

        for i in nodes:
            trip_time += serviceTimes[i]

        plan = {w: set() for w in W}
        for w in sorted(plan.keys(), reverse=False):
            wt = waveTimes[w]
            if wt - trip_time >= 0:
                plan[w] = set(nodes)
                break

        print(f'Initial plan: {plan}\n')
        return plan

    def arrivalUpdate(self, plan, t, a, w, i, b, penalties, pending):
        folder = 'generated_models'

        W__ = [j for j in W if j <= w]
        param = max(W__)

        d = Deterministic(a, None, penalties)

        # Si el modelo ya existe, lo cargamos
        if param in self.previous_models:
            d.loadModel(f'{folder}/model_wave_{param}')

        # Si no existe, lo generamos
        else:
            d.setVars(W__)
            d.feasibleSpaceConstr(W__)

            d.saveModel(f'{folder}/params_wave_{param}',
                        f'{folder}/model_wave_{param}')
            self.previous_models.add(param)

        # Seteamos la restricción de atender las solicitudes pendientes
        for j in pending:
            h = latestPossibleDispatchWave(0, j)
            lhs = quicksum(d.model.getVarByName(f'y[{j},{k}]')
                           for k in range(h, min(a[j], w) + 1))
            d.model.addConstr(lhs == 1)

        # Seteamos la función objetivo
        obj = penalties[i] * d.model.getVarByName(f'z[{i}]')

        h = latestPossibleDispatchWave(0, i)
        inf = max(b+1, h)

        obj += quicksum(penalties[i] + d.model.getVarByName(f'y[{i},{k}]')
                        for k in range(inf, w+1))

        for k in range(1, w+1):
            obj += quicksum(gamma * edgeTime(u, v) *
                            d.model.getVarByName(f'x[{u},{v},{k}]')
                            for u, v in feasibleDispatchEdges(k))

        d.model.setObjective(obj, sense=GRB.MINIMIZE)
        d.solve()

        plan = {w_: set() for w_ in W__}
        for var in d.model.getVars():
            spl = var.varName.replace('[', ',').replace(']', '').split(',')
            if spl[0] == 'y' and var.X:
                i, w_ = spl[1:]
                plan[int(w_)].add(int(i))

        print(f'arrival update plan: {plan}')
        return plan

    def dispatchUpdate(self, plan, *args):
        return plan


class Apriori(Policy):
    def initPlan(self, nodes, edges):
        d = Deterministic({}, None, penalties)
        d.setVars(W)
        d.feasibleSpaceConstr(W)

        # Seteamos la restricción de atender las solicitudes pendientes
        for i in nodes:
            h = latestPossibleDispatchWave(i, 0)
            lhs = quicksum(d.y[i, w] for w in range(h, W_ + 1))
            d.model.addConstr(lhs == 1)

        # Seteamos la función objetivo
        obj = quicksum(
            penalties[i] * expectedNumberOfRequests(i, 0) * d.z[i] for i in I)

        for i_ in I:
            h = latestPossibleDispatchWave(0, i_)
            obj += penalties[i_] * quicksum(
                (expectedNumberOfRequests(i_, 0) -
                 expectedNumberOfRequests(i_, w)) * d.y[i_, w]
                 for w in range(h, W_ + 1)
            )

        obj += quicksum(
            quicksum(gamma * edgeTime(i, j) * d.x[i, j, w]
                     for i, j in feasibleDispatchEdges(w))
            for w in range(1, W_ + 1)
        )

        d.model.setObjective(obj, sense=GRB.MINIMIZE)
        d.solve()

        # Construimos el plan de despacho
        plan = {w: set() for w in W}
        for (i, w), var_ in d.y.items():
            if var_.X == 1:
                plan[w].add(i)

        return plan

    def arrivalUpdate(self, plan, t, a, w, i, b, penalties, pending):
        return plan

    def dispatchUpdate(self, plan, t, a, w):
        route = set()
        for node in plan[w]:
            if a[node] != float('inf'):
                route.add(node)
        plan[w] = route
        return plan


class RolloutApriori(Apriori):
    # Agregar que borre los archivos previamente generados
    previous_models = set()

    def arrivalUpdate(self, plan, t, a, w, i, b, penalties, pending):
        for wave, dispatch in plan.items():
            if i in dispatch:
                return plan

        folder = 'generated_models'

        W__ = [j for j in W if j <= w]
        param = max(W__)

        d = Deterministic(a, None, penalties)

        # Si el modelo ya existe, lo cargamos
        if param in self.previous_models:
            d.loadModel(f'{folder}/model_wave_{param}')

        # Si no existe, lo generamos
        else:
            d.setVars(W__)
            d.feasibleSpaceConstr(W__)

            d.saveModel(f'{folder}/params_wave_{param}',
                        f'{folder}/model_wave_{param}')
            self.previous_models.add(param)

        # Seteamos la restricción de atender las solicitudes pendientes
        for j in pending:
            h = latestPossibleDispatchWave(j, 0)
            lhs = quicksum(d.model.getVarByName(f'y[{j},{k}]')
                           for k in range(h, min(a[j], w) + 1))
            d.model.addConstr(lhs == 1)

        # Seteamos la función objetivo
        obj = penalties[i] * (d.model.getVarByName(f'z[{i}]') +
                              quicksum(d.model.getVarByName(f'y[{i},{k}]') for k
                                       in range(max(b+1,
                                       latestPossibleDispatchWave(0, i)), w+1)))

        obj += quicksum(
            quicksum(
                gamma * edgeTime(u, v) * d.model.getVarByName(f'x[{u},{v},{k}]')
                for u, v in feasibleDispatchEdges(k)
            ) for k in range(1, w+1)
        )

        obj += quicksum(
            penalties[j] * (expectedNumberOfRequests(j, 0, t) *
            d.model.getVarByName(f'z[{j}]')
            + quicksum(
                (expectedNumberOfRequests(j, 0, t) -
                 expectedNumberOfRequests(j, k, t)) *
                d.model.getVarByName(f'y[{j},{k}]')
                for k in range(latestPossibleDispatchWave(0, j), w+1)
            ))
            for j in I
        )

        # d.model.Params.MIPGap = gap
        d.model.setObjective(obj, sense=GRB.MINIMIZE)
        d.solve()

        plan = {w_: set() for w_ in W__}
        for var in d.model.getVars():
            spl = var.varName.replace('[', ',').replace(']', '').split(',')
            if spl[0] == 'y' and var.X == 1:
                i_, w_ = spl[1:]
                plan[int(w_)].add(int(i_))

        print(f'arrival update plan: {plan}')
        return plan

    def dispatchUpdate(self, plan, t, a, w):
        folder = 'generated_models'

        W__ = [j for j in W if j <= w]
        param = max(W__)

        d = Deterministic(a, None, penalties)

        # Si el modelo ya existe, lo cargamos
        if param in self.previous_models:
            d.loadModel(f'{folder}/model_wave_{param}')

        # Si no existe, lo generamos
        else:
            d.setVars(W__)
            d.feasibleSpaceConstr(W__)

            d.saveModel(f'{folder}/params_wave_{param}',
                        f'{folder}/model_wave_{param}')
            self.previous_models.add(param)

        # Seteamos la restricción de atender las solicitudes pendientes
        # print(a.items())
        for j, earliest_wave in a.items():
            if earliest_wave == float('inf'):
                continue
            h = latestPossibleDispatchWave(j, 0)
            lhs = quicksum(d.model.getVarByName(f'y[{j},{k}]')
                           for k in range(h, min(a[j], w) + 1))
            d.model.addConstr(lhs == 1)

        obj = quicksum(
            quicksum(
                gamma * edgeTime(u, v) * d.model.getVarByName(f'x[{u},{v},{k}]')
                for u, v in feasibleDispatchEdges(k)
            )
            for k in range(1, w+1)
        )

        obj += quicksum(
            penalties[j] * (expectedNumberOfRequests(j, 0, waveTimes[w]) *
                            d.model.getVarByName(f'z[{j}]') +
            quicksum(
                (expectedNumberOfRequests(j, 0, waveTimes[w]) -
                expectedNumberOfRequests(j, k, waveTimes[w])) *
                d.model.getVarByName(f'y[{j},{k}]')
                for k in range(latestPossibleDispatchWave(0, j), w+1)
            )
                            )
            for j in I
        )

        # d.model.Params.MIPGap = gap
        d.model.setObjective(obj, sense=GRB.MINIMIZE)
        d.solve()

        # Construimos el plan de despacho
        plan = {w_: set() for w_ in W__}
        for var in d.model.getVars():
            spl = var.varName.replace('[', ',').replace(']', '').split(',')
            if spl[0] == 'y' and var.X == 1:
                i, w_ = spl[1:]
                plan[int(w_)].add(int(i))

        print(f'dispatch update plan: {plan}')
        return plan
