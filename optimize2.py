import pandas as pd
import numpy as np
from pulp import *

#Carga de dados
data = pd.read_csv('antenas.txt', names= ['id_car', 'eta', 'x', 'y', 'duration'], delim_whitespace=True)

#### TRATAMENTO ######

statistics = {}

data_grouped_by_locations = pd.DataFrame(data[['x', 'y']].groupby(by=['x', 'y']).value_counts())

interval = 15

for ic in np.arange(0, 100, interval):
    id = ic + interval
    for ia in np.arange(0, 100, interval):
        ib = ia + interval
        registros = data_grouped_by_locations.query('x>=@ic and x<@id and y>=@ia and y<@ib')
        quantidade_carros = data.query('x>=@ic and x<@id and y>=@ia and y<@ib')
        statistics[(ic, ia)] = {'ocorrencias':sum(registros['count']),
                                'carros': len(quantidade_carros['id_car'].drop_duplicates())}

statistics_treated = [ia for ia in statistics.keys() if statistics.get(ia)['carros']>1000]

solutions = {}
print(statistics_treated)

for m, n in statistics_treated:
    print(m,n)
    sup1 = m+interval
    sup2 = n+interval
    treating_sets = pd.DataFrame(data[['x', 'y', 'id_car']].groupby('id_car').value_counts()).query('x>= @m and x<@sup1 and y>=@n and y<@sup2')
    sets = pd.DataFrame(set(treating_sets.index), columns=['id_car', 'x', 'y'])

    #Parâmetros
    duration_by_car = data[['x', 'y', 'id_car', 'duration']].query('x>= @m and x<@sup1 and y>=@n and y<@sup2')
    duration_by_car_grouped = duration_by_car.groupby(by=['x', 'y', 'id_car']).sum()
    total_duration_by_car = duration_by_car[['id_car', 'duration']].groupby(by='id_car').sum()
    duration_by_car_index = duration_by_car.set_index(keys = ['x', 'y', 'id_car'])

    a = 0.5
    b = 0.3

    #Conjuntos
    cars = sets['id_car'].drop_duplicates()
    x_coord = sets['x'].drop_duplicates()
    y_coord = sets['y'].drop_duplicates()

    x = pulp.LpVariable.dicts('x', (x_coord.to_list(),y_coord.to_list() ), lowBound=0, upBound= 1,  cat='Integer')
    y = pulp.LpVariable.dicts('y',( x_coord,y_coord, cars), lowBound=0, upBound= 1,  cat='Integer')

    model = LpProblem("alocacao", LpMinimize)
    model += lpSum(x[i][j] for i in x_coord.to_list() for j in y_coord.to_list())

    # Restrição 1
    k = 0
    for c in cars.to_list():
            model += lpSum(duration_by_car_index.loc[(i, j, c), 'duration'] * y[i][j][c] for i , j in zip(duration_by_car.query('id_car==@c').x.to_list(), duration_by_car.query('id_car==@c').y.to_list()))/(total_duration_by_car.loc[c, 'duration']) >= a

    # Restrição 2
    model += lpSum( y[i][j][c] for i, j, c in duration_by_car_grouped.index)/len(total_duration_by_car) >= b

    # Restrição 3
    for c in cars.to_list():
            for i, j in zip(x_coord, y_coord):
                    model += lpSum(x[i][j]-y[i][j][c]) == 0

    model.solve()
    value(model.objective)
    aux = {}
    for ka in x_coord:
        for kb in y_coord:
            aux[(ka, kb)] = x[ka][kb].varValue

    solutions[(m,n)] = aux


#Output para pós-otimização - Excel

pd.DataFrame([]).to_excel('saida'+str(interval)+'.xlsx')

for m, n in statistics_treated:
    aa = pd.DataFrame({'x':[ia[0] for ia in solutions[(m, n)].keys()],
                       'y':[ia[1] for ia in solutions[(m, n)].keys()],
                       'val': solutions[(m, n)].values()})
    with pd.ExcelWriter('saida' + str(interval) + '.xlsx', engine='openpyxl', mode='a') as writer:
        aa.to_excel(writer, sheet_name='('+str(m)+', '+str(n)+')', index=False)

