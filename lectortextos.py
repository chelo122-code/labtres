import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

# Cargar los datos del archivo
data = np.loadtxt(r"C:\Users\joses\OneDrive\Escritorio\carpetajulian\Batman.txt", delimiter=',')


# Separar tiempo y amplitud
tiempo = data[:, 0]
amplitud = data[:, 1]

# Detectar picos
picos, _ = find_peaks(amplitud, height=0)  # Cambiar "height" según el umbral deseado

# Ventanas alrededor de cada pico
ventana = 0.01  # Ventana de 0.01 segundos (ajustar según sea necesario)
ventanas_picos = []

for pico in picos:
    idx_ini = np.where(tiempo >= (tiempo[pico] - ventana))[0][0]
    idx_fin = np.where(tiempo <= (tiempo[pico] + ventana))[0][-1]
    ventanas_picos.append((tiempo[idx_ini:idx_fin], amplitud[idx_ini:idx_fin]))

# Visualización de la señal completa y los picos detectados
plt.plot(tiempo, amplitud, label='Señal')
plt.plot(tiempo[picos], amplitud[picos], 'rx', label='Picos')
plt.xlabel('Tiempo (s)')
plt.ylabel('Amplitud (mV)')
plt.legend()
plt.show()
