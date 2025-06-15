from random import sample, randint, random

n = 20
costo_repartidor = 50
dist_max = 20
min_dist_c = 5
max_dist_c = 50
refrigerados = 5
exclusivos = 5

ids = [str(i) for i in range(1,n+1)]

print(n)
print(costo_repartidor)
print(dist_max)
print(refrigerados)
print("\n".join(sample(ids, refrigerados)))
print(exclusivos)
print("\n".join(sample(ids, exclusivos)))

ancho = dist_max * 10
alto = dist_max * 10

grilla = [(i%ancho, i//alto) for i in range(ancho*alto)]
puntos = sample(grilla, n)

# Aseguro un ciclo
for i, c_1 in enumerate(puntos):
    j = (i + 1) % n
    c_2 = puntos[j]
    dist = abs(c_2[0] - c_1[0]) + abs(c_2[1] - c_1[1])
    costo = randint(20, 100)
    print(f"{i} {j} {dist} {costo}")

for i, c_1 in enumerate(puntos):
    for j, c_2 in enumerate(puntos):
        if j <= i+1: continue
        if random() <= .4: continue
        dist = abs(c_2[0] - c_1[0]) + abs(c_2[1] - c_1[1])
        costo = randint(20, 100)
        print(f"{i} {j} {dist} {costo}")

