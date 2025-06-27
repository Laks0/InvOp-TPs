import itertools
import math

import cplex
import networkx as nx
from matplotlib import pyplot as plt

from src.base import InstanciaRecorridoMixto, VariableNameMapping
from src import TOLERANCE


class GraficarSolucion:
    def __init__(self, instancia: InstanciaRecorridoMixto, instancia_cplex: cplex.Cplex):
        self._instancia = instancia
        self._instancia_cplex = instancia_cplex
        self._nombre_variable_a_valor = self._map_nombres_a_variables()

    def _map_nombres_a_variables(self):
        variables = self._instancia_cplex.solution.get_values()
        nombres = self._instancia_cplex.variables.get_names()
        return {nombre: valor for nombre, valor in zip(nombres, variables)}

    def _circuito_camion(self):
        # Circuito Hamiltoniano del camion
        n = self._instancia.cantidad_clientes
        circuito_camion = []
        for u, v in itertools.product(range(n), range(n)):
            if u == v: continue
            valor_x_u_v = self._nombre_variable_a_valor[VariableNameMapping.x(u, v)]
            if valor_x_u_v > TOLERANCE:
                circuito_camion.append((u, v))
        return circuito_camion

    def _aristas_repartidor(self):
        n = self._instancia.cantidad_clientes
        aristas_repartidor = []
        for u, v in itertools.product(range(n), range(n)):
            if u == v: continue
            try:
                valor_b_u_v = self._nombre_variable_a_valor[VariableNameMapping.b(u, v)]
                if valor_b_u_v > TOLERANCE:
                    aristas_repartidor.append((u, v))
            except KeyError:
                continue  # No todas las b_i_j están definidas
        return aristas_repartidor

    def dibujar_clientes_en_grilla(self, grid_size, clients, export_path: str):
        circuito_camion = self._circuito_camion()
        aristas_repartidor = self._aristas_repartidor()
        funcion_objectivo = self._instancia_cplex.solution.get_objective_value()

        plt.figure(figsize=(6, 6))

        for u, v in circuito_camion:
            punto_u = clients[u,:]
            punto_v = clients[v,:]
            plt.plot([punto_u[0], punto_v[0]], [punto_u[1], punto_v[1]], c='red', linewidth=1, alpha=0.75)

        for u, v in aristas_repartidor:
            punto_u = clients[u,:]
            punto_v = clients[v,:]
            plt.plot([punto_u[0], punto_v[0]], [punto_u[1], punto_v[1]], c='green', linewidth=1, alpha=0.75)

        plt.scatter(clients[:, 0], clients[:, 1], c='blue', marker='o', zorder=3, alpha=0.5)
        plt.xlim(0, grid_size)
        plt.ylim(0, grid_size)
        plt.grid(True, which='both', linestyle=':', linewidth=0.5)

        plt.xlabel('X')
        plt.ylabel('Y')
        plt.title('Clientes en la grilla')
        plt.legend(
            handles=[
                plt.Line2D([0], [0], color='red', linewidth=2, label='Camión'),
                plt.Line2D([0], [0], color='green', linewidth=2, label='Repartidor'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, label='Clientes')
            ],
            loc='upper right',
            facecolor='white',
            edgecolor='black'
        )
        plt.figtext(0.99, 0.01, f'Función objetivo: {funcion_objectivo:.2f}', horizontalalignment='right', fontsize=10)
        plt.savefig(export_path, bbox_inches='tight', dpi=300)
        plt.close()


    def dibujar_grafo(self, export_path: str):
        color_camion = 'skyblue'
        color_repartidor = 'salmon'

        circuito_camion = self._circuito_camion()
        aristas_repartidor = self._aristas_repartidor()

        grafo = nx.Graph()
        grafo.add_nodes_from(range(self._instancia.cantidad_clientes))
        grafo.add_edges_from(circuito_camion)
        grafo.add_edges_from(aristas_repartidor)

        k_val = 2 / math.sqrt(grafo.number_of_nodes())  # para que no estén tan apretados los nodos
        pos = nx.spring_layout(grafo, seed=8_11_1914, k=k_val, iterations=1000)  # Cumple Dantzig

        aristas_ordenadas = {tuple(sorted(edge)) for edge in circuito_camion}

        coloreo_aristas = []
        for u, v in grafo.edges():
            if tuple(sorted((u, v))) in aristas_ordenadas:
                coloreo_aristas.append(color_camion)
            else:
                coloreo_aristas.append(color_repartidor)

        plt.figure(figsize=(20, 16))

        nx.draw(
            grafo,
            pos,
            with_labels=True,
            node_color='lightgray',
            node_size=600,
            font_size=10,
            font_weight='bold',
            edge_color=coloreo_aristas,
            width=2.0
        )
        plt.savefig(export_path, bbox_inches='tight', dpi=300)
        plt.close()

