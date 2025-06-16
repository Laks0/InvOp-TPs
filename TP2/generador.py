from random import sample, randint, random
import math
from itertools import product

n = 50
costo_repartidor = 5
dist_max = 100
min_dist_c = 5
max_dist_c = 75
min_costo_camion = 500
max_costo_camion = 1000
refrigerados = 1
exclusivos = 1

ids = [str(i) for i in range(1,n+1)]

print(n)
print(costo_repartidor)
print(dist_max)
print(refrigerados)
print("\n".join(sample(ids, refrigerados)))
print(exclusivos)
print("\n".join(sample(ids, exclusivos)))

alto, ancho = n * 6, n * 6

grilla = [(i, j) for i, j in product(range(alto), range(ancho))]

puntos = sample(grilla, n)

def distancia_euclideanda(x, y):
    return int(math.sqrt((x[0] - y[0])** 2 + (x[1] - y[1])** 2))

# Aseguro un ciclo
for i, c_1 in enumerate(puntos):
    j = (i + 1) % n
    c_2 = puntos[j]
    dist = distancia_euclideanda(c_1, c_2)
    costo = randint(min_costo_camion, max_costo_camion)
    print(f"{i} {j} {dist} {costo}")

for i, c_1 in enumerate(puntos):
    for j, c_2 in enumerate(puntos):
        if j <= i+1: continue
        if random() <= .4: continue
        dist = distancia_euclideanda(c_1, c_2)
        costo = randint(min_costo_camion, max_costo_camion)
        print(f"{i} {j} {dist} {costo}")

