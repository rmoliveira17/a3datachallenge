import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = pd.read_csv('antenas.txt', names= ['id_car', 'eta', 'x', 'y', 'duration'], delim_whitespace=True)

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

matrix_data_solution_allocation = np.zeros([100, 100])
quantidade_antenas = 0

for ia in statistics_treated:
    info = pd.read_excel('saida'+str(interval)+'.xlsx', sheet_name=str(ia))
    quantidade_antenas += info['val'].sum()
    for ia, ib in zip(info.x.to_list(), info.y.to_list()):
        matrix_data_solution_allocation[ia, ib] = info[(info.x == ia) & (info.y == ib)]['val'].iloc[0]


print("Quantidade de Antenas: ", quantidade_antenas)
fig, ax = plt.subplots()
im = ax.imshow(matrix_data_solution_allocation)
ax.set_title('Espalhamento de Antenas - Solução - WorkAREA='+str(interval))
plt.show()

