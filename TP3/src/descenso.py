import numpy as np
from metodos import metodo, W, generar_instancias_uniformes

# Gradiente de W
def DW(x, puntos, pesos):
    puntos_en_uso = puntos
    pesos_en_uso = pesos
    # Si es un punto, lo excluimos de la matriz de puntos para usar el diferencial
    #coincidencias = np.all(puntos == x, axis=1)
    coincidencias = np.linalg.norm(puntos - x, axis=1) < 1e-12
    no_cero = ~coincidencias
    puntos_en_uso = puntos[no_cero]
    pesos_en_uso = pesos[no_cero]
    norma = 1/np.linalg.norm(x - puntos_en_uso, axis=1)
    d_w = np.sum(np.diag(norma)@np.diag(pesos_en_uso)@(x-puntos_en_uso), axis=0)

    try:
        j = np.argwhere(puntos_en_uso == True)[0,0]
        # Caso x = p_j
        v_unit = np.random.random((puntos.shape[1]))
        v_unit /= np.linalg.norm(v_unit)
        d_w -= pesos[j] * v_unit
    except IndexError:
        pass # Caso x != p_j

    return d_w


class Descenso(metodo):
    def __init__(self, puntos, pesos, epsilon=1e-8):
        metodo.__init__(self, puntos, pesos, epsilon)
        self.epsilon_alpha = 1e-8

    def _iterar_desde_punto(self, punto_inicial):
        x_0 = punto_inicial
        while True:
            #self.recorrido.append(x_0)
            self.contador_iteraciones += 1
            alpha = 1
            D = DW(x_0, self._puntos, self._pesos)
            D_prod_D = D @ D
            W_x_0 = W(x_0, self._puntos, self._pesos)
    
            while W(x_0 - alpha * D, self._puntos, self._pesos) >= W_x_0 - 0.5 * alpha * D_prod_D and alpha > self.epsilon_alpha:
                alpha = alpha / 2
            
            x_1 = x_0 - alpha * D
    
            if np.linalg.norm(x_1 - x_0) < self.epsilon:
                #self.recorrido.append(x_1)
                return x_1
    
            x_0 = x_1

            #print(D[0])

if __name__ == "__main__":
    puntos, pesos = generar_instancias_uniformes()
    print(DW(puntos[0]*10, puntos, pesos))
