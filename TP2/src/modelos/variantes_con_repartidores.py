import itertools

from src.base import VariableNameMapping
from src.modelos.modelo_repartidores import ModeloConRepartidores


class VarianteRepartidorCuatroOMasClientes(ModeloConRepartidores):
    def _agregar_restricciones(self):
        super()._agregar_restricciones()
        n = self._instancia.cantidad_clientes
        instancia = self._instancia
        modelo = self._modelo

        # Si se contrata un repartidor, este pasa por al menos 4 clientes
        for i, j in itertools.product(range(n), range(n)):
            if i == j: continue
            if j not in instancia.clientes_alcanzables_por_repartidor_desde(i): continue
            indices = [
                VariableNameMapping.b(i, j),
            ]
            valores = [
                -3
            ]
            indices.extend(
                [VariableNameMapping.b(i, k) for k in instancia.clientes_alcanzables_por_repartidor_desde(i) - {j}])
            valores.extend([1] * len(indices[1:]))
            lhs = [indices, valores]
            modelo.linear_constraints.add(lin_expr=[lhs], senses=["G"], rhs=[0],
                                        names=[f"Al menos 4 por repartidor {i}, {j}"])

class VarianteClientesExclusivos(ModeloConRepartidores):
    def _agregar_restricciones(self):
        super()._agregar_restricciones()
        n = self._instancia.cantidad_clientes
        instancia = self._instancia
        modelo = self._modelo

        for j in instancia.exclusivos:
            indices = []
            for i in range(n):
                if i == j: continue
                if j in instancia.clientes_alcanzables_por_repartidor_desde(i):
                    indices.append(VariableNameMapping.b(i, j))
            valores = [1] * len(indices)
            lhs = [indices, valores]
            modelo.linear_constraints.add(lin_expr=[lhs], senses=["E"], rhs=[0],
                                        names=[f"Cliente exclusivo {j}"])