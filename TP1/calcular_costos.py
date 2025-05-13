# Ej 1
X_aviones = 500
X_vehiculos = 3000
X_kerosene = 6000

gasto_fijo_refinado = 5_000_000
gasto_fijo_fraccionado = 5_000_000
gasto_fijo_embalaje_aviones = 2_000_000
gasto_fijo_embalaje_vehiculos = 1_000_000
gasto_fijo_embalaje_kerosene = 500_000

# Ej 2

X_aviones = 0
gasto_fijo_embalaje_aviones = 0

# Ej 3
X_aviones = 0
gasto_fijo_embalaje_aviones = 0
X_vehiculos = 3000
X_kerosene = 7000
# costo_amortizado_refinado_aviones = 5000000 * ((10 * Xa) / (10 * Xa + 5 * Xv + 3 * Xk)) + 4100 * Xa

def costo_combustible_avion():
    gasto_refinado = gasto_fijo_refinado * ((10 * X_aviones) / (10 * X_aviones + 5 * X_vehiculos + 3 * X_kerosene)) + 4100 * X_aviones

    gasto_fraccionado = gasto_fijo_fraccionado * ((20 * X_aviones) / (20 * X_aviones + 10 * X_vehiculos + 6 * X_kerosene)) + 1000 * X_aviones

    gasto_embalaje = gasto_fijo_embalaje_aviones + 1000 * X_aviones

    gasto_materia_prima = 4000 * X_aviones

    return gasto_refinado + gasto_fraccionado + gasto_embalaje + gasto_materia_prima


def costo_combustible_vehiculo():
    gasto_refinado = gasto_fijo_refinado * ((5 * X_vehiculos) / (10 * X_aviones + 5 * X_vehiculos + 3 * X_kerosene)) + 3000 * X_vehiculos

    gasto_fraccionado = gasto_fijo_fraccionado * ((10 * X_vehiculos) / (20 * X_aviones + 10 * X_vehiculos + 6 * X_kerosene)) + 600 * X_vehiculos

    gasto_embalaje = gasto_fijo_embalaje_vehiculos + 500 * X_vehiculos

    gasto_materia_prima = 1000 * X_vehiculos

    return gasto_refinado + gasto_fraccionado + gasto_embalaje + gasto_materia_prima

def costo_combustible_kerosene():
    gasto_refinado = gasto_fijo_refinado * ((3 * X_kerosene) / (10 * X_aviones + 5 * X_vehiculos + 3 * X_kerosene)) + 1500 * X_kerosene

    gasto_fraccionado = gasto_fijo_fraccionado * ((6 * X_kerosene) / (20 * X_aviones + 10 * X_vehiculos + 6 * X_kerosene)) + 400 * X_kerosene

    gasto_embalaje = gasto_fijo_embalaje_kerosene + 400 * X_kerosene

    gasto_materia_prima = 500 * X_kerosene

    return gasto_refinado + gasto_fraccionado + gasto_embalaje + gasto_materia_prima

ganancia_avion = 6000 * X_aviones -     costo_combustible_avion()
ganancia_vehiculo = 8000 * X_vehiculos - costo_combustible_vehiculo()
ganancia_kerosene = 4000 * X_kerosene - costo_combustible_kerosene()


print("Ganancia avion:", ganancia_avion, "Costo avion: ", costo_combustible_avion())
print("Ganancia vehiculo:", ganancia_vehiculo, "Costo vehiculo: ", costo_combustible_vehiculo())
print("Ganancia kerosene:", ganancia_kerosene, "Costo kerosene: ", costo_combustible_kerosene())
print("Total: ", ganancia_avion + ganancia_kerosene + ganancia_vehiculo)
