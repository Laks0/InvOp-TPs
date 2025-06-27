import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Cargar los datos
df = pd.read_csv("/home/santiago/Desktop/InvOp-TPs-master/TP2/test/resultados_modelos.csv")

# Mapear los nombres
nombre_modelos = {
    "tsp": "TSP",
    "repartidores": "MR",
    "cuatro_o_mas": "MR4",
    "exclusivos": "MRE"
}
orden_modelos = ["TSP", "MR", "MR4", "MRE"]

# Aplicar mapeo
df['modelo'] = df['modelo'].map(nombre_modelos)

# Agrupar y calcular el promedio
resumen = df.groupby(['tipo_distribucion', 'modelo'])['valor_objetivo'].mean().reset_index()
resumen['valor_objetivo'] = resumen['valor_objetivo'].round(2)

# Capitalizar nombres de tipo_distribucion
resumen['tipo_distribucion'] = resumen['tipo_distribucion'].str.capitalize()

# Guardar resumen en CSV
os.makedirs("test", exist_ok=True)
resumen.to_csv("test/resumen_agregado.csv", index=False)

# Graficar
sns.set(style="whitegrid")
plt.figure(figsize=(10, 6))
grafico = sns.barplot(
    data=resumen,
    x='tipo_distribucion',
    y='valor_objetivo',
    hue='modelo',
    order=sorted(resumen['tipo_distribucion'].unique()),
    hue_order=orden_modelos,
    palette='Set2'
)

plt.title("Promedio de valor objetivo por distribución y modelo", fontsize=14)
plt.xlabel("Tipo de distribución", fontsize=12)
plt.ylabel("Valor objetivo promedio", fontsize=12)
plt.xticks(rotation=0)
plt.legend(title="Modelo")

# Mostrar valores sobre las barras
for container in grafico.containers:
    grafico.bar_label(container, fmt='%.0f', label_type='edge', fontsize=9)

plt.tight_layout()
plt.savefig("/home/santiago/Desktop/InvOp-TPs-master/TP2/test/barras_costos.png", dpi=300)
plt.close()
