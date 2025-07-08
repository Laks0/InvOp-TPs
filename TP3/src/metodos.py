import matplotlib.pyplot as plt
import numpy as np
import concurrent.futures
import os


from numpy import dtype

class metodo:
    def __init__(self, puntos, pesos):
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

def generar_instancias(N = 10_000, grid_size = 500, dimension = 30):
    puntos = np.random.uniform(0, grid_size, (N, dimension))
    pesos = np.random.uniform(0, grid_size, (N,))
    return puntos, pesos

def grafico_instancias_2d(puntos, pesos, grid_size, ruta, recorrido=[]):
    nx, ny = grid_size*2, grid_size*2
    x_vals = np.linspace(0, grid_size, nx)
    y_vals = np.linspace(0, grid_size, ny)
    X, Y = np.meshgrid(x_vals, y_vals)
    
    Z = np.zeros_like(X)
    for j in range(ny):
        for i in range(nx):
            Z[j,i] = W(np.array([X[j,i], Y[j,i]]), puntos, pesos)
    
    plt.figure()
    contour = plt.contourf(X, Y, Z, levels=30, cmap='gray')
    plt.scatter(puntos[:, 0], puntos[:, 1], s=pesos/np.max(pesos)*grid_size/2, alpha=0.6, marker='+', linewidths=2, c='darkred')
    if recorrido is not None:
        x_coords = [x[0] for x in recorrido]
        y_coords = [x[1] for x in recorrido]
        plt.plot(x_coords, y_coords, marker='o', lw=1, ms=4)
    plt.title("Contorno de W(x) y puntos ponderados")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.colorbar(contour, label="W(x)")
    plt.gca().set_aspect('equal', adjustable='box')

    plt.savefig(ruta,dpi=300,bbox_inches='tight')

