import optuna
import pandas as pd

import numpy as np
import random

# importando dados

#Carga de dados
data = pd.read_csv('antenas.txt', names= ['id_car', 'eta', 'x', 'y', 'duration'], delim_whitespace=True)

#### TRATAMENTO ######

treating_sets = pd.DataFrame(data[['x', 'y', 'id_car']].groupby('id_car').value_counts()).query('x>= 70 and x<72 and y>= 44 and y<46')
sets = pd.DataFrame(set(treating_sets.index), columns=['id_car', 'x', 'y'])

#Parâmetros
duration_by_car = data[['x', 'y', 'id_car', 'duration']].query('x>= 70 and x<72 and y>= 44 and y<46')
duration_by_car_grouped = duration_by_car.groupby(by=['x', 'y', 'id_car']).sum()
total_duration_by_car = duration_by_car[['id_car', 'duration']].groupby(by='id_car').sum()
duration_by_car_index = duration_by_car.set_index(keys = ['x', 'y', 'id_car'])

a = 0.5
b = 0.3

#Conjuntos
cars = sets['id_car'].drop_duplicates()
x_coord = sets['x'].drop_duplicates()
y_coord = sets['y'].drop_duplicates()

# Definindo a função de avaliação
def objective(trial):
    duration_by_car_grouped['var'] = [trial.suggest_categorical('y'+str(ia), [0, 1]) for ia in range(len(duration_by_car_grouped))]
    x = pd.DataFrame({'var':trial.suggest_categorical('x'+str(i*j+j), [0, 1]) for i in range(len(x_coord)) for j in range(len(y_coord))}, index = pd.merge(x_coord, y_coord, how='cross').groupby(by=['x', 'y']).sum().index)
    y = duration_by_car_grouped['var']

    penalidade = 0

    # Segunda Restrição
    for i,j,c in y.index:
            if x.loc[(i,j), 'var'] - y.loc[(i,j,c)] != 0:
                penalidade += 1

    # Primeira Restrição
    for c in cars.to_list():
        for i, j in zip(duration_by_car.query('id_car==@c').x.to_list(),
                        duration_by_car.query('id_car==@c').y.to_list()):
            result = sum([sum(duration_by_car.query('x==@i and y==@j and id_car==@c')['duration']) * x.loc[(i,j), 'var']/total_duration_by_car.loc[c, 'duration']])
            if result < a:
                penalidade +=1

    # Terceira Restrição
    if sum([y.loc[(i,j,c)]/len(total_duration_by_car) for i,j,c in y.index]) < b:
        penalidade +=1

    # Função de otimização
    return sum(x['var']), penalidade


# Configurando o estudo do Optuna
seed = 128
n_startup_trials = 100
sampler = optuna.samplers.TPESampler(seed=10)

study = optuna.create_study(study_name='a3data', directions=['minimize', 'minimize'], sampler=sampler)

# Definindo a função fitness como a função objetivo
def fitness(trial):
    return objective(trial)


# Executando a otimização usando algoritmo genético
study.optimize(fitness, n_trials=10)

# Obtendo o melhor conjunto de hiperparâmetros
best_params = study.best_trials
print(f'Melhores hiperparâmetros encontrados: {best_params}')