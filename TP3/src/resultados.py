import time
import os
import pandas as pd
from memory_profiler import memory_usage
from hookeJeeves import HookeJeeves
from weiszfeld import Weiszfeld1
from descenso import Descenso
from metodos import generar_instancias, W

# Parámetros
grupos_nodos = [10, 50, 100, 250, 500, 1000]
replicas = 30
epsilon_parada = 1e-6


resultados = []
os.makedirs('figuras', exist_ok=True)

for N in grupos_nodos:
    for run in range(1, replicas + 1):
        # Generar instancias
        puntos, pesos = generar_instancias(N, grid_size=N*10, dimension=2)

        # Métodos a evaluar
        metodos = [
            ('HookeJeeves', HookeJeeves(puntos, pesos, epsilon_parada)),
            ('Weiszfeld1', Weiszfeld1(puntos, pesos, epsilon_parada)),
            ('Descenso', Descenso(puntos, pesos, epsilon_parada)),
        ]

        for nombre, instancia in metodos:
            # Medir memoria pico y tiempo de optimizar()
            def ejecutar():
                return instancia.optimizar()

            # Memoria (MB) medida con memory_profiler
            mem_peak = memory_usage((ejecutar, ), max_usage=True)

            t0 = time.time()
            x_opt = instancia.optimizar()
            t1 = time.time()

            # Recopilar datos
            resultados.append({
                'metodo': nombre,
                'nodos': N,
                'num_de_instancia': run,
                'tiempo_s': t1 - t0,
                'memoria_pico_MB': mem_peak,
                'iteraciones': instancia.contador_iteraciones,
                'valor_objetivo': W(x_opt, puntos, pesos),
            })

# Guardar resultados a CSV
df = pd.DataFrame(resultados)
csv_path = 'resultados.csv'
df.to_csv(csv_path, index=False)
