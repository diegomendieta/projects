from collections import deque, defaultdict
from functions import *
from parameters import *
from sortedcontainers import SortedList

'''
Clase que representa un evento que ocurre en la simulación.
'''
class Evento:
    def __init__(self, tiempo, lote, tipo, descarga=None, sorting=None,
                 secador=None, modulo=None, desgrane=None, secado=None,
                 tiempo_limpieza=None, lote_perdido=None, indice=None):

        self.tiempo = tiempo
        self.lote = lote
        self.tipo = tipo

        self.descarga = descarga
        self.sorting = sorting
        self.modulo = modulo
        self.secador = secador
        self.desgrane = desgrane
        self.secado = secado
        self.tiempo_limpieza = tiempo_limpieza
        self.lote_perdido = lote_perdido
        self.indice = indice

'''
Entidad que representa un lote de maíz.
'''
class Lote:

    id_counter = 0

    def __init__(self, tipo, gmo, tiempo_llegada):
        self.tipo = tipo
        self.gmo = gmo
        self.__humedad = humedad_lote()
        self.carga = carga_camion()
        self.tiempo_llegada = tiempo_llegada
        self.id = self.generate_id()

    def __repr__(self):
        return f'(ID: {self.id}; Tipo: {self.tipo}; GMO: {self.gmo}; ' \
               f'Tiempo llegada: ' \
               f'{self.tiempo_llegada}; Carga: {self.carga})'

    def generate_id(self):
        Lote.id_counter += 1
        return self.id_counter

    @property
    def humedad(self):
        return self.__humedad

    @humedad.setter
    def humedad(self, valor):
        if valor < 0:
            self.__humedad = 0
        else:
            self.__humedad = valor


'''
Clase que representa una mezcla de lotes, luego de haber pasado por el proceso 
de Secado.
'''
class LoteMezclado(Lote):

    id_counter = 0

    def __init__(self, tipo, gmo, tiempo_llegada):
        super().__init__(tipo, gmo, tiempo_llegada)
        self.componentes = []
        self.cantidad = 0
        self.carga = 0

    def generate_id(self):
        LoteMezclado.id_counter += 1
        return self.id_counter

    def agregar_lote(self, lote):
        self.componentes.append(lote)
        self.carga += lote.carga

    @property
    def humedad(self):
        return sum([lote.humedad * lote.carga for lote in self.componentes]) \
               / self.carga


'''
Clase que representa una linea.
'''
class Linea:
    def __init__(self):
        self.tipo_hibrido = None
        self.lote_actual = None
        self.velocidad = 0  # asignar después; depende si es Descarga o Sorting.

    '''
    Retorna True si la linea está ocupada, False en caso contrario.
    '''
    def ocupada(self):
        if self.lote_actual is not None:
            return True
        return False

    '''
    Retorna el tiempo (en horas) que se demorará el lote en pasar por la línea.
    '''
    def tiempo_en_pasar(self):
        if not self.ocupada():
            raise AttributeError('Se le está pidiendo un tiempo de pasada a una'
                                 ' línea desocupada')
        else:
            return self.lote_actual.carga / self.velocidad

    '''
    Desocupa la línea.
    '''
    def desocupar(self):
        self.lote_actual = None


'''
Clase que representa una línea de descarga.
SUPUESTO: no existe limpieza en relación a GMO.
'''
class LineaDescarga(Linea):
    def __init__(self, gmo):
        super().__init__()
        # self.gmo = gmo
        self.velocidad = velocidad_descarga
        # self.tiempo_final_descarga = float('inf')

    '''
    Retorna el tiempo de limpieza correspondiente a cambio de híbrido.
    '''
    def tiempo_limpieza_por_hibrido(self):
        return limpieza_hibrido_descarga()


'''
Clase que representa una línea de desgrane.
'''
class LineaDesgrane(Linea):
    def __init__(self, gmo):
        super().__init__()
        self.gmo = gmo
        self.velocidad = velocidad_desgrane

    def tiempo_limpieza_por_hibrido(self):
        return limpieza_hibrido_desgrane()


'''
Clase que representa una línea de sorting.
SUPUESTO: las líneas de sorting son indiferentes a GMO/No-GMO. Es decir, todas
sierven para ambos tipos.
'''
class LineaSorting(Linea):
    def __init__(self, automatica):
        super().__init__()
        self.velocidad = velocidad_sorting_automatico if automatica \
                         else velocidad_sorting_manual
        # self.tiempo_final_sorting = float('inf')


'''
Módulo que representa la llegada de camiones.
'''
class Llegada:
    def __init__(self):
        self.entidad_siguiente = None  # próxima entidad que llegará
        self.tiempo_hasta_proxima_llegada = float('inf')

    '''
    Genera una entidad Lote.
    '''
    def generar_camion(self, tipo, gmo, tiempo_llegada):
        return Lote(tipo, gmo, tiempo_llegada)

    '''
    Genera un evento de tipo "llegada_camion".
    '''
    def generar_evento_llegada(self, lote):
        return Evento(lote.tiempo_llegada, lote, 'llegada_camion')

    '''
    Asigna un deque de dicts de formato [{tipo, gmo, tiempo_entre_llegadas}] al
    atributo llegadas. Debe ser ejecutado cada día de la simulación.
    '''
    def generar_llegadas(self):
        self.llegadas = deque(llegadas())
        self.entidad_siguiente = self.proxima_entidad()

    '''
    Método que retorna la entidad que llegará próximamente. Si no corresponde
    que lleguen más camiones en el día, retorna None.
    '''
    def proxima_entidad(self):
        if self.llegadas:
            x = self.llegadas.popleft()
            self.tiempo_hasta_proxima_llegada = x['tiempo_entre_llegadas']
            return x
        else:
            self.tiempo_hasta_proxima_llegada = float('inf')
            return None

    '''
    Representa la llegada de un camión a la planta. Crea la entidad camión y
    retorna un evento de tipo "llegada_camion".
    '''
    def entregar_lote(self, tiempo_actual):
        entidad_siguiente = self.entidad_siguiente
        attrs = False
        if entidad_siguiente is not None:
            attrs = list(self.entidad_siguiente.values())
        if not attrs:
            return None
        lote = self.generar_camion(*attrs)
        lote.tiempo_llegada += tiempo_actual
        self.entidad_siguiente = self.proxima_entidad()
        return self.generar_evento_llegada(lote)


'''
Módulo que representa el proceso de descarga.
'''
class Descarga:
    def __init__(self):
        self.cola = deque()
        self.lineas = self.generar_lineas_descarga()  # diccionario {n: linea_n}

        self.lineas_ocupadas = 0

    '''
    Genera 2 líneas de descarga destinadas a GMO, y 2 destinadas a No-GMO. Crea
    un diccionario para poder acceder a ellas.
    '''
    def generar_lineas_descarga(self):
        linea_1, linea_2 = LineaDescarga(True), LineaDescarga(True)
        linea_3, linea_4 = LineaDescarga(False), LineaDescarga(False)
        return {1: linea_1, 2: linea_2, 3: linea_3, 4: linea_4}

    '''
    Recibe a un camión y lo agrega a la cola para las líneas de descarga.
    '''
    def recibir_lote(self, lote):
        self.cola.append(lote)

    '''
    Retorna una lista con los números de las líneas desocupadas.
    '''
    def lineas_desocupadas(self):
        return [u for u, v in self.lineas.items() if not v.ocupada()]

    '''
    Retorna un diccionario cuyas keys son los tipos de híbrido pasando por las
    líneas, y sus values son los números de las líneas correspondientes.
    '''
    def hibridos_pasando(self):
        return {linea.tipo_hibrido: n for n, linea in self.lineas.items()
                if linea.tipo_hibrido is not None}

    '''
    Retorna (Lote(), num_línea) correspondiente al lote que debe pasar más
    próximamente. Si num_línea es None, no va dirigido específicamente. Si no lo
    es, debe ir a la línea correspondiente.
    
    No considera GMO/No-GMO.
    '''
    def asignar_lote_siguiente(self, clock):
        if not len(self.cola):
            raise ValueError('Intentando asignar un lote inexistente')

        if elegir_por_tiempo:
            if clock - self.cola[0].tiempo_llegada >=\
                    tolerancia_espera_cola * porcentaje_espera:
                return self.cola.popleft(), None

        indice = 0
        hibridos_pasando = self.hibridos_pasando()
        for lote in self.cola:
            if lote.tipo in hibridos_pasando:
                linea_correspondiente = hibridos_pasando[lote.tipo]
                if linea_correspondiente not in self.lineas_desocupadas():
                    continue
                self.cola = list(self.cola)
                x = self.cola.pop(indice)
                self.cola = deque(self.cola)
                return x, linea_correspondiente
            indice += 1

        return self.cola.popleft(), None

    '''
    Retorna el número de la primera línea que está desocupada.
    '''
    def asignar_linea_arbitraria(self):
        for n, linea in self.lineas.items():
            if not linea.ocupada():
                return n
        return None
        #raise ValueError('Todas las líneas están ocupadas.')

    '''
    Genera un evento de comienzo de descarga.
    '''
    def generar_evento_comienzo_descarga(self, clock, lote=None):
        return Evento(clock, lote, 'comienza_descarga',)

    def desechar_lote_esperando(self, id_lote):
        self.cola = list(self.cola)
        contador = 0
        for lote in self.cola:
            if lote.id == id_lote:
                break
            contador += 1
        desecho = self.cola.pop(contador)
        if desecho.id != id_lote:
            raise ValueError('Popeando lote de id incorrecto.')
        self.cola = deque(self.cola)

    '''
    Comienza la descarga de un camión. Retorna un Evento('termina_descarga').
    '''
    def comenzar_descarga(self, clock):
        if not len(self.cola):
            return None

        if not self.lineas_desocupadas():
            return None

        lote, n = self.asignar_lote_siguiente(clock)
        arbitrario = False
        if n is None:
            n = self.asignar_linea_arbitraria()
            if n is None:
                return None
            arbitrario = True

        linea = self.lineas[n]

        tiempo_limpieza = 0
        #print(f'Tipo hib: {lote.tipo}. Hib anterior: {linea.tipo_hibrido}.')
        if lote.tipo != linea.tipo_hibrido and linea.tipo_hibrido is not None:
            tiempo_limpieza += linea.tiempo_limpieza_por_hibrido()
            print(f'Incluyendo tiempo de limpieza: {tiempo_limpieza}.')

        linea.lote_actual = lote
        linea.tipo_hibrido = lote.tipo

        print(f'Se asigna Lote({lote.id}) a la línea de descarga {n}. ', end='')
        if arbitrario:
            print('Esta asignación fue por orden de llegada.')
        else:
            print('Esta asignación fue por mismo tipo de híbrido.')

        tiempo_procesamiento = linea.tiempo_en_pasar() + tiempo_limpieza

        return Evento(clock + tiempo_procesamiento, lote,
                      'termina_descarga', tiempo_limpieza=tiempo_limpieza,
                      descarga=n)


    '''
    Despeja la línea correspondiente. Retorna un Evento('comienza_sorting'),
    '''
    def terminar_descarga(self, lote, n, clock):
        self.lineas[n].desocupar()
        print(f'Desocupando línea de descarga {n}.')
        print(f'Lineas de descarga desocupadas: {self.lineas_desocupadas()}')
        return Evento(clock, lote, 'comienza_sorting')


'''
Módulo que representa el proceso de sorting.
'''
class Sorting:
    def __init__(self):
        self.lineas = self.generar_lineas_sorting()

    '''
    Genera 2 líneas de sorting automáticas (1, 2) y 2 manuales (3, 4). Crea un 
    diccionario para poder acceder a ellas.
    '''
    def generar_lineas_sorting(self):
        linea_1, linea_2 = LineaSorting(True), LineaSorting(True)
        linea_3, linea_4 = LineaSorting(False), LineaSorting(False)
        return {1: linea_1, 2: linea_2, 3: linea_3, 4: linea_4}

    '''
    Retorna una lista con los números de las líneas desocupadas.
    '''
    def lineas_desocupadas(self):
        return [u for u, v in self.lineas.items() if not v.ocupada()]

    '''
    Asigna una línea a un proceso. Asigna en orden creciente (ya que las
    automáticas corresponden a la 1 y 2).
    '''
    def asignar_linea_sorting(self):
        for n, linea in self.lineas.items():
            if not linea.ocupada():
                return n
        raise ValueError('Todas las líneas de Sorting están ocupadas.')

    '''
    Recibe un lote desde una línea de descarga en alguna de las líneas de
    sorting. Retorna un Evento('termina_sorting')
    '''
    def comenzar_sorting(self, lote, clock):
        n = self.asignar_linea_sorting()
        linea = self.lineas[n]
        linea.lote_actual = lote

        tiempo_procesamiento = linea.tiempo_en_pasar()


        print(f'Se asigna Lote({lote.id}) a la línea de sorting {n}.')

        return Evento(clock + tiempo_procesamiento, lote,
                      'termina_sorting', sorting=n)

    '''
    Entrega un lote a alguna de las unidades de secado.
    SUPUESTO: no hay almacenamiento de inventario entre sorting y secado.
    '''
    def terminar_sorting(self, lote, n, clock):
        self.lineas[n].desocupar()
        print(f'Desocupando línea de sorting {n}.')
        return Evento(clock, lote, 'llenar_modulo')

'''
Clase que representa un módulo de un secador.
'''
class Modulo:
    def __init__(self, gmo, capacidad):
        self.gmo = gmo
        self.capacidad = capacidad
        self.velocidad = velocidad_secado

        self.iniciado = False
        self.terminado = False

        self.tiempo_inicio_carga = None
        self.lote_mezclado = None

    '''
    Calcula el tiempo de secado según el conjunto de lotes en el módulo.
    '''
    def tiempo_secado(self):
        return (self.lote_mezclado.humedad - humedad_final_secado) / \
                self.velocidad

    '''
    Retorna True si el módulo está ocupado, False en caso contrario.
    '''
    def ocupado(self):
        if self.lote_mezclado is not None:
            return True
        return False

    '''
    Retorna el tipo de híbrido presente en el módulo.
    '''
    @property
    def tipo_hibrido(self):
        if not self.ocupado():
            return None
        return self.lote_mezclado.tipo

    '''
    Retorna estado correspondiente, dependiendo de (iniciado, terminado).
    '''
    @property
    def estado(self):
        if not self.iniciado:
            return 'esperando_carga'  # (0, *)
        if not self.terminado:
            return 'secando'  # (1, 0)
        return 'esperando_desgrane'  # (1, 1)

    '''
    Retorna la carga del módulo.
    '''
    @property
    def carga(self):
        if not self.ocupado():
            return 0
        return self.lote_mezclado.carga

    '''
    Agrega un lote al LoteMezclado en el módulo.
    '''
    def cargar(self, lote, clock=None):
        if lote.gmo != self.gmo:
            raise ValueError('Cargando GMO incorrecto.')
        if self.estado != 'esperando_carga':
            raise ValueError('Cargando en estado incorrecto.')

        if self.ocupado():
            if lote.tipo != self.tipo_hibrido:
                raise ValueError\
                (f'Intentando cargar módulo con distintos tipos de híbrido '
                 f'({lote.tipo == self.tipo_hibrido}/'
                 f'{self.tipo_hibrido}).')

        else:
            self.lote_mezclado = LoteMezclado(lote.tipo, lote.gmo, clock)
            self.tiempo_inicio_carga = clock

        self.lote_mezclado.agregar_lote(lote)
        print(f'Cargando módulo con {lote.carga} tons. '
              f'{self.capacidad - self.lote_mezclado.carga} tons restantes.')


    '''
    Abre el módulo, una vez terminado el proceso de secado.
    '''
    def abrir(self):
        self.terminado = True
        return self.lote_mezclado

    '''
    Vacía el módulo y actualiza parámetros correspondientes. Retorna un
    LoteMezclado.
    '''
    def vaciar(self):
        if self.estado != 'esperando_desgrane':
            raise ValueError('Vaciando en estado incorrecto.')

        lote_mezclado = self.lote_mezclado

        self.iniciado = False
        self.lote_mezclado = None
        self.tiempo_inicio_carga = None

        return lote_mezclado

    '''
    Cierra el módulo e inicia el secado. Retorna evento de término de secado.
    '''
    def iniciar_secado(self, n, m, clock):
        if self.estado != 'esperando_carga':
            raise ValueError('Iniciando carga en estado incorrecto.')

        self.iniciado = True
        self.terminado = False
        tiempo_proceso = self.tiempo_secado()
        return Evento(clock + tiempo_proceso, self.lote_mezclado,
                      'termina_secado', secador=n, modulo=m)


'''
Clase que representa un secador con sus respectivos módulos.
'''
class Secador:
    def __init__(self, gmo, cantidad, capacidad):
        self.gmo = gmo
        self.capacidad = capacidad
        self.modulos = self.generar_modulos(cantidad, capacidad)
        self.hibridos_contenidos = defaultdict(set)
        self.modulos_vacios = cantidad

    '''
    Genera los módulos correspondientes al secador.
    '''
    def generar_modulos(self, cantidad, capacidad):
        return {n+1: Modulo(self.gmo, capacidad) for n in range(cantidad)}

    '''
    Carga el lote en el módulo m.
    '''
    def lote_a_modulo(self, lote, m, clock):
        modulo = self.modulos[m]

        first = False
        if not modulo.ocupado():
            first = True
            self.modulos_vacios -= 1

        modulo.cargar(lote, clock)

        cumple_capacidad = False
        if modulo.capacidad - modulo.carga <= toneladas_cierre_modulo:
            cumple_capacidad = True

        self.hibridos_contenidos[lote.tipo].add(m)

        if first:
            tiempo_cierre = clock + horas_cierre_modulo
            print('Se genera evento de cierre de módulo por cumplimiento de '
                  f'tiempo. El módulo se cerrará en T <= {tiempo_cierre}.')
            return Evento(tiempo_cierre, None, 'comienza_secado_por_tiempo',
                          modulo=m)

        '''
        No está considerado todavía.
        
        if cumple_capacidad:
            print('Se genera evento de cierre de módulo por cumplimiento de '
                  f'capacidad. El módulo se cerrará en T = {clock}.')
            return Evento(clock, None, 'comienza_secado_por_capacidad',
                          modulo=m)
        '''
        return None



'''
Clase que representa el proceso de Secado.
'''
class Secado:
    def __init__(self):
        self.secadores = self.generar_secadores()
        self.esperando_descarga = SortedList(key=lambda x: -x[2].carga)
        # (n, m, lote_mezclado)

    ''' 
    Genera los 5 secadores correspondientes al proceso de Secado.
    '''
    def generar_secadores(self):
        secador_1 = Secador(True, cantidad_modulos_secador_1,
                            capacidad_modulos_secador_1)
        secador_2 = Secador(True, cantidad_modulos_secador_2,
                            capacidad_modulos_secador_2)
        secador_3 = Secador(True, cantidad_modulos_secador_3,
                            capacidad_modulos_secador_3)
        secador_4 = Secador(False, cantidad_modulos_secador_4,
                            capacidad_modulos_secador_4)
        secador_5 = Secador(False, cantidad_modulos_secador_5,
                            capacidad_modulos_secador_5)
        return {1: secador_2, 2: secador_3, 3: secador_4, 4: secador_5,
                5: secador_1}

    '''
    Retorna el índice del primer contador con gmo específico esperando en la
    cola de descarga.
    '''
    def gmo_esperando_descarga(self, gmo):
        contador = len(self.esperando_descarga) - 1
        for n, m, lote in reversed(self.esperando_descarga):
            if lote.gmo == gmo:
                return contador
            contador -= 1
        return None

    '''
    Retorna tupla (n_secador, m_módulo) según dónde deba dirigirse el lote. Si
    no hay una dirección específica, retorna None.
    '''
    def dirigir_especifico(self, lote):
        for n, secador in self.secadores.items():
            lista_modulos = {}
            if lote.tipo in secador.hibridos_contenidos \
                    and lote.gmo == secador.gmo:
                lista_modulos = secador.hibridos_contenidos[lote.tipo]
            if lista_modulos:
                for m in lista_modulos:
                    if not secador.modulos[m].iniciado:
                        if secador.modulos[m].carga + lote.carga <=\
                           secador.modulos[m].capacidad:
                            return n, m
        return None

    '''
    Retorna tupla (n_secador, m_módulo) según disponibilidad.
    '''
    def asignar_segun_disponibilidad(self, lote):
        for n, secador in self.secadores.items():
            if secador.modulos_vacios and secador.gmo == lote.gmo:
                for m, modulo in secador.modulos.items():
                    if not modulo.ocupado():
                        if lote.carga <= modulo.capacidad:
                            return n, m
        return None

    '''
    Carga el lote en el módulo m del secador n. Retorna un evento de cierre de
    módulo.
    '''
    def lote_a_secador(self, lote, n, m, clock):
        secador = self.secadores[n]
        evento = secador.lote_a_modulo(lote, m, clock)
        if evento is not None:
            evento.secador = n
            return evento
        return None

    '''
    Carga el lote en el secador y módulo que correspondan. Retorna un evento de
    cierre de módulo.
    '''
    def recibir_lote(self, lote, clock):
        n, m, = None, None
        especifico = self.dirigir_especifico(lote)
        if especifico is not None:
            n, m = especifico
            print(f'Dirigiendo Lote({lote.id}) de tipo {lote.tipo} '
                  f'específicamente a Secador({n}), Módulo({m}).')
        else:
            disponibilidad = self.asignar_segun_disponibilidad(lote)
            if disponibilidad is None:

                return Evento(clock, lote, 'perdida_carga', secado=1)
            n, m = disponibilidad
            print(f'Dirigiendo Lote({lote.id}) de tipo {lote.tipo} '
                  f'arbitrariamente a Secador({n}), Módulo({m}).')

        evento = self.lote_a_secador(lote, n, m, clock)
        #print(f'Se asigna Lote({lote.id}) a Módulo({m}) en Secador({n}).')
        return evento

    '''
    Cierra el módulo correspondiente. Retorna evento de término de secado.
    '''
    def cerrar_modulo(self, n, m, clock):
        modulo = self.secadores[n].modulos[m]
        print(f'Comenzando secado en Módulo ({m}) de Secador({n}).')
        return modulo.iniciar_secado(n, m, clock)

    '''
    Abre el módulo correspondiente, dejándolo disponible para ser vaciado.
    '''
    def abrir_modulo(self, n, m, clock=None):
        modulo = self.secadores[n].modulos[m]
        lote_mezclado = modulo.abrir()
        print(f'Abriendo Módulo({m}) en Secador({n}).')

        tupla = (n, m, lote_mezclado)
        self.esperando_descarga.add(tupla)


    '''
    Vacía el módulo correspondiente, dejándolo disponible para ser vuelto a
    usar. 
    '''
    def vaciar_modulo(self, n, m, clock):
        secador = self.secadores[n]
        modulo = secador.modulos[m]

        if not modulo.ocupado():
            raise ValueError('Vaciando módulo desocupado.')

        lote_mezclado = modulo.vaciar()
        secador.modulos_vacios += 1
        if lote_mezclado.tipo in secador.hibridos_contenidos:
            secador.hibridos_contenidos[lote_mezclado.tipo].remove(m)
            if not len(secador.hibridos_contenidos[lote_mezclado.tipo]):
                del secador.hibridos_contenidos[lote_mezclado.tipo]

        print(f'Vaciando Secador({n}), Módulo({m}).')

'''
Módulo que representa el proceso de desgrane.
'''
class Desgrane:
    def __init__(self):
        self.lineas = self.generar_lineas_desgrane()

    '''
    Creación de las 2 lineas de desgrane.
    '''
    def generar_lineas_desgrane(self):
        return {1: LineaDesgrane(True), 2: LineaDesgrane(False)}

    '''
    Retorna el número de la primera línea con GMO requerido desocupada. Si no
    hay disponibilidad, retorna None.
    '''
    def linea_disponible(self, gmo=None):
        for l, linea in self.lineas.items():
            if not linea.ocupada():
                if gmo is not None:
                    if linea.gmo == gmo:
                        return l
                else:
                    return l
        return None

    '''
    Retorna evento comenzar desgrane.
    '''
    def comenzar_desgrane(self, clock, indice=None, desgrane=None):
        return Evento(clock, None, 'comienza_desgrane', indice=indice,
                      desgrane=desgrane)

    '''
    Comienza el proceso de desgrane. Retorna evento de término de desgrane.
    '''
    def recibir_lote(self, lote, n, m, clock, desgrane=None):
        l = desgrane
        if l is None:
            print('l is None 1')
            l = self.linea_disponible(lote.gmo)
            if l is None:
                raise ValueError('Comenzando desgrane sin tener'
                                 'línea disponible.')
        print(f'l = {l}')
        linea = self.lineas[l]
        print(f'Linea({l}), GMO={linea.gmo}; Lote{lote}')
        if linea.gmo != lote.gmo:
            raise ValueError('GMO no compatible en desgrane.')
        tipo_anterior = linea.tipo_hibrido

        linea.lote_actual = lote
        linea.tipo_hibrido = lote.tipo

        tiempo_limpieza = 0
        print(f'Tipo hib: {linea.tipo_hibrido}. Tipo anterior: {tipo_anterior}')
        if linea.tipo_hibrido != tipo_anterior and tipo_anterior is not None:
            tiempo_limpieza = linea.tiempo_limpieza_por_hibrido()
            print(f'Incluyendo tiempo de limpieza {tiempo_limpieza}.')
        tiempo_termino = clock + linea.tiempo_en_pasar() + tiempo_limpieza

        return Evento(tiempo_termino,  lote, 'termina_desgrane',
                      secador=n, modulo=m, desgrane=l)

    '''
    Termina el desgrane por una línea. Retorna evento "vacia_modulo".
    '''
    def terminar_desgrane(self, l, n, m, clock):
        lote = self.lineas[l].lote_actual
        self.lineas[l].desocupar()
        return Evento(clock, lote, 'vaciar_modulo', secador=n, modulo=m)
