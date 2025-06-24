import itertools
from src.modelos.modelo_base import ModeloBase
from src.base import VariableNameMapping


class ModeloConRepartidores(ModeloBase):
    def _agregar_variables(self):
        n = self._instancia.cantidad_clientes
        instancia = self._instancia
        modelo = self._modelo
        # Variables de orden
        # prob.variables.add(obj = [0]*n, names = [VariableNameMapping.u(i) for i in range(n)], lb=[0]*n, ub=[n-1]*n, types = ['I']*n)
        modelo.variables.add(obj=[0], names=[VariableNameMapping.u(0)], lb=[0], ub=[0],
                           types=['I'])
        modelo.variables.add(obj=[0] * (n - 1), names=[VariableNameMapping.u(i) for i in range(1, n)], lb=[1] * (n - 1),
                           ub=[n - 1] * (n - 1),
                           types=['I'] * (n - 1))
        # Aristas de camión
        for i in range(n):
            for j in range(n):
                modelo.variables.add(obj=[instancia.costos[i][j]], names=[VariableNameMapping.x(i, j)], types=['B'])
        # Aristas de bicicleta
        for i in range(n):
            clientes_alcanzables = instancia.clientes_alcanzables_por_repartidor_desde(i)
            for j in range(n):
                if j in clientes_alcanzables:
                    modelo.variables.add(obj=[instancia.costo_repartidor], names=[VariableNameMapping.b(i, j)],
                                       types=['B'])

    def _agregar_restricciones(self):
        n = self._instancia.cantidad_clientes
        instancia = self._instancia
        modelo = self._modelo

        # A toda ciudad se entra una vez (por camión o bicicleta)
        for i in range(n):
            indices_x = []
            indices_b = []
            for j in range(n):
                if i == j: continue
                clientes_alcanzables = instancia.clientes_alcanzables_por_repartidor_desde(j)
                indices_x.append(VariableNameMapping.x(j, i))
                if i in clientes_alcanzables:
                    indices_b.append(VariableNameMapping.b(j, i))
            lhs = [
                indices_x + indices_b,
                [1] * (len(indices_x) + len(indices_b))
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

        # Si se entra en bicicleta, no se sale de otra forma
        for i in range(n):
            indices_b_j_i = []
            indices_x_i_j = []
            indices_b_i_j = []
            clientes_alcanzables_desde_i = instancia.clientes_alcanzables_por_repartidor_desde(i)
            for j in range(n):
                if i == j: continue
                clientes_alcanzables_desde_j = instancia.clientes_alcanzables_por_repartidor_desde(j)
                indices_x_i_j.append(VariableNameMapping.x(i, j))
                if i in clientes_alcanzables_desde_j:
                    indices_b_j_i.append(VariableNameMapping.b(j, i))
                if j in clientes_alcanzables_desde_i:
                    indices_b_i_j.append(VariableNameMapping.b(i, j))
            lhs = [
                indices_b_j_i + indices_x_i_j + indices_b_i_j,
                [n] * len(indices_b_j_i) + [1] * (len(indices_x_i_j) + len(indices_b_i_j))
            ]
            modelo.linear_constraints.add(lin_expr=[lhs], senses=["L"], rhs=[n],
                                        names=[f"Si entro en bicicleta en {i}, no salgo de otra forma"])

        # Ningún repartidor tiene más de un refrigerado
        for i in range(n):
            clientes_alcanzables = instancia.clientes_alcanzables_por_repartidor_desde(i)
            indices_b_i_j = [VariableNameMapping.b(i, j) for j in clientes_alcanzables]
            valores_r_j = [1 if j in instancia.refrigerados else 0 for j in clientes_alcanzables]
            lhs = [
                indices_b_i_j,
                valores_r_j
            ]
            modelo.linear_constraints.add(lin_expr=[lhs], senses=["L"], rhs=[1],
                                        names=[f"Repartidor que sale de {i} no tiene más de un refrigerado"])

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
