#!/bin/bash
instancias=$(ls instancias)

for i in $instancias; do
	venv/bin/python tsp.py instancias/$i
	venv/bin/python sin_exc.py instancias/$i
	venv/bin/python con_exc.py instancias/$i
	echo "Terminado $i"
done
