import time
import os
from hookeJeeves import HookeJeeves
from weiszfeld import Weiszfeld1
from descenso import Descenso
from metodos import generar_instancias, W, grafico_instancias_2d

if __name__ == "__main__":
    N = 300
    grid_size = 1000
    dimension = 2
    puntos, pesos = generar_instancias(N, grid_size, dimension)
    os.makedirs('figuras', exist_ok=True)
    if dimension == 2:
        grafico_instancias_2d(puntos, pesos, grid_size, 'figuras/contorno_W.png')
        
    epsilon_parada = 1e-6
     
    hj = HookeJeeves(puntos, pesos, epsilon_parada)
    t0 = time.time()
    opt_hj = hj.optimizar()
    t1 = time.time()
    
    print("Hooke Jeeves: ", t1-t0, " segundos")
    print("Iteraciones: ", hj.contador_iteraciones)
    print("Óptimo: ", W(opt_hj, puntos, pesos))
    print("Punto: ", opt_hj)
    if dimension == 2:
        grafico_instancias_2d(puntos, pesos, grid_size, 'figuras/recorrido_hj.png', hj.recorrido)
    print("-"*30)

    wz = Weiszfeld1(puntos, pesos, epsilon_parada)
    t0 = time.time()
    opt_wz = wz.optimizar()
    t1 = time.time()

    print("Weiszfeld: ", t1-t0, " segundos")
    print("Iteraciones: ", wz.contador_iteraciones)
    print("Óptimo: ", W(opt_wz, puntos, pesos))
    print("Punto: ", opt_wz)
    if dimension == 2:
        grafico_instancias_2d(puntos, pesos, grid_size, 'figuras/recorrido_wz.png', wz.recorrido)
    print("-"*30)
    
    dg = Descenso(puntos, pesos, epsilon_parada)
    t0 = time.time()
    opt_dg = dg.optimizar()
    t1 = time.time()

    print("Descenso de gradiente: ", t1-t0, " segundos")
    print("Iteraciones: ", dg.contador_iteraciones)
    print("Óptimo: ", W(opt_dg, puntos, pesos))
    print("Punto: ", opt_dg)
    if dimension == 2:
        grafico_instancias_2d(puntos, pesos, grid_size, 'figuras/recorrido_dg.png', dg.recorrido)
    print("-"*30)
    