#!venv/bin/python3.11
import itertools
import sys
from functools import cache

#importamos el modulo cplex
import cplex

TOLERANCE =10e-6 

class VariableNameMapping:
    @classmethod
    def x(cls, i, j):
        if not (isinstance(i, int) and isinstance(j, int)):
            raise ValueError("i, j deben ser enteros")
        return f"x{i,j}"

    @classmethod
    def b(cls, i, j):
        if not (isinstance(i, int) and isinstance(j, int)):
            raise ValueError("i, j deben ser enteros")
        return f"b{i, j}"

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
        #TODO: el conjunto D_i incluye al cliente i?
        return frozenset(cliente for cliente, distancia in enumerate(self.distancias[cliente_partida])
                if distancia < self.d_max)

    def leer_datos(self,filename):
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
            row = list(map(int,linea.split(' ')))
            self.distancias[row[0]-1][row[1]-1] = row[2]
            self.distancias[row[1]-1][row[0]-1] = row[2]
            self.costos[row[0]-1][row[1]-1] = row[3]
            self.costos[row[1]-1][row[0]-1] = row[3]
        
        # cerramos el archivo
        f.close()

def cargar_instancia():
    # El 1er parametro es el nombre del archivo de entrada
    nombre_archivo = sys.argv[1].strip()
    # Crea la instancia vacia
    instancia = InstanciaRecorridoMixto()
    # Llena la instancia con los datos del archivo de entrada 
    instancia.leer_datos(nombre_archivo)
    return instancia

def agregar_variables(prob: cplex.Cplex, instancia: InstanciaRecorridoMixto):
    # Definir y agregar las variables:
	# metodo 'add' de 'variables', con parametros:
	# obj: costos de la funcion objetivo
	# lb: cotas inferiores
    # ub: cotas superiores
    # types: tipo de las variables
    # names: nombre (como van a aparecer en el archivo .lp)
	
    # Poner nombre a las variables y llenar coef_funcion_objetivo
#    nombres = ....
#    coeficientes_funcion_objetivo = ....
#    
#    # Agregar las variables
#    prob.variables.add(obj = coeficientes_funcion_objetivo, lb = ..., ub = ...., types=..., names=nombres)
    
    n = instancia.cantidad_clientes
    # Variables de orden
    #prob.variables.add(obj = [0]*n, names = [VariableNameMapping.u(i) for i in range(n)], lb=[0]*n, ub=[n-1]*n, types = ['I']*n)
    prob.variables.add(obj=[0], names=[VariableNameMapping.u(0)], lb=[0], ub=[0],
                       types=['I'])
    prob.variables.add(obj=[0] * (n - 1), names=[VariableNameMapping.u(i) for i in range(1, n)], lb=[1] * (n - 1), ub=[n - 1] * (n - 1),
                       types=['I'] * (n - 1))
    # Aristas de camión
    for i in range(n):
        for j in range(n):
            prob.variables.add(obj = [instancia.costos[i][j]], names=[VariableNameMapping.x(i,j)], types = ['B'])
    # Aristas de bicicleta
    for i in range(n):
        for j in range(n):
            prob.variables.add(obj = [instancia.costo_repartidor], names=[VariableNameMapping.b(i,j)], types = ['B'])

def agregar_restricciones(prob: cplex.Cplex, instancia: InstanciaRecorridoMixto):
    # Agregar las restricciones ax <= (>= ==) b:
	# funcion 'add' de 'linear_constraints' con parametros:
	# lin_expr: lista de listas de [ind,val] de a
    # sense: lista de 'L', 'G' o 'E'
    # rhs: lista de los b
    # names: nombre (como van a aparecer en el archivo .lp)

    # Notar que cplex espera "una matriz de restricciones", es decir, una
    # lista de restricciones del tipo ax <= b, [ax <= b]. Por lo tanto, aun cuando
    # agreguemos una unica restriccion, tenemos que hacerlo como una lista de un unico
    # elemento.
    n = instancia.cantidad_clientes

    # A toda ciudad se entra una vez (por camión o bicicleta)
    for i in range(n):
        indices_x = []
        indices_b = []
        for j in range(n):
            if i == j: continue
            indices_x.append(VariableNameMapping.x(j,i))
            indices_b.append(VariableNameMapping.b(j,i))
        lhs = [
            indices_x + indices_b,
            [1]*(len(indices_x) + len(indices_b))
        ]
        prob.linear_constraints.add(lin_expr=[lhs], senses=["E"], rhs=[1], names=[f"Entra una vez a {i}"])

    # Si se entró en camión, se sale por camión
    for i in range(n):
        indices_x_i_j = []
        indices_x_j_i = []
        for j in range(n):
            if i == j: continue
            indices_x_i_j.append(VariableNameMapping.x(i,j))
            indices_x_j_i.append(VariableNameMapping.x(j,i))
        lhs = [
            indices_x_i_j + indices_x_j_i,
            [1]*len(indices_x_i_j) + [-1]* len(indices_x_j_i)
        ]
        prob.linear_constraints.add(lin_expr=[lhs], senses=["E"], rhs=[0], names=[f"Entro y salgo en camión en {i}"])

    # Si se entra en bicicleta, no se sale de otra forma
    for i in range(n):
        indices_b_j_i = []
        indices_x_i_j = []
        for j in range(n):
            if i == j: continue
            indices_x_i_j.append(VariableNameMapping.x(i,j))
            indices_b_j_i.append(VariableNameMapping.b(j,i))
        clientes_alcanzables = instancia.clientes_alcanzables_por_repartidor_desde(i)
        indices_b_i_j = [VariableNameMapping.b(i,j) for j in clientes_alcanzables]
        lhs = [
            indices_b_i_j + indices_x_i_j + indices_b_j_i,
            [1]*(len(indices_b_i_j) + len(indices_x_i_j) + len(indices_b_j_i))
        ]
        prob.linear_constraints.add(lin_expr=[lhs], senses=["L"], rhs=[1], names=[f"Si entro en bicicleta en {i}, no salgo de otra forma"])

    # Ningún repartidor tiene más de un refrigerado
    for i in range(n):
        clientes_alcanzables = instancia.clientes_alcanzables_por_repartidor_desde(i)
        indices_b_i_j = [VariableNameMapping.b(i, j) for j in clientes_alcanzables]
        valores_r_j = [1 if j in instancia.refrigerados else 0 for j in clientes_alcanzables]
        lhs = [
            indices_b_i_j,
            valores_r_j
        ]
        prob.linear_constraints.add(lin_expr=[lhs], senses=["L"], rhs=[1],
                                    names=[f"Repartidor que sale de {i} no tiene más de un refrigerado"])

    for i, j in itertools.product(range(1, n), range(1, n)): #no incluye al v1
        if i == j: continue
        indices = [
            VariableNameMapping.u(i),
            VariableNameMapping.u(j),
            VariableNameMapping.x(i,j)
        ]
        valores = [
            1,
            -1,
            n-1
        ]
        lhs = [indices, valores]
        prob.linear_constraints.add(lin_expr=[lhs], senses=["L"], rhs=[n - 2],
                                    names=[f"Continutidad {i}, {j}"])

def armar_lp(prob: cplex.Cplex, instancia):

    # Agregar las variables
    agregar_variables(prob, instancia)
   
    # Agregar las restricciones 
    agregar_restricciones(prob, instancia)

    # Setear el sentido del problema
    prob.objective.set_sense(prob.objective.sense.minimize)

    # Escribir el lp a archivo
    prob.write('recorridoMixto.lp')

def resolver_lp(prob: cplex.Cplex):
    
    # Definir los parametros del solver
    #prob.parameters.mip.....
       
    # Resolver el lp
    prob.solve()

def mostrar_solucion(prob: cplex.Cplex, instancia):
    
    # Obtener informacion de la solucion a traves de 'solution'
    
    # Tomar el estado de la resolucion
    status = prob.solution.get_status_string(status_code = prob.solution.get_status())
    
    # Tomar el valor del funcional
    valor_obj = prob.solution.get_objective_value()
    
    print('Funcion objetivo: ',valor_obj,'(' + str(status) + ')')
    
    # Tomar los valores de las variables
    x  = prob.solution.get_values()

    # Mostrar las variables con valor positivo (mayor que una tolerancia)
    pass

def main():
    
    # Lectura de datos desde el archivo de entrada
    instancia = cargar_instancia()
    
    # Definicion del problema de Cplex
    prob = cplex.Cplex()
    
    # Definicion del modelo
    armar_lp(prob,instancia)

    # Resolucion del modelo
    resolver_lp(prob)

    # Obtencion de la solucion
    mostrar_solucion(prob,instancia)

if __name__ == '__main__':
    main()
