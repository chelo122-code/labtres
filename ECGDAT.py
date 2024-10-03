import sys
from PyQt6 import uic, QtCore, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QFileDialog, QLineEdit
from PyQt6.QtCore import *
from PyQt6.QtGui import *

import serial.tools.list_ports
import serial
import numpy as np
import struct

import threading

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from scipy.signal import butter, filtfilt

import datetime

class principal(QMainWindow):
    
    def __init__(self):
        super(principal, self).__init__()
        uic.loadUi("ECGD.ui", self)
        self.puertos_disponibles()
        
        self.ser1 = None
        
        self.connect.clicked.connect(self.conectar)
        
        self.guardarButton.clicked.connect(self.guardar_datos)
        self.cargarButton.clicked.connect(self.cargar_y_mostrar_datos)

        self.x = np.linspace(0, 10, 6000)
        self.y = np.linspace(0, 0, 6000)
    
        self.fig = Figure()
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvas(self.fig)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.graficawidget.setLayout(layout)

        self.fm = 1000  # Frecuencia de muestreo para EMG
        
        # Frecuencias de corte para el filtro pasa banda
        self.fc_baja = 20  # Pasa altos
        self.fc_alta = 450  # Pasa bajos

        # Normalización de frecuencias de corte
        self.fn_baja = self.fc_baja / (0.5 * self.fm)
        self.fn_alta = self.fc_alta / (0.5 * self.fm)

        # Orden del filtro
        self.orden = 4

        # Filtro pasa banda para EMG
        self.b, self.a = butter(self.orden, [self.fn_baja, self.fn_alta], btype='bandpass', analog=False)     

    def puertos_disponibles(self):
        p = serial.tools.list_ports.comports()
        for port in p:
            self.puertos.addItem(port.device)

    def conectar(self): 
        estado = self.connect.text()
        self.stop_event_ser1 = threading.Event()
        if estado == "CONECTAR":
            com = self.puertos.currentText()
            try:
                self.ser1 = serial.Serial(com, 115200)
                self.hilo_ser1 = threading.Thread(target=self.periodic_thread1)
                self.hilo_ser1.start()
                print("Puerto serial 1 Conectado")
                self.connect.setText("DESCONECTAR")

            except serial.SerialException as e:
                print("Error en el puerto serial 1: ", e)
        else:
            self.ser1.close()
            self.stop_event_ser1.set()
            self.hilo_ser1.join()
            print("Puerto serial 1 Desconectado")
            self.connect.setText("CONECTAR")

    def periodic_thread1(self):
        if self.ser1 is not None and self.ser1.is_open:
            data = self.ser1.read(50)
            if len(data) == 50:
                data = struct.unpack('50B', data)
                for i in range(0, len(data), 2):
                    self.y = np.roll(self.y, -1)
                    self.y[-1] = data[i] * 100 + data[i + 1]

                self.ax.clear()

                # Aplicar el filtro pasa banda
                df = filtfilt(self.b, self.a, self.y)

                # Graficar la señal filtrada
                self.ax.plot(self.x, df)
                self.ax.grid(True)
                self.canvas.draw()

        if not self.stop_event_ser1.is_set():
            threading.Timer(1e-3, self.periodic_thread1).start()

    def guardar_datos(self):
        try:
            now = datetime.datetime.now()
            fecha_hora = now.strftime("%Y-%m-%d %H:%M:%S")
            nombre_persona = self.nombre_persona.text()
            nombre_persona = nombre_persona.replace(":", "").replace(" ", "_")
            nombre_archivo = f"{nombre_persona}.txt"

            # Aplicar el filtro a la señal actual antes de guardarla
            df = filtfilt(self.b, self.a, self.y)

            # Guardar la señal filtrada en el archivo
            with open(nombre_archivo, 'w') as f:
                f.write(f"Fecha y hora: {fecha_hora}\n")
                f.write(f"Nombre del paciente: {nombre_persona}\n")
                f.write("Datos filtrados de la medición:\n")
                for i in range(len(self.x)):
                    f.write(f"{self.x[i]}, {df[i]}\n")  # Guardar los datos filtrados

            print(f"Datos filtrados guardados en {nombre_archivo}")

        except Exception as e:
            print("Error al guardar los datos:", e)

    def cargar_datos(self, nombre_archivo):
        try:
            x = []
            y = []

            with open(nombre_archivo, 'r') as f:
                for _ in range(4):
                    next(f)

                for line in f:
                    datos = line.strip().split(",")
                    x.append(float(datos[0]))
                    y.append(float(datos[1]))
            return x, y

        except Exception as e:
            print("Error al cargar los datos:", e)
            return None, None

    def detectar_pulsos(self, señal, umbral):
        """
        Detectar segmentos de pulsos EMG en la señal basada en un umbral.
        """
        pulsos = []
        en_pulso = False
        inicio_pulso = 0

        for i in range(len(señal)):
            if señal[i] > umbral and not en_pulso:
                en_pulso = True
                inicio_pulso = i
            elif señal[i] < umbral and en_pulso:
                en_pulso = False
                fin_pulso = i
                pulsos.append((inicio_pulso, fin_pulso))
        
        return pulsos

    def aplicar_ventana_hanning_por_pulsos(self, y, pulsos):
        """
        Aplica una ventana de Hanning a cada pulso detectado en la señal.
        """
        señal_filtrada = np.zeros_like(y)
        
        for inicio, fin in pulsos:
            ventana_hanning = np.hanning(fin - inicio)
            señal_filtrada[inicio:fin] = y[inicio:fin] * ventana_hanning
        
        return señal_filtrada

    def cargar_y_mostrar_datos(self):
        nombre_archivo, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo", "", "Archivos de texto (*.txt)")
        if nombre_archivo:
            x, y = self.cargar_datos(nombre_archivo)
            if x and y:
                self.x = x
                self.y = y

                # Detectar pulsos en la señal
                umbral = 20  # Definir un umbral adecuado para la detección de pulsos
                pulsos = self.detectar_pulsos(self.y, umbral)

                # Aplicar la ventana de Hanning por pulsos
                y_filtrada = self.aplicar_ventana_hanning_por_pulsos(self.y, pulsos)

                # Limpiar la gráfica antes de dibujar
                self.ax.clear()

                # Graficar la señal original
                self.ax.plot(self.x, self.y, label="Original")

                # Graficar la señal con la ventana de Hanning aplicada a los pulsos
                self.ax.plot(self.x, y_filtrada, label="Hanning Window Pulsos", linestyle="--")
                nombre_archivo1 = f"Batman.txt"
                with open(nombre_archivo1, 'w') as f:
                    for i in range(len(self.x)):
                        f.write(f"{self.x[i]}, {y_filtrada[i]}\n")  # Guardar los datos filtrados

                # Añadir etiquetas, título y leyenda
                self.ax.set_xlabel('Tiempo')
                self.ax.set_ylabel('amplitud (mV)')
                self.ax.set_title('Datos con Ventana de Hanning en Pulsos')
                self.ax.legend()

                # Refrescar el canvas para mostrar la gráfica
                self.canvas.draw()
                print("Datos cargados y mostrados desde", nombre_archivo)
            else:
                print("No se pudieron cargar los datos desde", nombre_archivo)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = principal()
    ventana.show()
    sys.exit(app.exec())


