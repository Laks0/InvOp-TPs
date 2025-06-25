import itertools
import matplotlib.pyplot as plt

import numpy as np


def manhattan_distance(x, y):
    return np.sum(np.abs(x - y))

def write_instance(distancias, costos, exclusivos, refrigerados, costo_repartidor, max_repartidor, costo_camion_unidad, path: str):
    cant_clientes, _ = distancias.shape
    cant_exclusivos, = exclusivos.shape
    cant_refrigerados, = refrigerados.shape
    with open(path, 'w') as fd:
        fd.write(f"{cant_clientes}\n")
        fd.write(f"{costo_repartidor}\n")
        fd.write(f"{max_repartidor}\n")
        fd.write(f"{cant_refrigerados}\n")
        for refrigerado in refrigerados:
            fd.write(f"{refrigerado}\n")
        fd.write(f"{cant_exclusivos}\n")
        for exclusivo in exclusivos:
            fd.write(f"{exclusivo}\n")
        for i, j in zip(*np.tril_indices(cant_clientes, k=0)):
            if distancias[i,j] < np.inf and costos[i,j] < np.inf:
                fd.write(f"{i} {j} {int(distancias[i,j])} {int(costos[i,j])}\n")



def main():
    seed = sum(map(ord, "soy una semillaa"))
    grid_size = 100
    client_count = 20
    max_repartidor = 15 # Cuantas "cuadras se mueve el repartidor"
    costo_repartidor = 10
    costo_camion_por_unidad = 50
    cant_refrigerados = 0
    cant_exculsivos = 0

    np.random.seed(seed)
    clients = muestra_clientes_uniforme(client_count, grid_size)
    clients = muestra_clientes_clusters(client_count, grid_size, 3, 10)
    exclusivos = np.random.choice(np.arange(client_count), size=cant_exculsivos, replace=False)
    refrigerados = np.random.choice(np.arange(client_count), size=cant_refrigerados, replace=False)

    dibujar_clientes_en_grilla(clients, grid_size)

    distancias, costos = generar_grafo_completo(clients, costo_camion_por_unidad)
    #distancias, costos = generar_grafo_ralo(clients, costo_camion_por_unidad, 0.5)

    write_instance(
        distancias,
        costos,
        exclusivos,
        refrigerados,
        costo_repartidor,
        max_repartidor,
        costo_camion_por_unidad,
        "/tmp/instancia"
    )

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