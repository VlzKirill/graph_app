from flask import Flask, render_template, request
import json
import matplotlib.pyplot as plt
import os
import base64
from io import BytesIO
import matplotlib


app = Flask(__name__)

matplotlib.use('Agg')

BENCHMARKS_FOLDER = 'C:\\Users\\Пользователь\\Desktop\\benchmarks'

def read_json_files(folder_path):
    data = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    data.append(json.load(f))
    return data

def get_unique_benchmark_names(data):
    unique_names = set()
    for entry in data:
        benchmarks = entry.get("benchmarks", [])
        for benchmark in benchmarks:
            name = benchmark["name"]
            if name.endswith("real_time_mean"):
                name = name.replace("/real_time_mean", "")
                unique_names.add(name)
    return list(unique_names)

def create_static_folder():
    static_folder = 'static'
    if not os.path.exists(static_folder):
        os.makedirs(static_folder)

def plot_graph(data, selected_name):
    x_values = []
    y_values = []

    for entry in data:
        version = entry["version"]["values"][0]
        benchmarks = entry.get("benchmarks", [])

        for benchmark in benchmarks:
            if benchmark["name"] == selected_name:
                x_values.append(version)
                y_values.append(benchmark["bytes_per_second"])

    fig, ax = plt.subplots()
    ax.plot(x_values, y_values, marker='o')
    ax.set_xlabel('Версия')
    ax.set_ylabel('Значение bytes_per_second')
    ax.set_title(f'График для {selected_name}')
    ax.grid(True)

    img_buf = BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)

    graph_data = base64.b64encode(img_buf.getvalue()).decode('utf-8')

    plt.close(fig)

    return graph_data

def plot_summary_graph(data, unique_names):
    fig, ax = plt.subplots(figsize=(10, 6))  # Устанавливаем начальный размер графика

    for i, unique_name in enumerate(unique_names):
        unique_name = f"{unique_name}/real_time_mean"
        x_values = []
        y_values = []
        for entry in data:
            version = entry["version"]["values"][0]
            benchmarks = entry.get("benchmarks", [])

            for benchmark in benchmarks:
                if benchmark["name"] == unique_name:
                    x_values.append(version)
                    y_values.append(benchmark["bytes_per_second"])

        # Используем уникальный цвет для каждого бенчмарка
        color = plt.cm.viridis(i / len(unique_names))

        ax.plot(x_values, y_values, marker='o', label=unique_name, color=color)

    ax.set_xlabel('Версия')
    ax.set_ylabel('Значение bytes_per_second')
    ax.set_title('Сводный график')
    ax.grid(True)
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), fancybox=True, shadow=True, ncol=3)  # Добавляем легенду

    img_buf = BytesIO()
    plt.savefig(img_buf, format='png', bbox_inches='tight')  # bbox_inches='tight' убирает отсечение графика при сохранении
    img_buf.seek(0)

    graph_data = base64.b64encode(img_buf.getvalue()).decode('utf-8')

    plt.close(fig)

    return graph_data


@app.route('/')
def index():
    data = read_json_files(BENCHMARKS_FOLDER)
    unique_names = get_unique_benchmark_names(data)
    return render_template('index.html', unique_names=unique_names, selected_name=None)

@app.route('/plot', methods=['POST'])
def plot():
    selected_name = f"{request.form['selected_name']}/real_time_mean"
    data = read_json_files(BENCHMARKS_FOLDER)
    graph_data = plot_graph(data, selected_name)
    return render_template('index.html', unique_names=get_unique_benchmark_names(data), selected_name=selected_name,
                           graph_data=graph_data)

@app.route('/summary', methods=['GET'])
def summary():
    data = read_json_files(BENCHMARKS_FOLDER)
    unique_names = get_unique_benchmark_names(data)
    summary_graph_data = plot_summary_graph(data, unique_names)
    return render_template('index.html', unique_names=unique_names,
                           selected_name=None, graph_data=None, summary_graph_data=summary_graph_data)

if __name__ == '__main__':
    app.run(debug=True)
