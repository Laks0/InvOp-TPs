import sys
from random import sample, random
import numpy as np
import math

def distancia_euclideanda(x, y):
    return int(math.sqrt((x[0] - y[0])** 2 + (x[1] - y[1])** 2))

def main():
    # El 1er parámetro es el nombre del archivo de entrada
    try:
        nombre_archivo = sys.argv[1].strip()
    except IndexError:
        raise RuntimeError("El primer argumento debe ser el archivo con los puntos")

    # El segundo parámetro es la proporción de refrigerados (default .4)
    try:
        p_refrigerados = float(sys.argv[2].strip())
    except IndexError:
        p_refrigerados = .4

    # El tercer parámetro es la proporción de exclusivos (default .1)
    try:
        p_exclusivos = float(sys.argv[3].strip())
    except IndexError:
        p_exclusivos = .1

    # El cuarto parámetro es el cuartil de los costos que se toma para el costo del repartidor
    try:
        c_costo = min(3, int(sys.argv[4].strip()))
    except IndexError:
        c_costo = 2

    # El quinto parámetro es el cuartil de las distancias que se toma para la distancia máxima del repartidor
    try:
        c_dist_max = min(3, int(sys.argv[5].strip()))
    except IndexError:
        c_dist_max = 2

    # El sexto parámetro es la probabilidad de que una arista no esté en el modelo
    try:
        chance_arista = float(sys.argv[6].strip())
    except IndexError:
        chance_arista = .6

    puntos = []
    with open(nombre_archivo) as f:
        lineas = [line.rstrip() for line in f]
        puntos = [[float(l.split(",")[0]),float(l.split(",")[1])] for l in lineas]

    indices = [i for i in range(len(puntos))]
    refrigerados = sample(indices, int(p_refrigerados * len(puntos)))
    exclusivos = sample(indices, int(p_exclusivos * len(puntos)))

    distancias = np.zeros( (len(puntos), len(puntos)) )
    costos = np.zeros( (len(puntos), len(puntos)) )
    for i, c_1 in enumerate(puntos):
        for j, c_2 in enumerate(puntos):
            distancias[i][j] = distancia_euclideanda(c_1, c_2)
            costos[i][j] = distancias[i][j] * (1+random()/2)

    dist_max = np.percentile(distancias, 25*c_dist_max)
    costo_repartidor = np.percentile(costos, 25*c_costo)

    print(len(puntos))
    print(int(costo_repartidor))
    print(int(dist_max))

    print(len(refrigerados))
    for i in refrigerados:
        print(i)

    print(len(exclusivos))
    for i in exclusivos:
        print(i)

    for i in range(len(puntos)):
        for j in range(i+1, len(puntos)):
            if j != i + 1 and random() > chance_arista:
                continue
            print(f"{i} {j} {int(distancias[i][j])} {int(costos[i][j])}")

if __name__ == "__main__":
    main()
