import itertools
import time
import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import pandas as pd
from cplex._internal._constants import CPX_NODESEL_DFS

from src.main import cargar_instancia
from src.base import InstanciaRecorridoMixto
from src.modelos.modelo_repartidores import ModeloConRepartidores
from src.modelos.modelo_tsp import ModeloTSP
from src.util import GraficarSolucion
from src.modelos.variantes_con_repartidores import VarianteClientesExclusivos, VarianteRepartidorCuatroOMasClientes


def manhattan_distance(x, y):
    return np.sum(np.abs(x - y))

def write_instance(distancias, costos, exclusivos, refrigerados, costo_repartidor, max_repartidor, costo_camion_unidad, path: str):
    cant_clientes, _ = distancias.shape
    cant_exclusivos, = exclusivos.shape
    cant_refrigerados, = refrigerados.shape
    # El TP indexa los clientes de 1 a n. NO SE INDEXA DESDE EL 0!!!!
    with open(path, 'w') as fd:
        fd.write(f"{cant_clientes}\n")
        fd.write(f"{costo_repartidor}\n")
        fd.write(f"{max_repartidor}\n")
        fd.write(f"{cant_refrigerados}\n")
        for refrigerado in refrigerados:
            fd.write(f"{refrigerado + 1}\n")
        fd.write(f"{cant_exclusivos}\n")
        for exclusivo in exclusivos:
            fd.write(f"{exclusivo + 1}\n")
        for i, j in zip(*np.tril_indices(cant_clientes, k=0)):
            if i == j:
                continue
            if distancias[i,j] < np.inf and costos[i,j] < np.inf:
                fd.write(f"{i + 1} {j + 1} {int(distancias[i,j])} {int(costos[i,j])}\n")



def main():
    #generar_instancias_evaluacion_modelos_clustered()
    #generar_instancias_evaluacion_modelos_uniformes()
    testeos_rendimiento()



def testeos_rendimiento():
    seed = sum(map(ord, "Programación lineal entera"))
    grid_size = 100
    client_count = 75
    max_repartidor = 12  # Cuantas "cuadras" se mueve el repartidor
    costo_repartidor = 2
    costo_camion_por_unidad = 5
    cant_refrigerados = client_count // 8
    cant_exculsivos = client_count // 4
    tmp_path = "/tmp/instancia"
    np.random.seed(seed)

    tiempos_dfs = []
    tiempos_default = []

    df = pd.DataFrame(columns=["default", "no_default"])

    for i in range(3):

        #clients = muestra_clientes_uniforme(client_count, grid_size)
        clients = muestra_clientes_clusters(client_count, grid_size, 7, 10)
        exclusivos = np.random.choice(np.arange(client_count), size=cant_exculsivos, replace=False)
        refrigerados = np.random.choice(np.arange(client_count), size=cant_refrigerados, replace=False)

        distancias, costos = generar_grafo_completo(clients, costo_camion_por_unidad)
        #distancias, costos = generar_grafo_ralo(clients, costo_camion_por_unidad, 0.6)

        write_instance(
            distancias,
            costos,
            exclusivos,
            refrigerados,
            costo_repartidor,
            max_repartidor,
            costo_camion_por_unidad,
            tmp_path
        )

        instancia = cargar_instancia(tmp_path)
        prob = ModeloConRepartidores(instancia)
        mem_limit = lambda c: c.parameters.mip.limits.treememory.set(1024 * 32)  # 32GB

        prob._modelo.parameters.randomseed.set(seed)
        prob._modelo.parameters.timelimit.set(60 * 10) # 10 min

        t0 = time.monotonic()
        prob.resolver(mem_limit)
        t1 = time.monotonic()

        objectivo_default, _, _ = prob.obtener_solucion()

        tiempo_default = t1 - t0
        tiempos_default.append(tiempo_default)

        instancia = cargar_instancia(tmp_path)
        prob = ModeloConRepartidores(instancia)
        mem_limit = lambda c: c.parameters.mip.limits.treememory.set(1024 * 32)  # 32GB

        prob._modelo.parameters.randomseed.set(seed)
        prob._modelo.parameters.timelimit.set(60 * 10) # 10 min

        # Busqueda DFS
        #prob._modelo.parameters.mip.strategy.nodeselect.set(prob._modelo.parameters.mip.strategy.nodeselect.values.depth_first)

        # Busqueda best estimate
        #prob._modelo.parameters.mip.strategy.nodeselect.set(prob._modelo.parameters.mip.strategy.nodeselect.values.best_estimate)

        #prob._modelo.parameters.mip.strategy.heuristiceffort.set(10)

        prob._modelo.parameters.mip.strategy.variableselect.set(4)

        #prob._modelo.parameters.threads.set(6)

        #prob._modelo.parameters.mip.cuts.nodecuts.set(1)
        #prob._modelo.parameters.mip.cuts.gomory.set(2)
        #prob._modelo.parameters.mip.cuts.flowcovers.set(2)
        # Con todas las semillas fijas estas corridas deberían ser deterministicas (salvo por variaciones en la carga de la computadora)

        t0 = time.monotonic()
        prob.resolver(mem_limit)
        t1 = time.monotonic()

        objectivo_no_default, _, _ = prob.obtener_solucion()

        tiempo_dfs = t1 - t0
        tiempos_dfs.append(tiempo_dfs)

        df.loc[len(df)] = {
            "default": objectivo_default,
            "no_default": objectivo_no_default
        }

        df.to_csv(f'objetivo_{i}.csv', index=False)


    print("Tiempos default:", tiempos_default)
    print("Tiempos DFS: ", tiempos_dfs)

def generar_instancias_evaluacion_modelos_uniformes():
    seed = sum(map(ord, "branch and bound"))
    grid_size = 75
    client_count = 25
    max_repartidor = 10 # Cuantas "cuadras" se mueve el repartidor
    costo_repartidor = 2
    costo_camion_por_unidad = 5
    cant_refrigerados = client_count // 8
    cant_exculsivos = client_count // 4
    tmp_path = "/tmp/instancia"
    np.random.seed(seed)

    costos_por_modelo = pd.DataFrame(columns=["modelo_tsp", "modelo_repartidores", "deseable_cuatro", "deseable_exclusivos"])

    for i in range(15):
        fila_df = {}

        clients = muestra_clientes_uniforme(client_count, grid_size)
        #clients = muestra_clientes_clusters(client_count, grid_size, 4, 10)
        exclusivos = np.random.choice(np.arange(client_count), size=cant_exculsivos, replace=False)
        refrigerados = np.random.choice(np.arange(client_count), size=cant_refrigerados, replace=False)

        distancias, costos = generar_grafo_completo(clients, costo_camion_por_unidad)
        # distancias, costos = generar_grafo_ralo(clients, costo_camion_por_unidad, 0.65)

        write_instance(
            distancias,
            costos,
            exclusivos,
            refrigerados,
            costo_repartidor,
            max_repartidor,
            costo_camion_por_unidad,
            tmp_path
        )

        # Modelo TSP
        instancia = cargar_instancia(tmp_path)
        prob = ModeloTSP(instancia)
        mem_limit = lambda c: c.parameters.mip.limits.treememory.set(1024 * 32)  # 32GB
        tmp_dir = lambda c: c.parameters.workdir.set("/home/jorge/tmp/cplex")
        prob.resolver(mem_limit, tmp_dir)

        valor_obj, instancia, solucion = prob.obtener_solucion()

        fila_df["modelo_tsp"] = valor_obj

        prob._modelo.end()
        del prob

        #plotter = GraficarSolucion(instancia, solucion)
        #plotter.dibujar_clientes_en_grilla(grid_size, clients, f"plano_uniforme_tsp_{i}.png")
        #plotter.dibujar_grafo(f"grafo_uniforme_tsp_{i}.png")

        # Modelo repartidores
        instancia = cargar_instancia(tmp_path)
        prob = ModeloConRepartidores(instancia)
        mem_limit = lambda c: c.parameters.mip.limits.treememory.set(1024 * 32)  # 32GB
        tmp_dir = lambda c: c.parameters.workdir.set("/home/jorge/tmp/cplex")
        prob.resolver(mem_limit, tmp_dir)

        valor_obj, instancia, solucion = prob.obtener_solucion()

        fila_df["modelo_repartidores"] = valor_obj

        prob._modelo.end()
        del prob

        #plotter = GraficarSolucion(instancia, solucion)
        #plotter.dibujar_clientes_en_grilla(grid_size, clients, f"plano_uniforme_repartidores_{i}.png")
        #plotter.dibujar_grafo(f"grafo_uniforme_repartidores_{i}.png")

        # Deseable clientes exclusivos
        instancia = cargar_instancia(tmp_path)
        prob = VarianteClientesExclusivos(instancia)
        mem_limit = lambda c: c.parameters.mip.limits.treememory.set(1024 * 32)  # 32GB
        tmp_dir = lambda c: c.parameters.workdir.set("/home/jorge/tmp/cplex")
        prob.resolver(mem_limit, tmp_dir)

        valor_obj, instancia, solucion = prob.obtener_solucion()

        fila_df["deseable_exclusivos"] = valor_obj

        prob._modelo.end()
        del prob

        #plotter = GraficarSolucion(instancia, solucion)
        #plotter.dibujar_clientes_en_grilla(grid_size, clients, f"plano_uniforme_exclusivos_{i}.png")
        #plotter.dibujar_grafo(f"grafo_uniforme_exclusivos_{i}.png")

        # Deseable 4 o mas clientes por repartidor
        instancia = cargar_instancia(tmp_path)
        prob = VarianteRepartidorCuatroOMasClientes(instancia)
        mem_limit = lambda c: c.parameters.mip.limits.treememory.set(1024 * 32)  # 32GB
        tmp_dir = lambda c: c.parameters.workdir.set("/home/jorge/tmp/cplex")
        prob.resolver(mem_limit, tmp_dir)

        valor_obj, instancia, solucion = prob.obtener_solucion()

        fila_df["deseable_cuatro"] = valor_obj

        prob._modelo.end()
        del prob

        #plotter = GraficarSolucion(instancia, solucion)
        #plotter.dibujar_clientes_en_grilla(grid_size, clients, f"plano_uniforme_cuatro_o_mas_{i}.png")
        #plotter.dibujar_grafo(f"grafo_uniforme_cuatro_o_mas_{i}.png")

        costos_por_modelo.loc[len(costos_por_modelo)] = fila_df

        costos_por_modelo.to_csv(f'uniforme_{i}.csv', index=False)

    costos_por_modelo.to_csv('uniforme.csv', index=False)

def generar_instancias_evaluacion_modelos_clustered():
    seed = sum(map(ord, "branch and bound"))
    grid_size = 75
    client_count = 25
    max_repartidor = 10 # Cuantas "cuadras" se mueve el repartidor
    costo_repartidor = 2
    costo_camion_por_unidad = 5
    cant_refrigerados = client_count // 8
    cant_exculsivos = client_count // 4
    tmp_path = "/tmp/instancia"
    np.random.seed(seed)

    costos_por_modelo = pd.DataFrame(columns=["modelo_tsp", "modelo_repartidores", "deseable_cuatro", "deseable_exclusivos"])

    for i in range(15):
        fila_df = {}

        # clients = muestra_clientes_uniforme(client_count, grid_size)
        clients = muestra_clientes_clusters(client_count, grid_size, 4, 10)
        exclusivos = np.random.choice(np.arange(client_count), size=cant_exculsivos, replace=False)
        refrigerados = np.random.choice(np.arange(client_count), size=cant_refrigerados, replace=False)

        distancias, costos = generar_grafo_completo(clients, costo_camion_por_unidad)
        # distancias, costos = generar_grafo_ralo(clients, costo_camion_por_unidad, 0.65)

        write_instance(
            distancias,
            costos,
            exclusivos,
            refrigerados,
            costo_repartidor,
            max_repartidor,
            costo_camion_por_unidad,
            tmp_path
        )

        # Modelo TSP
        instancia = cargar_instancia(tmp_path)
        prob = ModeloTSP(instancia)
        mem_limit = lambda c: c.parameters.mip.limits.treememory.set(1024 * 32)  # 32GB
        tmp_dir = lambda c: c.parameters.workdir.set("/home/jorge/tmp/cplex")
        prob.resolver(mem_limit, tmp_dir)

        valor_obj, instancia, solucion = prob.obtener_solucion()

        fila_df["modelo_tsp"] = valor_obj

        prob._modelo.end()
        del prob

        #plotter = GraficarSolucion(instancia, solucion)
        #plotter.dibujar_clientes_en_grilla(grid_size, clients, f"plano_clusters_tsp_{i}.png")
        #plotter.dibujar_grafo(f"grafo_clusters_tsp_{i}.png")

        # Modelo repartidores
        instancia = cargar_instancia(tmp_path)
        prob = ModeloConRepartidores(instancia)
        mem_limit = lambda c: c.parameters.mip.limits.treememory.set(1024 * 32)  # 32GB
        tmp_dir = lambda c: c.parameters.workdir.set("/home/jorge/tmp/cplex")
        prob.resolver(mem_limit, tmp_dir)

        valor_obj, instancia, solucion = prob.obtener_solucion()

        fila_df["modelo_repartidores"] = valor_obj

        prob._modelo.end()
        del prob

        #plotter = GraficarSolucion(instancia, solucion)
        #plotter.dibujar_clientes_en_grilla(grid_size, clients, f"plano_clusters_repartidores_{i}.png")
        #plotter.dibujar_grafo(f"grafo_clusters_repartidores_{i}.png")

        # Deseable clientes exclusivos
        instancia = cargar_instancia(tmp_path)
        prob = VarianteClientesExclusivos(instancia)
        mem_limit = lambda c: c.parameters.mip.limits.treememory.set(1024 * 32)  # 32GB
        tmp_dir = lambda c: c.parameters.workdir.set("/home/jorge/tmp/cplex")
        prob.resolver(mem_limit, tmp_dir)

        valor_obj, instancia, solucion = prob.obtener_solucion()

        fila_df["deseable_exclusivos"] = valor_obj

        prob._modelo.end()
        del prob

        #plotter = GraficarSolucion(instancia, solucion)
        #plotter.dibujar_clientes_en_grilla(grid_size, clients, f"plano_clusters_exclusivos_{i}.png")
        #plotter.dibujar_grafo(f"grafo_clusters_exclusivos_{i}.png")

        # Deseable 4 o mas clientes por repartidor
        instancia = cargar_instancia(tmp_path)
        prob = VarianteRepartidorCuatroOMasClientes(instancia)
        mem_limit = lambda c: c.parameters.mip.limits.treememory.set(1024 * 32)  # 32GB
        tmp_dir = lambda c: c.parameters.workdir.set("/home/jorge/tmp/cplex")
        prob.resolver(mem_limit, tmp_dir)

        valor_obj, instancia, solucion = prob.obtener_solucion()

        fila_df["deseable_cuatro"] = valor_obj

        prob._modelo.end()
        del prob

        #plotter = GraficarSolucion(instancia, solucion)
        #plotter.dibujar_clientes_en_grilla(grid_size, clients, f"plano_clusters_cuatro_o_mas_{i}.png")
        #plotter.dibujar_grafo(f"grafo_clusters_cuatro_o_mas_{i}.png")

        costos_por_modelo.loc[len(costos_por_modelo)] = fila_df

        costos_por_modelo.to_csv(f'clusters_{i}.csv', index=False)

    costos_por_modelo.to_csv('clusters.csv', index=False)

def dibujar_clientes_en_grilla(clients, grid_size):
    plt.figure(figsize=(6, 6))
    plt.scatter(clients[:, 0], clients[:, 1], c='blue', marker='o')
    plt.xlim(0, grid_size)
    plt.ylim(0, grid_size)
    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Clientes en la grilla')
    plt.show()

def muestra_clientes_uniforme(client_count, grid_size):
    clients = np.random.randint(0, grid_size, size=(client_count, 2))
    return clients

def muestra_clientes_clusters(client_count, grid_size, clusters, cluster_radius):
    assert client_count >= clusters
    clientes_por_cluster = [client_count // clusters] * clusters
    for i in range(client_count % clusters):
        clientes_por_cluster[i] += 1

    assert grid_size - cluster_radius > cluster_radius

    # Las filas de la matriz circulos es el punto (x,y) de su centro.
    # Voy a muestrear clientes al rededor de esos circulos.
    circulos = np.random.randint(0, grid_size, size=(clusters, 2))
    clients = []
    for idx, clientes_por_cluster in enumerate(clientes_por_cluster):
        # Tomo clientes dentro del circulo en coordenadas polares
        angulos = np.random.uniform(0, 2 * np.pi, clientes_por_cluster)
        distancia_radio = np.random.uniform(0, cluster_radius, clientes_por_cluster)

        # Paso a coordenadas cartesianas
        x_offsets = (distancia_radio * np.cos(angulos)).astype(int)
        y_offsets = (distancia_radio * np.sin(angulos)).astype(int)

        puntos_cluster_actual = circulos[idx] + np.stack([x_offsets, y_offsets], axis=1)
        puntos_cluster_actual = np.clip(puntos_cluster_actual, 0, grid_size - 1)
        clients.append(puntos_cluster_actual)
    puntos_clientes = np.vstack(clients)
    n_clientes, _ = puntos_clientes.shape
    assert n_clientes == client_count
    return np.vstack(clients)

def generar_grafo_ralo(clients, costo_camion_por_unidad, probabilidad_agregar_arista):
    client_count = len(clients)
    distancias = np.zeros((client_count, client_count)) + np.inf
    costos = np.zeros((client_count, client_count)) + np.inf
    # Aseguro un circuito
    for i in range(1, len(clients)):
        distancias[i - 1, i] = manhattan_distance(clients[i - 1], clients[i])
        costos[i - 1, i] = distancias[i - 1, i] * costo_camion_por_unidad
    distancias[len(clients) - 1, 0] = manhattan_distance(clients[len(clients) - 1], clients[0])
    costos[len(clients) - 1, 0] = distancias[len(clients) - 1, 0] * costo_camion_por_unidad

    for i, j in itertools.product(range(client_count), range(client_count)):
        if np.random.random() <= probabilidad_agregar_arista:
            distancias[i, j] = manhattan_distance(clients[i], clients[j])
            costos[i, j] = distancias[i, j] * costo_camion_por_unidad
    costos *= np.random.uniform(0.75, 1.25, size=costos.shape)  # Variación en los costos del camión
    return distancias, costos

def generar_grafo_completo(clients, costo_camion_por_unidad):
    client_count = len(clients)
    distancias = np.zeros((client_count, client_count)) + np.inf
    costos = np.zeros((client_count, client_count)) + np.inf
    for i, j in itertools.product(range(client_count), range(client_count)):
        distancias[i, j] = manhattan_distance(clients[i], clients[j])
        costos[i, j] = distancias[i, j] * costo_camion_por_unidad
    costos *= np.random.uniform(0.75, 1.25, size=costos.shape)  # Variación en los costos del camión
    return distancias, costos


if __name__ == "__main__":
    main()
