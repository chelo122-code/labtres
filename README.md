# labtres
# Ventana de Hanning

Tiene forma de campana y principalmente se usa para minimizar efectos no deseados cuando se analizan señales en el dominio de la frecuencia. Su objetivo principal es reducir las discontinuidades en los bordes de las señales al realizar la Transformada de Fourier. Sin una ventana, las señales pueden generar artefactos o errores llamados fugas espectrales, que aparecen cuando las señales no son periódicas y se cortan abruptamente. La ventana de Hanning suaviza esta transición.

# Uso general para utilizar el código

El código fue tomado a través de un AD620 por medio de una stm hacia una interfaz de Python que recopila los datos y los transforma a archivo tipo txt, de forma que este se descarga y se pone dentro del colab o se carga el archivo en la interfaz que utilices para que analice los datos ya tomados de antes. Los músculos analizados fueron el grupo flexor superficial de los dedos y el tierra se colocó en el codo, el movimiento realizado para obtener los datos fue tomar una pelota antiestrés para apretarla hasta fatigar el músculo.


En Python, al aplicar esta ventana de hanning a nuestros datos, los puntos extremos de la señal se atenúan suavemente a cero, lo que reduce los efectos de las discontinuidades.

También hay otras cosas a tener en cuenta respecto a cómo responde el músculo, su respuesta rápida y lenta:

La respuesta rápida del músculo está asociada a fibras de contracción rápida (fibras tipo II). Estas fibras se contraen rápidamente, son ideales para movimientos explosivos como correr a gran velocidad, saltar o levantar pesas. Sin embargo, se fatigan rápidamente porque utilizan energía de forma anaeróbica, es decir, sin oxígeno. Son perfectas para actividades de corta duración pero alta intensidad.

Por otro lado, la respuesta lenta está relacionada con fibras de contracción lenta (fibras tipo I). Estas fibras son más lentas para contraerse, pero tienen una gran resistencia a la fatiga. Son ideales para actividades de resistencia, como correr largas distancias, nadar o caminar. Utilizan energía de manera aeróbica, es decir, con oxígeno, lo que les permite trabajar durante mucho tiempo sin agotarse.

En este caso, las fibras que se están utilizando más con él movimiento realizado por la persona es con las fibras lentas porque el movimiento de sostener la pelota es repetitivo y sostenido.
