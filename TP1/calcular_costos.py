# =============================================================================
# Ejercicio 1
# =============================================================================
X_aviones = 500
X_vehiculos = 3000
X_kerosene = 6000

gasto_fijo_refinado = 5_000_000
gasto_fijo_fraccionado = 5_000_000
gasto_fijo_embalaje_aviones = 2_000_000
gasto_fijo_embalaje_vehiculos = 1_000_000
gasto_fijo_embalaje_kerosene = 500_000

def costo_avion():
    def costo_combustible_avion():
        gasto_refinado = gasto_fijo_refinado * ((10 * X_aviones) / (10 * X_aviones + 5 * X_vehiculos + 3 * X_kerosene)) + 4100 * X_aviones
    
        gasto_fraccionado = gasto_fijo_fraccionado * ((20 * X_aviones) / (20 * X_aviones + 10 * X_vehiculos + 6 * X_kerosene)) + 1000 * X_aviones
    
        gasto_embalaje = gasto_fijo_embalaje_aviones + 1000 * X_aviones
    
        gasto_materia_prima = 4000 * X_aviones
    
        return gasto_refinado + gasto_fraccionado + gasto_embalaje + gasto_materia_prima
    
    return costo_combustible_avion()

def costo_vehiculo():
    def costo_combustible_vehiculo():
        gasto_refinado = gasto_fijo_refinado * ((5 * X_vehiculos) / (10 * X_aviones + 5 * X_vehiculos + 3 * X_kerosene)) + 3000 * X_vehiculos
    
        gasto_fraccionado = gasto_fijo_fraccionado * ((10 * X_vehiculos) / (20 * X_aviones + 10 * X_vehiculos + 6 * X_kerosene)) + 600 * X_vehiculos
    
        gasto_embalaje = gasto_fijo_embalaje_vehiculos + 500 * X_vehiculos
    
        gasto_materia_prima = 1000 * X_vehiculos
    
        return gasto_refinado + gasto_fraccionado + gasto_embalaje + gasto_materia_prima
    
    return costo_combustible_vehiculo()

def costo_kerosene():
    def costo_combustible_kerosene():
        gasto_refinado = gasto_fijo_refinado * ((3 * X_kerosene) / (10 * X_aviones + 5 * X_vehiculos + 3 * X_kerosene)) + 1500 * X_kerosene
    
        gasto_fraccionado = gasto_fijo_fraccionado * ((6 * X_kerosene) / (20 * X_aviones + 10 * X_vehiculos + 6 * X_kerosene)) + 400 * X_kerosene
    
        gasto_embalaje = gasto_fijo_embalaje_kerosene + 400 * X_kerosene
    
        gasto_materia_prima = 500 * X_kerosene
    
        return gasto_refinado + gasto_fraccionado + gasto_embalaje + gasto_materia_prima
    
    return costo_combustible_kerosene()


ganancia_avion = 16000 * X_aviones - costo_avion()
ganancia_vehiculo = 8000 * X_vehiculos - costo_vehiculo()
ganancia_kerosene = 4000 * X_kerosene - costo_kerosene()


print('-'*10 + 'Ejercicio 1' + '-'*10)

print("Ganancia avion:", ganancia_avion, "Costo avion: ", costo_avion())
print("Ganancia vehiculo:", ganancia_vehiculo, "Costo vehiculo: ", costo_vehiculo())
print("Ganancia kerosene:", ganancia_kerosene, "Costo kerosene: ", costo_kerosene())
print("Total: ", ganancia_avion + ganancia_kerosene + ganancia_vehiculo)

# =============================================================================
# Ejercicio 2
# =============================================================================
X_aviones = 0
gasto_fijo_embalaje_aviones = 0

ganancia_vehiculo = 8000 * X_vehiculos - costo_vehiculo()
ganancia_kerosene = 4000 * X_kerosene - costo_kerosene()


print('-'*10 + 'Ejercicio 2' + '-'*10)

print("Ganancia vehiculo:", ganancia_vehiculo, "Costo vehiculo: ", costo_vehiculo())
print("Ganancia kerosene:", ganancia_kerosene, "Costo kerosene: ", costo_kerosene())
print("Total: ", ganancia_kerosene + ganancia_vehiculo)

# =============================================================================
# Ejercicio 3
# =============================================================================
X_aviones = 0
gasto_fijo_embalaje_aviones = 0
X_vehiculos = 3000
X_kerosene = 7000

ganancia_vehiculo = 8000 * X_vehiculos - costo_vehiculo()
ganancia_kerosene = 4000 * X_kerosene - costo_kerosene()

print('-'*10 + 'Ejercicio 3' + '-'*10)

print("Ganancia vehiculo:", ganancia_vehiculo, "Costo vehiculo: ", costo_vehiculo())
print("Ganancia kerosene:", ganancia_kerosene, "Costo kerosene: ", costo_kerosene())
print("Total: ", ganancia_kerosene + ganancia_vehiculo)

# =============================================================================
# Ejercicio 4
# =============================================================================
X_aviones = 1000
X_vehiculos = 3000
X_kerosene = 4333.333333

gasto_fijo_refinado = 5_000_000
gasto_fijo_fraccionado = 5_000_000
gasto_fijo_embalaje_aviones = 2_000_000
gasto_fijo_embalaje_vehiculos = 1_000_000
gasto_fijo_embalaje_kerosene = 500_000

ganancia_avion = 16000 * X_aviones - costo_avion()
ganancia_vehiculo = 8000 * X_vehiculos - costo_vehiculo()
ganancia_kerosene = 4000 * X_kerosene - costo_kerosene()


print('-'*10 + 'Ejercicio 4' + '-'*10)

print("Ganancia avion:", ganancia_avion, "Costo avion (x1000 litros): ", costo_avion() /X_aviones)
print("Ganancia vehiculo:", ganancia_vehiculo, "Costo vehiculo (x1000 litros): ", costo_vehiculo() / X_vehiculos)
print("Ganancia kerosene:", ganancia_kerosene, "Costo kerosene (x1000 litros): ", costo_kerosene() / X_kerosene)
print("Total: ", ganancia_avion + ganancia_kerosene + ganancia_vehiculo)
