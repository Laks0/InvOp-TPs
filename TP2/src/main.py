#!venv/bin/python3.11
import os.path
import sys

from src.base import InstanciaRecorridoMixto
from src.modelos.modelo_repartidores import ModeloConRepartidores
from src.modelos.modelo_tsp import ModeloTSP
from src.modelos.variantes_con_repartidores import VarianteClientesExclusivos, VarianteRepartidorCuatroOMasClientes


def cargar_instancia():
    # El 1er parametro es el nombre del archivo de entrada
    nombre_archivo = sys.argv[1].strip()
    # Crea la instancia vacia
    instancia = InstanciaRecorridoMixto()
    # Llena la instancia con los datos del archivo de entrada
    instancia.leer_datos(nombre_archivo)
    return instancia


def main():
    # Lectura de datos desde el archivo de entrada
    instancia = cargar_instancia()

    # Definicion del problema de Cplex
    prob = VarianteRepartidorCuatroOMasClientes(instancia)

    mem_limit = lambda c: c.parameters.mip.limits.treememory.set(1024 * 32)  # 32GB
    tmp_dir = lambda c: c.parameters.workdir.set("/home/jorge/tmp/cplex")

    prob.resolver(mem_limit, tmp_dir)

    nombre_instancia = os.path.basename(sys.argv[1].strip())
    prob.mostrar_solucion(f"{nombre_instancia}_sin_exc.png")


if __name__ == '__main__':
    main()
