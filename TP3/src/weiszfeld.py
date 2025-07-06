import matplotlib.pyplot as plt
import numpy as np
import concurrent.futures

from numpy import dtype

from metodos import metodo, generar_instancias

class Weiszfeld2(metodo):
    def _iterar_desde_punto(self, punto_inicial):
        """
        Aplica el algoritmo iterativo de Weiszfeld hasta satisfacer _criterio_de_parada.
        """
        puntos = self._puntos
        (_, dimension_puntos) = puntos.shape
        (dimension_punto_inicial, ) = punto_inicial.shape
        assert dimension_puntos == dimension_punto_inicial
        pesos_col = self._pesos.reshape(-1, 1)
        puntos_por_pesos = puntos * pesos_col
        x_0 = punto_inicial
        while True:
            norma_col = np.linalg.norm(x_0 - puntos, axis=1).reshape(-1, 1)
            dividendo = np.sum(puntos_por_pesos / norma_col, axis=0)
            divisor = np.sum(pesos_col / norma_col, axis=0)
            x_1 = dividendo / divisor
            if np.all(np.isclose(x_0, x_1)):
                break
            x_0 = x_1
        return x_0

    def _seleccionar_punto_inicial(self):
        puntos = self._puntos
        (cantidad_puntos, dimension_puntos) = puntos.shape
        pesos_col = self._pesos.reshape(-1, 1)

        def W_i(i):
            p_s = puntos[i, :]
            norma_col = np.linalg.norm(p_s - puntos, axis=1).reshape(-1, 1)
            W_i = np.sum(norma_col * pesos_col, axis=0)
            return W_i, i

        # Calcular todos los W_j en paralelo (por default usa la cantidad de CPUs de la computadora)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            resultados = list(executor.map(W_i, range(cantidad_puntos)))

        min_j = min(resultados, key=lambda x: x[0])[1]
        p_j = puntos[min_j, :]

        # Calculo R_j
        dividendo = pesos_col * (p_j - puntos)
        # Parche para hacer sum_i con i != j :)
        dividendo[min_j] = np.zeros(dimension_puntos)
        norma_p_j = np.linalg.norm(p_j - puntos, axis=1)
        norma_p_j[min_j] = 1 # En este punto el denominador de la división va a ser cero, es para evitar dividir por cero
        divisor = norma_p_j.reshape(-1, 1)
        R_j = np.sum(dividendo / divisor, axis=0)

        norma_R_j = np.linalg.norm(R_j)
        if norma_R_j <= pesos[min_j]:
            return True, p_j # p_j es óptimo, no es necesario aplicar el algoritmo

        # Calculo S(p_j)
        d_j = -(R_j / norma_R_j)
        dividendo = norma_R_j - pesos[min_j]

        w_j = pesos_col[min_j][0] # Todo sea para no copiar unos bytes en memoria...
        pesos_col[min_j] = 0.0
        # Acá sigue estando el parche que apliqué antes (para no dividir por cero en dist[j,j])
        divisor = np.sum(pesos_col / norma_p_j.reshape(-1, 1), axis=0)
        pesos_col[min_j] = w_j
        t_j = dividendo / divisor

        S_p_j = p_j + d_j * t_j

        return False, S_p_j # S_p_j no es óptimo, es necesario aplicar el algoritmo

    def optimizar(self):
        es_optimo, punto_inicial = self._seleccionar_punto_inicial()
        if not es_optimo:
            return self._iterar_desde_punto(punto_inicial)
        else:
            return punto_inicial

class Weiszfeld1(metodo):
    def _iterar_desde_punto(self, punto_inicial):
        """
        Aplica el algoritmo iterativo de Weiszfeld hasta satisfacer _criterio_de_parada.
        """
        puntos = self._puntos
        (cantidad_puntos, dimension_puntos) = puntos.shape
        (dimension_punto_inicial, ) = punto_inicial.shape
        assert dimension_puntos == dimension_punto_inicial
        pesos_col = self._pesos.reshape(-1, 1)
        puntos_por_pesos = puntos * pesos_col
        x_0 = punto_inicial

        def T(x):
            norma_col = np.linalg.norm(x - puntos, axis=1).reshape(-1, 1)
            dividendo = np.sum(puntos_por_pesos / norma_col, axis=0)
            divisor = np.sum(pesos_col / norma_col, axis=0)
            return dividendo / divisor

        def R(j, norma_p_j, mascara_i_dif_j):
            p_j = puntos[j,:]
            dividendo = (pesos_col * (p_j - puntos))[mascara_i_dif_j]
            divisor = norma_p_j[mascara_i_dif_j].reshape(-1, 1)
            R_j = np.sum(dividendo / divisor, axis=0)
            return R_j

        def S(j, R_j, norma_R_j, norma_p_j, mascara_i_dif_j):
            p_j = puntos[j,:]
            d_j = -(R_j / norma_R_j)
            dividendo = norma_R_j - pesos[j]
            norma_p_j_col = norma_p_j[mascara_i_dif_j].reshape(-1, 1)
            divisor = np.sum(pesos_col[mascara_i_dif_j] / norma_p_j_col, axis=0)
            t_j = dividendo / divisor
            return p_j + d_j * t_j

        while True:
            j = self._indice_de_x_en_puntos(x_0)
            if j is not None:
                # Esta máscara es para las sumas sobre i donde i != j
                mascara_i_dif_j = np.ones((cantidad_puntos,), dtype=np.bool)
                mascara_i_dif_j[j] = False
                p_j = puntos[j,:]
                norma_p_j = np.linalg.norm(p_j - puntos, axis=1)
                R_j = R(j, norma_p_j, mascara_i_dif_j)
                norma_R_j = np.linalg.norm(R_j)
                if norma_R_j <= pesos[j]:
                    x_1 = p_j
                else:
                    x_1 = S(j, R_j, norma_R_j, norma_p_j, mascara_i_dif_j)
            else:
                x_1 = T(x_0)
            if np.all(np.isclose(x_0, x_1)):
                break
            x_0 = x_1
        return x_0

    def _indice_de_x_en_puntos(self, x):
        """
        Retorna la fila i de _puntos donde x = puntos[i,:]. None si x no pertenece a _puntos.
        """
        indice = np.argwhere(np.all(np.isclose(x, self._puntos), axis=1) == True)
        try:
            return indice[0,0]
        except IndexError:
            return None

if __name__ == "__main__":
    puntos, pesos = generar_instancias()

    """
    w = Weiszfeld2(puntos, pesos)

    import time
    t0 = time.time()
    optimo = w.optimizar()
    t1 = time.time()
    print(t1-t0)

    
    plt.figure(figsize=(6, 6))
    plt.scatter(puntos[:, 0], puntos[:, 1], c='blue', label='Puntos', s=100)
    plt.scatter(optimo[0], optimo[1], c='red', label='Óptimo', s=200, marker='*')
    plt.grid(True)
    plt.xlim(0, grid_size)
    plt.ylim(0, grid_size)
    plt.title('Puntos y punto óptimo (primeras dos dimensiones)')
    plt.legend()
    plt.show()
    """
    w = Weiszfeld1(puntos, pesos)

    import time
    t0 = time.time()
    optimo = w.optimizar()
    t1 = time.time()
    print(t1-t0)
    print(optimo)

    """
    plt.figure(figsize=(50, 50))
    plt.scatter(puntos[:, 0], puntos[:, 1], c='blue', label='Puntos', s=100)
    plt.scatter(optimo[0], optimo[1], c='red', label='Óptimo', s=200, marker='*')
    plt.grid(True)
    plt.xlim(0, grid_size)
    plt.ylim(0, grid_size)
    plt.title('Puntos y punto óptimo (primeras dos dimensiones)')
    plt.legend()
    plt.show()
    """
