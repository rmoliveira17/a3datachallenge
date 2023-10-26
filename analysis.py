import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

#Carga de dados
data = pd.read_csv('antenas.txt', names= ['id_car', 'eta', 'x', 'y', 'duration'], delim_whitespace=True)

# Estatística Não Paramétrica - Duração
duration_mean = data[['duration']].mean()
duration_std = data[['duration']].std()

# Tempo total de trabalho por carro
duration_by_car = data[['id_car', 'duration']].groupby('id_car').sum().query('duration > 50')
cars = duration_by_car.index
teste = pd.merge(data, duration_by_car, on='id_car')

# Média de duração de ocupação por coordenada
duration_mean_by_coordinates = data[['x','y', 'duration']].groupby(by=['x','y'])['duration'].mean()

# Histograma - Tempo em cada célula

frequency = dict(Counter(data.duration))
# frequency_normalized = {ia:ib for ia, ib in zip(frequency.keys(), list(map(lambda x: x/len(data.duration), frequency.values())))}
frequency_normalized = {ia:ib for ia, ib in zip(frequency.keys(), list(map(lambda x: np.log(x), frequency.values())))}
frequency_normalized_sorted = dict(sorted(frequency_normalized.items(), key = lambda x: x[0],reverse = False))
plt.figure(num='0')
plt.bar(list(frequency_normalized_sorted.keys()), list(frequency_normalized_sorted.values()))
plt.title('Histograma - Ocupação horária nas células')
plt.xlabel("tempo", fontsize=20)
plt.ylabel("log(carros) [un]", fontsize=20)

# Distribuição de Carros ao longo do período em estudo
grouped_data_by_coordinates = teste[['x', 'y']].value_counts()
matrix_data = np.ones([100,100])

for ia in np.arange(0, 100):
    for ib in np.arange(0, 100):
        try:
            matrix_data[ia,ib] = grouped_data_by_coordinates[(ia, ib)]
        except:
            matrix_data[ia,ib] = 0

fig, ax = plt.subplots()
im = ax.imshow(matrix_data)
ax.set_title('Espalhamento Acumulado de Carros - Período')
fig.colorbar(im, ax=ax, label='Concentração de Carros')

soma_linhas = {i:sum(matrix_data[i,:]) > 1000 for i in range(100)}
dropped_lines = [ia for ia, ib in soma_linhas.items() if not ib]
new_matrix = np.array([ia for ia,ib in zip(matrix_data, soma_linhas.values()) if ib])

soma_colunas = {j:sum(new_matrix.T[j,:]) > 1000 for j in range(100)}
drop_columns = [ia for ia, ib in soma_colunas.items() if not ib]
new_matrix = np.array([ia for ia, ib in zip(new_matrix.T, soma_colunas.values()) if ib])

fig, ax = plt.subplots()
im = ax.imshow(new_matrix.T)
ax.set_title('City Map')

fig.colorbar(im, ax=ax, label='Concentração de Carros')

# Carros na rua em cada unidade de tempo
plt.figure(num='2')
grouped_data_by_time = data[['eta']].value_counts().to_frame()
plt.plot(data['eta'].drop_duplicates().sort_values(), grouped_data_by_time.sort_values(by='eta')['count'].to_list())
plt.title('Série Temporal - Concentração de Carros')
plt.xlabel("tempo", fontsize=20)
plt.ylabel("carros [un]", fontsize=20)

#Carros entrando na célula por hora
plt.show()
print(data)