import matplotlib.pyplot as plt
import numpy as np
import concurrent.futures

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

        self._puntos = puntos
        self._pesos = pesos

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
