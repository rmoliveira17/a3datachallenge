
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from celluloid import Camera
from PIL import Image

#Carga de dados
data = pd.read_csv('antenas.txt', names= ['id_car', 'eta', 'x', 'y', 'duration'], delim_whitespace=True)

times = data.eta.drop_duplicates().sort_values().to_list()

# Distribuição de Carros ao longo do tempo

fig, ax = plt.subplots()
camera = Camera(fig)
k = 0

for t in times:
    selected_data_by_time = data[data.eta == t]
    data_divided_by_coordinates = selected_data_by_time[['x', 'y']].value_counts()
    matrix_data = np.ones([100,100])
    for ia in np.arange(0, 100):
        for ib in np.arange(0, 100):
            try:
                matrix_data[ia,ib] = data_divided_by_coordinates[(ia, ib)]
            except:
                matrix_data[ia,ib] = 0

    im = ax.imshow(matrix_data)
    ax.text(.15, 1.05, 'City Map - Time Behaviour - ' + str(t), transform=ax.transAxes)
    camera.snap()
    plt.close(fig)
    print(k)
    k += 1

animation = camera.animate()
animation.save('anim.gif', writer='pillow', fps=10)
