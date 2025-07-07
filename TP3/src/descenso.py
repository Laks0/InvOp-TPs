import numpy as np
from metodos import metodo, W, generar_instancias

# Gradiente de W
def DW(x, puntos, pesos):
    puntos_en_uso = puntos
    pesos_en_uso = pesos
    # Si es un punto, lo excluimos de la matriz de puntos para usar el diferencial
    #coincidencias = np.all(puntos == x, axis=1)
    coincidencias = np.linalg.norm(puntos - x, axis=1) < 1e-12
    if np.any(coincidencias):
        j = np.argmax(coincidencias)
        puntos_en_uso = np.delete(puntos, j, axis=0)
        pesos_en_uso = np.delete(pesos, j, axis=0)
    norma = 1/np.linalg.norm(x - puntos_en_uso, axis=1)
    return np.sum(np.diag(norma)@np.diag(pesos_en_uso)@(x-puntos_en_uso), axis=0)

class Descenso(metodo):
    def __init__(self, puntos, pesos, epsilon):
        metodo.__init__(self, puntos, pesos)
        self.epsilon = epsilon

    def _iterar_desde_punto(self, punto_inicial):
        x = punto_inicial
        while True:
            alpha = 1
            D = DW(x, self._puntos, self._pesos)

            if np.linalg.norm(D) < self.epsilon:
                return x

            while W(x - alpha * D, self._puntos, self._pesos) >= W(x, self._puntos, self._pesos) - .5 * alpha * (D @ D) and alpha > self.epsilon:
                alpha = alpha / 2
            
            if alpha <= self.epsilon:
                return x
            
            x = x - alpha * D
            #print(D[0])

if __name__ == "__main__":
    puntos, pesos = generar_instancias()
    print(DW(puntos[0]*10, puntos, pesos))
