import itertools
from zipfile import compressor_names

import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import csv
from src.main import cargar_instancia
from src.base import InstanciaRecorridoMixto
from src.modelos.modelo_repartidores import ModeloConRepartidores
from src.modelos.modelo_tsp import ModeloTSP
from src.util import GraficarSolucion
from src.modelos.variantes_con_repartidores import VarianteClientesExclusivos, VarianteRepartidorCuatroOMasClientes

def asegurar_directorio(path):
    os.makedirs(path, exist_ok=True)

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
    seed = sum(map(ord, "Programación lineal entera"))
    grid_size = 50
    client_count = 20
    max_repartidor = 10
    costo_repartidor = 2
    costo_camion_por_unidad = 5
    cant_refrigerados = client_count // 8
    cant_exclusivos = client_count // 4
    tmp_path = "/tmp/instancia"
    n_instancias = 50  # 🔁 Cambiá esto según cuántas instancias quieras

    np.random.seed(seed)
    
    base_path = "test"
    csv_path = os.path.join(base_path, "resultados_modelos.csv")
    
    # Crear carpetas principales
    for tipo in ["clusters", "uniforme"]:
        for subcarpeta in ["grafo", "plano"]:
            asegurar_directorio(os.path.join(base_path, tipo, subcarpeta))
    
    # Escribir encabezado CSV
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["tipo_distribucion", "modelo", "instancia_id", "valor_objetivo"])



    generadores = {
        "uniforme": muestra_clientes_uniforme,
        "clusters": lambda n, g: muestra_clientes_clusters(n, g, 4, 10)
    }

    for tipo, generador in generadores.items():
        for i in range(n_instancias):
            clients = generador(client_count, grid_size)
            exclusivos = np.random.choice(np.arange(client_count), size=cant_exclusivos, replace=False)
            refrigerados = np.random.choice(np.arange(client_count), size=cant_refrigerados, replace=False)

            distancias, costos = generar_grafo_completo(clients, costo_camion_por_unidad)

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

            for Modelo, sufijo in [
                (ModeloTSP, "tsp"),
                (ModeloConRepartidores, "repartidores"),
                (VarianteClientesExclusivos, "exclusivos"),
                (VarianteRepartidorCuatroOMasClientes, "cuatro_o_mas")
            ]:
                instancia = cargar_instancia(tmp_path)
                prob = Modelo(instancia)
                mem_limit = lambda c: c.parameters.mip.limits.treememory.set(1024 * 10)
                tmp_dir = lambda c: c.parameters.workdir.set("/home/santiago/tmp/cplex")
                prob.resolver(mem_limit, tmp_dir)

                valor_obj, instancia, solucion = prob.obtener_solucion()
                plotter = GraficarSolucion(instancia, solucion)
                
                if i < 5:
                    plano_path = os.path.join(base_path, tipo, "plano", f"plano_{tipo}_{sufijo}_{i}.png")
                    grafo_path = os.path.join(base_path, tipo, "grafo", f"grafo_{tipo}_{sufijo}_{i}.png")
                    
                    plotter.dibujar_clientes_en_grilla(grid_size, clients, plano_path)
                    plotter.dibujar_grafo(grafo_path)
                
                # Guardar resultado en CSV
                with open(csv_path, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([tipo, sufijo, i, valor_obj])
                
                prob.liberar()
                del prob



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