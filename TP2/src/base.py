from functools import cache


class VariableNameMapping:
    @classmethod
    def x(cls, i, j):
        if not (isinstance(i, int) and isinstance(j, int)):
            raise ValueError("i, j deben ser enteros")
        return f"x{i},{j}"

    @classmethod
    def b(cls, i, j):
        if not (isinstance(i, int) and isinstance(j, int)):
            raise ValueError("i, j deben ser enteros")
        return f"b{i},{j}"

    @classmethod
    def u(cls, i):
        if not isinstance(i, int):
            raise ValueError("i debe ser entero")
        return f"u{i}"


class InstanciaRecorridoMixto:
    def __init__(self):
        self.cantidad_clientes = 0
        self.costo_repartidor = 0
        self.d_max = 0
        self.refrigerados = []
        self.exclusivos = []
        self.distancias = []
        self.costos = []

    @cache
    def clientes_alcanzables_por_repartidor_desde(self, cliente_partida: int):
        return frozenset(cliente for cliente, distancia in enumerate(self.distancias[cliente_partida])
                         if distancia < self.d_max)

    def leer_datos(self, filename):
        # abrimos el archivo de datos
        f = open(filename)

        # leemos la cantidad de clientes
        self.cantidad_clientes = int(f.readline())
        # leemos el costo por pedido del repartidor
        self.costo_repartidor = int(f.readline())
        # leemos la distamcia maxima del repartidor
        self.d_max = int(f.readline())

        # inicializamos distancias y costos con un valor muy grande (por si falta algun par en los datos)
        self.distancias = [[1000000 for _ in range(self.cantidad_clientes)] for _ in range(self.cantidad_clientes)]
        self.costos = [[1000000 for _ in range(self.cantidad_clientes)] for _ in range(self.cantidad_clientes)]

        # leemos la cantidad de refrigerados
        cantidad_refrigerados = int(f.readline())
        # leemos los clientes refrigerados
        for i in range(cantidad_refrigerados):
            self.refrigerados.append(int(f.readline()))

        # leemos la cantidad de exclusivos
        cantidad_exclusivos = int(f.readline())
        # leemos los clientes exclusivos
        for i in range(cantidad_exclusivos):
            self.exclusivos.append(int(f.readline()))

        # leemos las distancias y costos entre clientes
        lineas = f.readlines()
        for linea in lineas:
            row = list(map(int, linea.split(' ')))
            self.distancias[row[0] - 1][row[1] - 1] = row[2]
            self.distancias[row[1] - 1][row[0] - 1] = row[2]
            self.costos[row[0] - 1][row[1] - 1] = row[3]
            self.costos[row[1] - 1][row[0] - 1] = row[3]

        # cerramos el archivo
        f.close()
