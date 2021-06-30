from functions import *
from tsp import *


class System:
    def __init__(self, nodes, edges, penalties, policy):

        # Nodos
        self.nodes = nodes

        # Arcos
        self.edges = edges

        # Penalizaciones por no atender una solicitud hacia i.
        self.penalties = penalties

        # Seteamos la política a implementar.
        self.policy = policy

        # Tiempo
        self.t = None

        # Vector de compromisos indexado por i. Indica cuál es la ola más
        # próxima en el tiempo en que se puede atender las solicitudes hacia i.
        self.a = None

        # Próxima ola en que el vehículo está en el centro de distribución.
        self.w = None

    def pendingServices(self):
        '''
        Retorna los nodos con solicitudes pendientes.
        '''
        return set([i for i, t in self.a.items() if t != float('inf')])

    def returnWave(self, t, wave):
        '''
        Retorna la ola más próxima en que el vehículo está de vuelta.
        '''
        actual = waveTimes[wave]
        return_time = actual - t
        new_wave = -1
        for w in sorted(waveTimes.keys(), reverse=False):
            wt = waveTimes[w]
            if wt > return_time:
                return new_wave
            new_wave = w
        raise Exception('Tiempo de retorno infactible.')

    def initPlan(self, prev_commitments):
        '''
        Inicializa el plan de despacho.
        '''
        pending = {i for i, l in prev_commitments.items() if l != float('inf')}
        print(f'Pending: {pending}')
        plan = self.policy.initPlan(pending, self.edges)
        self.dispatchPlan = plan

    def acceptRequest(self, i, b):
        '''
        Actualiza el vector de compromisos por la aceptación de una solicitud.
        '''
        min_ = min(self.a[i], b)
        self.a[i] = min_
        self.accepted_requests += 1

    def rejectRequest(self, i):
        '''
        Rechaza una solicitud y paga la penalización por hacerlo.
        '''
        self.cost += self.penalties[i]
        self.penalty_cost += self.penalties[i]
        self.rejected_requests += 1

    def arrivalUpdate(self, i, b):
        '''
        Actualiza el plan de despacho debido a la llegada de una solicitud.
        '''
        pending = self.pendingServices()
        print(f'pending: {pending}')

        update = self.policy.arrivalUpdate(self.dispatchPlan,
                                           self.t, self.a, self.w, i, b,
                                           self.penalties, pending)
        self.dispatchPlan = update

    def waitUntilNextWave(self, wave):
        '''
        Ante una decisión de despacho, espera hasta la siguiente ola.
        '''
        del self.dispatchPlan[wave]
        if wave == self.w:
            self.w -= 1
        for i, w in self.a.items():
            if w == wave:
                self.a[i] -= 1

    def dispatchUpdate(self):
        '''
        Actualiza el plan de despacho debido a una decisión de despacho.
        '''
        update = self.policy.dispatchUpdate(self.dispatchPlan,
                                            self.t, self.a, self.w)
        self.dispatchPlan = update

    def planCoversNode(self, i, b):
        """
        Retorna True si el plan de despacho contempla visitar el nodo i después
        de la ola b, False en caso contrario.
        """
        for w in sorted(self.dispatchPlan.keys(), reverse=False):
            if w > b:
                break
            if i in self.dispatchPlan[w]:
                # print(f'Contemplado visitar en {w}')
                return True
        return False

    def dispatchAtWave(self, wave):
        """
        Retorna True si el plan tiene contemplado despachar en la ola actual,
        False en caso contrario.
        """
        if wave not in self.dispatchPlan:
            return False
        return len(self.dispatchPlan[wave]) != 0

    def execDispatch(self, wave):
        """
        Ejecuta un despacho.
        """
        nodes_to_visit = self.dispatchPlan[wave]
        print(f'Nodos en la ruta: {nodes_to_visit}')

        self.dispatch_quantities.append(len(nodes_to_visit))

        if len(nodes_to_visit) == 1:
            visit = nodes_to_visit.pop()
            distance = 2 * self.edges[0, visit]
            time = distance + serviceTimes[0] + serviceTimes[visit]
            self.a[visit] = float('inf')

        else:
            nodes_to_visit.add(0)

            t = TSP()
            t.setVars(nodes_to_visit)
            t.setConstrs()
            t.setObjective(self.edges)

            distance, _ = t.solve()
            time = distance + sum(serviceTimes[i] for i in nodes_to_visit)

        self.travel_time += time

        print(f'Costo de ruteo: {distance:.2f}')
        print(f'Tiempo de ruta: {time:.2f}')
        self.cost += gamma * distance
        self.routing_cost += gamma * distance

        ret_wave = self.returnWave(time, wave)
        print(f'Comenzando ruta de despacho. '
              f'Vehículo vuelve en w = {ret_wave}.')
        self.w = ret_wave

        for i in self.a.keys():
            if i in nodes_to_visit:
                self.a[i] = float('inf')
            elif self.a[i] == wave:
                self.a[i] -= 1
        del self.dispatchPlan[wave]

    def resetStats(self):
        self.cost = 0
        self.penalty_cost = 0
        self.routing_cost = 0
        self.accepted_requests = sum([1 for com, wave in self.a.items() if wave != float('inf')])
        self.rejected_requests = 0
        self.travel_time = 0
        self.dispatch_quantities = []

    def initState(self, t, a, w):
        self.t = t
        self.a = a
        self.w = w

    def simulate(self, t, a, w, instance):
        print()

        self.initState(t, a, w)
        self.resetStats()
        self.initPlan(a)

        while instance:
            event = instance.pop()
            self.t = event.time

            if self.t == 0:
                break

            print(event)
            print(f'(t, w) = ({self.t:.2f}, {self.w})')
            print(f'a = {self.a}')
            print(self.dispatchPlan)
            print()

            # Si es un evento Llegada
            if isinstance(event, Arrival):
                i = event.node

                if self.w == 0:
                    self.rejectRequest(i)
                    print(f'Solicitud hacia {i} rechazada')
                    continue

                b = releaseWave(event.time)
                print(f'Solicitud hacia {i} liberada en w={b}.')
                self.arrivalUpdate(i, b)

                if self.planCoversNode(i, b):
                    self.acceptRequest(i, b)
                    print(f'Solicitud hacia {i} aceptada')
                else:
                    self.rejectRequest(i)
                    print(f'Solicitud hacia {i} rechazada')

            # Si es un evento DecisiónDespacho
            else:  # if isinstance(event, DispatchDecision)
                wave = event.wave
                if self.w != wave:
                    print(f'DISPATCH DECISION: False (not in Depot)\n')
                    if wave in self.dispatchPlan:
                        del self.dispatchPlan[wave]
                    continue

                self.dispatchUpdate()

                dispatch = self.dispatchAtWave(wave)
                print(f'DISPATCH DECISION: {dispatch}')

                if dispatch:
                    self.execDispatch(wave)
                else:
                    self.waitUntilNextWave(wave)

            print()

    def showStats(self):
        print(f'Total cost: {self.cost:.2f}')
        print(f'Routing cost: {self.routing_cost:.2f}')
        print(f'Penalty cost: {self.penalty_cost:.2f}')
        print(f'Requests accepted: {self.accepted_requests}')
        print(f'Requests rejected: {self.rejected_requests}')
        print(f'Fill rate: {self.accepted_requests / (self.accepted_requests + self.rejected_requests):.2f}')
        print(f'Total travel time: {self.travel_time:.2f}')
        print(f'Travel time / accepted requests: {self.travel_time / self.accepted_requests:.2f}')
        print(f'Average quantity of nodes on route: '
              f'{sum(self.dispatch_quantities) / len(self.dispatch_quantities):.2f}')


