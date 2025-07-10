import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

files_to_load = [
    {'file_path': '/home/jorge/oldhome/Documents/UBA/Carrera/1C2025/InvOp/InvOp-TPs/TP3/src/experimentos_grilla_densa/resultados_R3.csv', 'name': 'Clusters R^3'},
    {'file_path': '/home/jorge/oldhome/Documents/UBA/Carrera/1C2025/InvOp/InvOp-TPs/TP3/src/experimentos_grilla_densa/resultados_R10.csv', 'name': 'Clusters R^10'},
    {'file_path': '/home/jorge/oldhome/Documents/UBA/Carrera/1C2025/InvOp/InvOp-TPs/TP3/src/experimentos_uniforme_grilla_grande/resultados_R3.csv', 'name': 'Uniforme R^3'},
    {'file_path': '/home/jorge/oldhome/Documents/UBA/Carrera/1C2025/InvOp/InvOp-TPs/TP3/src/experimentos_uniforme_grilla_grande/resultados_R10.csv', 'name': 'Uniforme R^10'},
]

all_data = []

for file_info in files_to_load:
    df = pd.read_csv(file_info['file_path'])
    df['source'] = file_info['name']
    all_data.append(df)

combined_df = pd.concat(all_data, ignore_index=True)

methods = combined_df['metodo'].unique()

for method in methods:
    plt.figure(figsize=(12, 6))

    method_df = combined_df[combined_df['metodo'] == method]

    avg_time_df = method_df.groupby(['nodos', 'source'])['tiempo_s'].mean().reset_index()

    unique_nodes = sorted(avg_time_df['nodos'].unique())

    sns.lineplot(data=avg_time_df, x='nodos', y='tiempo_s', hue='source', marker='o', palette='viridis')


    plt.title(f'Tiempo de ejecución promedio para el método: {method}', fontsize=16)
    plt.xlabel('Cantidad de Nodos', fontsize=12)
    plt.ylabel('Tiempo promedio (s)', fontsize=12)
    plt.xticks(ticks=unique_nodes)

    plt.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.legend(title='Tipo de Experimento')
    plt.tight_layout()

    plot_filename = f'{method}_runtime_plot.png'
    plt.savefig(plot_filename)
    plt.close()

    g = sns.FacetGrid(combined_df, col="source", col_wrap=2, hue="metodo", height=5, aspect=1.2, sharey=False)
    g.map(sns.lineplot, "nodos", "tiempo_s", marker="o")

    unique_nodes = sorted(combined_df['nodos'].unique())
    g.set(xticks=unique_nodes)

    g.set_titles(col_template="{col_name}", size=14)
    g.set_axis_labels("Cantidad de Nodos", "Tiempo promedio (s)")
    g.add_legend(title="Método")

    plt.tight_layout()
    plt.savefig("faceted_comparison_plot.png")

