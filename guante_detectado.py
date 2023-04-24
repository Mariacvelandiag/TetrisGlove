#--------------------------------------------------------------------------
#------- -------------CÓDIGO ----------------------------------------------
#-------Conceptos básicos de PDI-------------------------------------------
#-------Por: María Camila Velandia García    mariac.velandiag@udea.edu.co--
#-------Estudiante de Maestría en Ingeniría--------------------------------
#-------CC 1017252095,  Wpp 3117318160-------------------------------------
#-------Curso Básico de Procesamiento de Imágenes y Visión Artificial------
#------- V2 Abril de 2023-1------------------------------------------------
#--------------------------------------------------------------------------

#--------------------------------------------------------------------------
#--1. Inicializo el sistema -----------------------------------------------
#--------------------------------------------------------------------------

#---- Se importan las librerias necesarias---------------------------------
import cv2
import math
import numpy as np

#---- Lee la webcam
cap = cv2.VideoCapture(0)

# Definir el rango de color amarillo en HSV
low_yellow = np.array([20, 100, 100], np.uint8)
high_yellow = np.array([30, 255, 255], np.uint8)
count = [0, 0]          

#--------------------------------------------------------------------------
#-----Funciones------------------------------------------------------------
#--------------------------------------------------------------------------

#---Lee la webcam y retorna la version de la camara, invertida horizontalmente
def capture():

    ret, frame = cap.read()    
    return cv2.flip(frame, 1)


def yellow_glove(frame):

    global count # declarar la variable count con ámbito global, lo que permite
    #acceder a ella o modificarla desde fuera de la función en la que se definió.
    accion = 0 #inicializa la variable con un valor numerico 0
    kernel = np.ones((3, 3), np.uint8) #matriz para operacion de dilatacion

    # Se pasa la imagen al espacio de color HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Deteccion del color amarillo
    mask = cv2.inRange(hsv, low_yellow, high_yellow)
    # Operacion de dilatacion
    mask = cv2.dilate(mask, kernel, iterations=1)
    
    # Reducir el ruido de La imagen y obtener bordes más suaves
    mask = cv2.GaussianBlur(mask, (5, 5), 100)

    # Se obtienen contornos(son arreglos numoy)
    contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # obtiene centroides de buen tamaño mayores a 3000
    x, y, area = 0, 0, 0

    if len(contours) != 0:

        # Encontrar el contorno de area maxima(mano)
        cnt = max(contours, key=lambda x: cv2.contourArea(x))
        area = cv2.contourArea(cnt)
        if area > 3000:
            # calcula los momentos del contorno 
            M = cv2.moments(cnt)
            if M["m00"] == 0:
                M["m00"] = 1            
            # Se calcula la posición del centroide a partir de los momentos obtenidos
            x = int(M["m10"] / M["m00"])
            y = int(M['m01'] / M['m00'])
            # Se dibuja un circulo en donde está ubicado el centroide
            cv2.circle(frame, (x, y), 7, (0, 0, 250), 1)
            # Se define la fuente de la letra con la que se escribirá en pantalla
            font = cv2.FONT_HERSHEY_SIMPLEX
            # Se agrega a la imagen de salida las coordenadas del centroide y el área encerrada por el contorno
            cv2.putText(frame, '{},{}'.format(x, y), (x + 10, y), font, 0.75, (0,0, 250), 1, cv2.LINE_AA)
            cv2.putText(frame, '{}'.format(area), (x + 10, y + 20), font, 0.75, (0, 0, 250), 1, cv2.LINE_AA)
            #Encuentra los contornos de la imagen 
            contorno_convexo= cv2.convexHull(cnt)
            #Muestra sobre la imagen el contorno convexo 
            cv2.drawContours(frame, [contorno_convexo], 0, (255, 0, 0), 3)

        #Perimetro del contorno
        epsilon = 0.0005 * cv2.arcLength(cnt, True)
        #Aproximar el contorno para un resultado mas simplificado
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        # Hace una linea convexa alrededor de la mano
        hull = cv2.convexHull(cnt)
        #Caulculo del área de los contornos anteriormente encontrados
        areahull = cv2.contourArea(hull)
        areacnt = cv2.contourArea(cnt)
        # Se encuentra el porcentaje del area que no está cubierta por la mano
        arearatio = ((areahull - areacnt) / areacnt) * 100
        # Se encuentran los defectos en el area convexa, permite diferenciar entre cada dedo
        hull = cv2.convexHull(approx, returnPoints=False)
        defects = cv2.convexityDefects(approx, hull)

        #indices = numero de dedos
        indices = 0

        # Se encuentra el número de defectos debido a la separación de los dedos
        if defects is not None:
            for i in range(defects.shape[0]):
                # Se definen las coordenadas de los defectos, dónde empiezan dónde terminen y eso
                s, e, f, d = defects[i, 0]
                start = tuple(approx[s][0])
                end = tuple(approx[e][0])
                far = tuple(approx[f][0])
                pt = (100, 180)

                # Se encuentran los tamaños de los lados del triángulo
                a = math.sqrt((end[0] - start[0]) ** 2 + (end[1] - start[1]) ** 2)
                b = math.sqrt((far[0] - start[0]) ** 2 + (far[1] - start[1]) ** 2)
                c = math.sqrt((end[0] - far[0]) ** 2 + (end[1] - far[1]) ** 2)

                # Se calcula el semiperímetro del triángulo
                s = (a + b + c) / 2

                # Se aplica la fórmula de Herón para encontrar el área
                ar = math.sqrt(s * (s - a) * (s - b) * (s - c))

                # Se calcula la distancia entre el punto y el area convexa
                d = (2 * ar) / a

                # Se aplica la regla del coseno
                angle = math.acos((b ** 2 + c ** 2 - a ** 2) / (2 * b * c)) * 57

                # Se ignoran angulos mayores a 90 y defectos que estén muy cerca del área convexa (generalmente se deben a ruido)
                if angle <= 90 and d > 30:
                    indices += 1
            indices += 1
            font = cv2.FONT_HERSHEY_SIMPLEX
            if indices == 5:
                cv2.putText(frame, 'Nueva partida', (0, 50), font, 2, (0, 0, 0), 3, cv2.LINE_AA)               
                accion = 5    
            elif x >= 200 and x <= 320 and y>= 80 and y <=170:
                cv2.putText(frame, 'Rotar figura', (0, 50), font, 2, (0, 0, 0), 3, cv2.LINE_AA)                  
            elif  x >= 480:
                cv2.putText(frame, 'Mov. a la derecha', (0, 50), font, 2, (0, 0, 0), 3, cv2.LINE_AA)
            elif  x >= 15 and x <= 230:
                cv2.putText(frame, 'Mov. a la izquierda', (0, 50), font, 2, (0, 0, 0), 3, cv2.LINE_AA)     
            elif indices == 3 :  
                cv2.putText(frame, 'Bajar figura', (0, 50), font, 2, (0, 0, 0), 3, cv2.LINE_AA)
                count = [0, 0]
                accion = 3
            else:
                cv2.putText(frame, 'No movimiento ', (0, 50), font, 2, (0, 0, 0), 3, cv2.LINE_AA)
                

    # Se muestra la imagen resultante
    cv2.imshow('frame', frame)
    #Aila objetos con los umbrales de color amarillo
    #cv2.imshow('mask', mask)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return        
    return x, y, accion
#--------------------------------------------------------------------------
#---------------------------  FIN DE FUNCIONES ----------------------------
#--------------------------------------------------------------------------