from flask import Flask, render_template, request
import os
import json
import matplotlib.pyplot as plt

app = Flask(__name__)

# Функция для считывания данных из JSON файлов
def read_json_files(folder_path):
    data = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    data.append(json.load(f))
    return data

# Функция для получения уникальных значений benchmarks.name
def get_unique_benchmark_names(data):
    unique_names = set()
    for entry in data:
        benchmarks = entry.get("benchmarks", [])
        for benchmark in benchmarks:
            name = benchmark["name"]
            if name.endswith("real_time_mean"):
                unique_names.add(name)
    return list(unique_names)

# Функция для построения графика
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

    plt.plot(x_values, y_values, marker='o')
    plt.xlabel('Версия')
    plt.ylabel('Значение bytes_per_second')
    plt.title(f'График для {selected_name}')
    plt.grid(True)
    plt.savefig('static/graph.png')  # Сохраняем график как изображение

# Роут для отображения главной страницы
@app.route('/')
def index():
    folder_path = 'C:\\Users\\Пользователь\\Desktop\\benchmarks'
    data = read_json_files(folder_path)
    unique_names = get_unique_benchmark_names(data)
    return render_template('index.html', unique_names=unique_names, selected_name=None)

# Роут для обработки выбора значения из выпадающего списка
@app.route('/plot', methods=['POST'])
def plot():
    selected_name = request.form['selected_name']
    folder_path = 'C:\\Users\\Пользователь\\Desktop\\benchmarks'
    data = read_json_files(folder_path)
    plot_graph(data, selected_name)
    return render_template('index.html', unique_names=get_unique_benchmark_names(data), selected_name=selected_name)


if __name__ == '__main__':
    app.run(debug=True)