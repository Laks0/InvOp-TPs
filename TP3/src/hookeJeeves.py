import matplotlib.pyplot as plt
import numpy as np
import concurrent.futures

from scipy.optimize import minimize_scalar
from numpy import dtype

from metodos import metodo, generar_instancias, W

class HookJeeves(metodo):
    def _iterar_coordenado(self, punto_inicial):
        dim = punto_inicial.shape[0]
        x_0 = punto_inicial
        for i in range(dim):
            ei = np.array([0 if j!=i else 1 for j in range(dim)])
            opt_result = minimize_scalar(lambda l: W(x_0 + l*ei, self._puntos, self._pesos))
            x_0 = x_0 + opt_result.x*ei
        return x_0

    def _iterar_desde_punto(self, punto_inicial):
        x_0 = punto_inicial
        while True:
            x_1 = self._iterar_coordenado(x_0)
            dif = x_1 - x_0
            opt_result = minimize_scalar(lambda l: W(x_1 + l*dif, self._puntos, self._pesos))
            x_1 = x_1 + opt_result.x * dif

            if np.all(np.isclose(x_0, x_1)):
                return x_1
            x_0 = x_1

if __name__ == "__main__":
    puntos, pesos = generar_instancias()
    h = HookJeeves(puntos, pesos)
    optimo = h.optimizar()
    print(optimo)
