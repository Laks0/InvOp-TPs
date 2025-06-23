#!/bin/bash

comando="python puntos_a_instancia.py $1"
archivo=$1
nombre="${archivo%.*}"

$comando 0.4 0.1 2 2 0.3 > instancias/$nombre\_ralo
$comando 0.4 0.1 2 2 0.9 > instancias/$nombre\_denso

$comando 0.7 > instancias/$nombre\_muchos_refrigerados
$comando 0.1 > instancias/$nombre\_pocos_refrigerados

$comando 0.4 0.8 > instancias/$nombre\_muchos_exclusivos
$comando 0.4 0.1 > instancias/$nombre\_pocos_exclusivos

$comando 0.4 0.1 1 2 > instancias/$nombre\_rep_barato
$comando 0.4 0.1 3 2 > instancias/$nombre\_rep_caro
$comando 0.4 0.1 2 3 > instancias/$nombre\_rep_largo
$comando 0.4 0.1 2 1 > instancias/$nombre\_rep_corto
$comando 0.4 0.1 1 3 > instancias/$nombre\_rep_largo_barato
$comando 0.4 0.1 3 1 > instancias/$nombre\_rep_corto_caro
$comando 0.4 0.1 3 1 > instancias/$nombre\_rep_caro_corto
$comando 0.4 0.1 1 3 > instancias/$nombre\_rep_barato_largo
