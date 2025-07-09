import matplotlib.pyplot as plt
import numpy as np
import concurrent.futures
import os


from numpy import dtype

class metodo:
    def __init__(self, puntos, pesos, epsilon=1e-8):
        """
        Los puntos deben ser una matriz de R^(m x n) y los pesos un vector de R^m.
        Siendo m la cantidad de puntos y n la dimensión del espacio.
        """
        (cantidad_puntos, _) = puntos.shape
        (cantidad_pesos, ) = pesos.shape
        assert cantidad_puntos == cantidad_pesos
        assert np.all(pesos > 0)
        
        self.contador_iteraciones = 0
        self._puntos = puntos
        self._pesos = pesos
        self.epsilon = epsilon
        self.recorrido = []

    def _seleccionar_punto_inicial(self):
        puntos = self._puntos
        return puntos[0,:]

    def _iterar_desde_punto(self, punto_inicial):
        pass

    def optimizar(self):
        punto_inicial = self._seleccionar_punto_inicial()
        return self._iterar_desde_punto(punto_inicial)

def W(x, puntos, pesos):
    norma = np.linalg.norm(x - puntos, axis=1)
    return np.sum(norma * pesos, axis=0)

def generar_instancias_uniformes(N = 10_000, grid_size = 500, dimension = 30):
    puntos = np.random.uniform(0, grid_size, (N, dimension))
    pesos = np.random.uniform(0, grid_size, (N,))
    return puntos, pesos

def generar_instancias_densas(N, grid_size, dimension, n_clusters):
    clusters = np.random.uniform(0, grid_size, (n_clusters, dimension))
    puntos_por_cluster = N // n_clusters
    cluster_stack = []
    for i in range(n_clusters):
        centro = clusters[i, :]
        p_cluster = np.random.uniform(0, grid_size // 1000, (puntos_por_cluster, dimension))
        cluster_stack.append(centro + p_cluster)
    resto = N % n_clusters
    for i in range(resto):
        centro = clusters[i, :]
        p_cluster = np.random.uniform(0, grid_size // 1000, (1, dimension))
        cluster_stack.append(centro + p_cluster)
    puntos = np.concat(cluster_stack)
    assert puntos.shape[0] == N
    pesos = np.random.uniform(0, grid_size, (N,))
    return puntos, pesos



def grafico_instancias_2d(puntos, pesos, grid_size, ruta, recorrido=[]):
    nx, ny = len(puntos)*2, len(puntos)*2
    x_vals = np.linspace(0, grid_size, nx)
    y_vals = np.linspace(0, grid_size, ny)
    X, Y = np.meshgrid(x_vals, y_vals)
    
    Z = np.zeros_like(X)
    for j in range(ny):
        for i in range(nx):
            Z[j,i] = W(np.array([X[j,i], Y[j,i]]), puntos, pesos)
    
    plt.figure()
    contour = plt.contourf(X, Y, Z, levels=30, cmap='gray')
    plt.scatter(puntos[:, 0], puntos[:, 1], s=(pesos/np.max(pesos))*100, alpha=0.6, marker='+', linewidths=2, c='darkred')
    if recorrido is not None:
        x_coords = [x[0] for x in recorrido]
        y_coords = [x[1] for x in recorrido]
        plt.plot(x_coords, y_coords, marker='o', lw=1, ms=2)
    plt.title("Contorno de W(x) y puntos ponderados")
    #plt.xlabel("X")
    #plt.ylabel("Y")
    plt.colorbar(contour, label="W(x)")
    plt.gca().set_aspect('equal', adjustable='box')

    plt.savefig(ruta,dpi=300,bbox_inches='tight')