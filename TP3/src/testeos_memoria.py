import numpy as np
from hookeJeeves import HookeJeeves
from weiszfeld import Weiszfeld1
from descenso import Descenso
from metodos import generar_instancias_uniformes

# Parámetros
epsilon_parada = 1e-6

np.random.seed(1234)

N = 100_000

puntos, pesos = generar_instancias_uniformes(N, grid_size=N * 10, dimension=5)

m = Descenso(puntos, pesos, epsilon_parada)
x_opt = m.optimizar()