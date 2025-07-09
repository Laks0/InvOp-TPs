import numpy as np
from scipy.optimize import minimize_scalar
from metodos import metodo, generar_instancias, W

class HookeJeeves(metodo):
    def _iterar_coordenado(self, punto_inicial):
        dim = punto_inicial.shape[0]
        x_0 = punto_inicial
        for i in range(dim):
            ei = np.eye(dim)[i]
            opt_result = minimize_scalar(lambda l: W(x_0 + l*ei, self._puntos, self._pesos))
            x_0 = x_0 + opt_result.x*ei
        return x_0

    def _iterar_desde_punto(self, punto_inicial):
        x_0 = punto_inicial
        while True:
            self.contador_iteraciones += 1
            #self.recorrido.append(x_0)
            x_1 = self._iterar_coordenado(x_0)
            dif = x_1 - x_0
            opt_result = minimize_scalar(lambda l: W(x_1 + l*dif, self._puntos, self._pesos))
            x_1 = x_1 + opt_result.x * dif

            if np.linalg.norm(x_1 - x_0) < self.epsilon:
                #self.recorrido.append(x_1)
                return x_1
            x_0 = x_1

if __name__ == "__main__":
    puntos, pesos = generar_instancias()
    h = HookeJeeves(puntos, pesos)
    optimo = h.optimizar()
    print(optimo)
