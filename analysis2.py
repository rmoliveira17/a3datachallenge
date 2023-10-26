import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import statsmodels.api as sm
from collections import Counter

#Carga de dados
data = pd.read_csv('antenas.txt', names= ['id_car', 'eta', 'x', 'y', 'duration'], delim_whitespace=True)

statistics = {}

data_grouped_by_locations = pd.DataFrame(data[['x', 'y']].groupby(by=['x', 'y']).value_counts())
for ic in np.arange(0, 100, 10):
    id = ic + 5
    for ia in np.arange(0, 100, 5):
        ib = ia + 5
        registros = data_grouped_by_locations.query('x>=@ic and x<@id and y>=@ia and y<@ib')
        quantidade_carros = data.query('x>=@ic and x<@id and y>=@ia and y<@ib')
        statistics[(ic, ia)] = {'ocorrencias':sum(registros['count']),
                                'carros': len(quantidade_carros['id_car'].drop_duplicates())}

# Estatistica de ocorrencias

ocorrencias_carros = pd.DataFrame(statistics.values(), index = statistics.keys())
plt.scatter(ocorrencias_carros.carros, ocorrencias_carros.ocorrencias)
correlacao = ocorrencias_carros.corr()

# Regressão Linear
ax= sns.lmplot(x='ocorrencias', y='carros', data=ocorrencias_carros)
plt.show()

resultado_regressao = sm.OLS(ocorrencias_carros.ocorrencias, sm.add_constant(ocorrencias_carros.carros)).fit()
# print(resultado_regressao.summary())

# Estatistica para Otimização

# Quem eu vou otimizar?
# Otimizamar workareas com mais de 1000 ocorrencias e mais de 100 carros

statistics_df = pd.DataFrame(statistics.values(), index = statistics.keys())
regions_to_optimize = list(statistics_df.query('ocorrencias > 1000 and carros> 100').index)

# Tratamento para otimização

treating_sets = pd.DataFrame(data[['x', 'y', 'id_car']].groupby('id_car').value_counts()).query('x>= 40 and x<50 and y>= 40 and y<50')
sets = pd.DataFrame(set(treating_sets.index), columns=['id_car', 'x', 'y'])

cars = sets['id_car'].drop_duplicates()
x_coord = sets['x'].drop_duplicates()
y_coord = sets['y'].drop_duplicates()

a =1

