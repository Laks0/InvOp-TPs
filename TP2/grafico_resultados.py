import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

df = pd.read_csv("/home/santiago/Desktop/InvOp-TPs-master/TP2/test/resultados_modelos.csv")

# Paleta personalizada para modelos
colores_modelos = {
    "TSP": "#66c2a5",   # verde
    "MR": "#fc8d62",    # naranja
    "MR4": "#8da0cb",   # azul
    "MRE": "#e78ac3"    # rosa
}

# Mapear los nombres de los modelos
nombre_modelos = {
    "tsp": "TSP",
    "repartidores": "MR",
    "cuatro_o_mas": "MR4",
    "exclusivos": "MRE"
}
orden_modelos = ["TSP", "MR", "MR4", "MRE"]

df['modelo'] = df['modelo'].map(nombre_modelos)

# Promedio de valores objetivos por tipo de distribución y modelo
resumen = df.groupby(['tipo_distribucion', 'modelo'])['valor_objetivo'].mean().reset_index()
resumen['valor_objetivo'] = resumen['valor_objetivo'].round(2)
resumen['tipo_distribucion'] = resumen['tipo_distribucion'].str.capitalize()

# Guardar resumen CSV
os.makedirs("test", exist_ok=True)
resumen.to_csv("test/resumen_agregado.csv", index=False)

# Gráfico de promedios
sns.set(style="whitegrid")
plt.figure(figsize=(6, 4))
grafico = sns.barplot(
    data=resumen,
    x='tipo_distribucion',
    y='valor_objetivo',
    hue='modelo',
    order=sorted(resumen['tipo_distribucion'].unique()),
    hue_order=orden_modelos,
    palette=colores_modelos
)

#plt.title("Promedio de valor objetivo por distribución y modelo", fontsize=14)
plt.xlabel("Tipo de distribución", fontsize=12)
plt.ylabel("Valor objetivo promedio", fontsize=12)
plt.xticks(rotation=0)
plt.legend(title="Modelo")

for container in grafico.containers:
    grafico.bar_label(container, fmt='%.0f', label_type='edge', fontsize=9)

plt.tight_layout()
plt.savefig("/home/santiago/Desktop/InvOp-TPs-master/TP2/informe/figuras/barras_costos.png", dpi=300)
plt.close()

# === Análisis de diferencia porcentual respecto a TSP por instancia ===

# Pivotear para tener una fila por instancia con columnas por modelo
pivot = df.pivot_table(index=['tipo_distribucion', 'instancia_id'], columns='modelo', values='valor_objetivo').reset_index()

# Calcular diferencias porcentuales respecto a TSP
for modelo in ['MR', 'MR4', 'MRE']:
    pivot[f'diff_{modelo}'] = ((pivot[modelo] - pivot['TSP']) / pivot['TSP']) * 100

# Reunir en formato largo para graficar
diferencias = pivot.melt(
    id_vars=['tipo_distribucion'],
    value_vars=['diff_MR', 'diff_MR4', 'diff_MRE'],
    var_name='modelo',
    value_name='diferencia_pct'
)

# Limpiar nombres de modelo
diferencias['modelo'] = diferencias['modelo'].str.replace('diff_', '')

# Calcular promedio de diferencias por tipo y modelo
resumen_dif = diferencias.groupby(['tipo_distribucion', 'modelo'])['diferencia_pct'].mean().reset_index()
resumen_dif['diferencia_pct'] = resumen_dif['diferencia_pct'].round(1)
resumen_dif['tipo_distribucion'] = resumen_dif['tipo_distribucion'].str.capitalize()

# === Gráfico de diferencias porcentuales ===
plt.figure(figsize=(6, 4))
grafico2 = sns.barplot(
    data=resumen_dif,
    x='tipo_distribucion',
    y='diferencia_pct',
    hue='modelo',
    order=sorted(resumen_dif['tipo_distribucion'].unique()),
    hue_order=['MR', 'MR4', 'MRE'],
    palette=colores_modelos
)

#plt.title("Diferencia porcentual promedio respecto a TSP", fontsize=14)
plt.xlabel("Tipo de distribución", fontsize=12)
plt.ylabel("Diferencia porcentual (%)", fontsize=12)
plt.xticks(rotation=0)
plt.legend(title="Modelo")

for container in grafico2.containers:
    grafico2.bar_label(container, fmt='%.1f%%', label_type='edge', fontsize=9)

plt.tight_layout()
plt.savefig("/home/santiago/Desktop/InvOp-TPs-master/TP2/informe/figuras/barras_diferencias_pct.png", dpi=300)
plt.close()
