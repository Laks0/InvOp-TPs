import itertools
from typing import Callable

import cplex

from src import TOLERANCE
from src.base import InstanciaRecorridoMixto, VariableNameMapping
from src.util import GraficarSolucion


class ModeloBase:
    def __init__(self, instancia: InstanciaRecorridoMixto):
        self._instancia = instancia
        self._modelo = cplex.Cplex()
        self._armar_lp()

    def _agregar_variables(self):
        raise RuntimeError("Implementar en subclases")

    def _agregar_restricciones(self):
        raise RuntimeError("Implementar en subclases")

    def _armar_lp(self):
        self._agregar_variables()
        self._agregar_restricciones()
        self._modelo.objective.set_sense(self._modelo.objective.sense.minimize)

    def resolver(self, *argumentos_cplex: Callable):
        for argumento in argumentos_cplex:
            argumento(self._modelo)
        self._modelo.solve()

    def mostrar_solucion(self, output_path: str):
        # Obtener informacion de la solucion a traves de 'solution'

        # Tomar el estado de la resolucion
        status = self._modelo.solution.get_status_string(status_code=self._modelo.solution.get_status())

        # Tomar el valor del funcional
        valor_obj = self._modelo.solution.get_objective_value()

        print('Funcion objetivo: ', valor_obj, '(' + str(status) + ')')

        plotter = GraficarSolucion(self._instancia, self._modelo)
        plotter.dibujar_grafo(output_path)

        # Tomar los valores de las variables
        x = self._modelo.solution.get_values()
        nombres = self._modelo.variables.get_names()

        # Mostrar las variables con valor positivo (mayor que una tolerancia)
        for variable, nombre in zip(x, nombres):
            if variable > TOLERANCE:
                print(nombre, variable)
