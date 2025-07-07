import time
from hookeJeeves import HookeJeeves
from weiszfeld import Weiszfeld1
from metodos import generar_instancias, W

if __name__ == "__main__":
    puntos, pesos = generar_instancias()

    hj = HookeJeeves(puntos, pesos)
    t0 = time.time()
    opt_hj = hj.optimizar()
    t1 = time.time()

    print("Hooke Jeeves: ", t1-t0)
    print("optimo: ", W(opt_hj, puntos, pesos))
    print("-"*30)

    wz = Weiszfeld1(puntos, pesos)
    t0 = time.time()
    opt_wz = wz.optimizar()
    t1 = time.time()

    print("Weiszfeld: ", t1-t0)
    print("optimo: ", W(opt_wz, puntos, pesos))
    print("-"*30)
