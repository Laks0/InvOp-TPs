import itertools
from src.modelos.modelo_base import ModeloBase
from src.base import VariableNameMapping


class ModeloTSP(ModeloBase):
    def _agregar_variables(self):
        n = self._instancia.cantidad_clientes
        instancia = self._instancia
        modelo = self._modelo
        # Variables de orden
        modelo.variables.add(obj=[0], names=[VariableNameMapping.u(0)], lb=[0], ub=[0],
                           types=['I'])
        modelo.variables.add(obj=[0] * (n - 1), names=[VariableNameMapping.u(i) for i in range(1, n)], lb=[1] * (n - 1),
                           ub=[n - 1] * (n - 1),
                           types=['I'] * (n - 1))
        # Aristas de camión
        for i in range(n):
            for j in range(n):
                modelo.variables.add(obj=[instancia.costos[i][j]], names=[VariableNameMapping.x(i, j)], types=['B'])

    def _agregar_restricciones(self):
        n = self._instancia.cantidad_clientes
        instancia = self._instancia
        modelo = self._modelo

        # A toda ciudad se entra una vez (por camión o bicicleta)
        for i in range(n):
            indices_x = []
            for j in range(n):
                if i == j: continue
                indices_x.append(VariableNameMapping.x(j, i))
            lhs = [
                indices_x,
                [1] * len(indices_x)
            ]
            modelo.linear_constraints.add(lin_expr=[lhs], senses=["E"], rhs=[1], names=[f"Entra una vez a {i}"])

        # Si se entró en camión, se sale por camión
        for i in range(n):
            indices_x_i_j = []
            indices_x_j_i = []
            for j in range(n):
                if i == j: continue
                indices_x_i_j.append(VariableNameMapping.x(i, j))
                indices_x_j_i.append(VariableNameMapping.x(j, i))
            lhs = [
                indices_x_i_j + indices_x_j_i,
                [1] * len(indices_x_i_j) + [-1] * len(indices_x_j_i)
            ]
            modelo.linear_constraints.add(lin_expr=[lhs], senses=["E"], rhs=[0],
                                          names=[f"Entro y salgo en camión en {i}"])

        # Continuidad
        for i, j in itertools.product(range(1, n), range(1, n)):  # no incluye al v1
            if i == j: continue
            indices = [
                VariableNameMapping.u(i),
                VariableNameMapping.u(j),
                VariableNameMapping.x(i, j),
            ]
            valores = [
                1,
                -1,
                n - 1,

            ]
            lhs = [indices, valores]
            modelo.linear_constraints.add(lin_expr=[lhs], senses=["L"], rhs=[n - 2],
                                        names=[f"Continutidad {i}, {j}"])
