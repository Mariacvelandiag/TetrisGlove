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
#---Programa Juego con deteccion de guante --------------------------------
#--------------------------------------------------------------------------

#---- Se importan las librerias necesarias---------------------------------
import cv2
from guante_detectado import capture
from guante_detectado import yellow_glove
import time
import os
import pygame
import random

#---- lista de los diferentes colores que se utilizan en el juego de Tetris
#---- y sus tonalidades específicas en el espacio de color RGB.
colors = [
    (0, 0, 0),
    (120, 37, 179),
    (100, 179, 179),
    (80, 34, 22),
    (80, 134, 22),
    (180, 34, 22),
    (180, 34, 122),
]
#---- Creacion de las diferentes figuras para el juego----------------------
class Figure:
    x = 0
    y = 0

    figures = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[4, 5, 9, 10], [2, 6, 5, 9]],
        [[6, 7, 9, 10], [1, 5, 6, 10]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[1, 2, 5, 6]],
    ]

#--------------------------------------------------------------------------
#-----Funciones------------------------------------------------------------
#--------------------------------------------------------------------------
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(self.figures) - 1)
        self.color = random.randint(1, len(colors) - 1)
        self.rotation = 0

    def image(self):
        return self.figures[self.type][self.rotation]

    def rotate(self):
        
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])

class Tetris:
    def __init__(self, height, width):
        self.level = 2
        self.score = 0
        self.state = "start"
        self.field = []
        self.height = 0
        self.width = 0
        self.x = 100
        self.y = 60
        self.zoom = 30
        self.figure = None
    
        self.height = height
        self.width = width
        self.field = []
        self.score = 0
        self.state = "start"
        for i in range(height):
            new_line = []
            for j in range(width):
                new_line.append(0)
            self.field.append(new_line)

    def new_figure(self):
        time.sleep(0.5)
        self.figure = Figure(3, 0)

    def intersects(self):
        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if i + self.figure.y > self.height - 1 or \
                            j + self.figure.x > self.width - 1 or \
                            j + self.figure.x < 0 or \
                            self.field[i + self.figure.y][j + self.figure.x] > 0:
                        intersection = True
        return intersection

    def break_lines(self):
        lines = 0
        for i in range(1, self.height):
            zeros = 0
            for j in range(self.width):
                if self.field[i][j] == 0:
                    zeros += 1
            if zeros == 0:
                lines += 1
                for i1 in range(i, 1, -1):
                    for j in range(self.width):
                        self.field[i1][j] = self.field[i1 - 1][j]
        self.score += lines ** 2

    def go_space(self):
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()

    def go_down(self):
        time.sleep(0.2)
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.break_lines()
        self.new_figure()
        if self.intersects():
            self.state = "gameover"

    def go_side(self, dx):
        time.sleep(0.3)
        old_x = self.figure.x
        self.figure.x += dx
        
        if self.intersects():
            self.figure.x = old_x

    def rotate(self):
        time.sleep(0.6)
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.rotation = old_rotation


#---- Se inicializa el juego  ---------------------------------------------    
pygame.init()

#---- Se define algunos colores--------------------------------------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
#----Se establece el tamaño de la ventana en píxeles-----------------------
size = (600, 700)
#----Se establece la posición de la ventana en la pantalla del usuario-----
os.environ['SDL_VIDEO_WINDOW_POS'] = "880,60"
#---- Esta surface se utiliza como la ventana principal del juego de Tetris
screen = pygame.display.set_mode(size)
#----Se establece el título de la ventana----------------------------------
pygame.display.set_caption("Tetris")

#---- Bucle hasta que el usuario haga clic en el botón de cerrar-----------
done = False
clock = pygame.time.Clock()
fps = 25
game = Tetris(20, 10)
counter = 0
pressing_down = False
#----Se utiliza para crear nuevas figuras, controlar la velocidad del juego
#---- y mover las figuras hacia abajo en el campo de juego en tiempo real.
while not done:
    if game.figure is None:
        game.new_figure()
    counter += 1
    if counter > 100000:
        counter = 0
    
    if counter % (fps // game.level // 2) == 0 or pressing_down:
        if game.state == "start":
            game.go_down()

#----Comportamiento de las fichas dependiendo de guante_detectado----------    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
#----Se llama la funcion que captura la imagen de la camara y detecta el
#--- guante amarillo
    frame = capture()
    X,Y, accion = yellow_glove(frame)
 
    if accion==3:#-----------------------------------------BAJAR FICHA
        game.go_space()
    if X >= 200 and X <= 320 and Y>= 80 and Y <=170:#------ROTAR FICHA
        game.rotate()            
    if X >= 370:#------------------MOVIMIENTO DE LA FICHA A LA DERECHA
        game.go_side(1)            
    if X >= 15 and X <= 230:#----MOVIMIENTO DE LA FICHA A LA IZQUIERDA
        game.go_side(-1)
    if accion==5:#---------------------------------------NUEVA PARTIDA
        game.__init__(20, 10)

    screen.fill(WHITE)
#----Campo de juego de Tetris en la pantalla 
    for i in range(game.height):
        for j in range(game.width):
            pygame.draw.rect(screen, GRAY, [game.x + game.zoom * j, game.y + game.zoom * i, game.zoom, game.zoom], 1)
            if game.field[i][j] > 0:
                pygame.draw.rect(screen, colors[game.field[i][j]],
                                 [game.x + game.zoom * j + 1, game.y + game.zoom * i + 1, game.zoom - 2, game.zoom - 1])
#----Figura actual en el campo de juego
    if game.figure is not None:
        for i in range(4):
            for j in range(4):
                p = i * 4 + j
                if p in game.figure.image():
                    pygame.draw.rect(screen, colors[game.figure.color],
                                     [game.x + game.zoom * (j + game.figure.x) + 1,
                                      game.y + game.zoom * (i + game.figure.y) + 1,
                                      game.zoom - 2, game.zoom - 2])
#----Estetica, cuando se acaba el juego
    font = pygame.font.SysFont('Arial', 20, True, False)
    font1 = pygame.font.SysFont('Arial', 60, True, False)
    text = font.render("Score: " + str(game.score), True, BLACK)
    text_game_over = font1.render("Game Over", True, (255, 125, 0))
    text_game_over1 = font1.render("HI 5", True, (255, 215, 0))
#----Se muestra puntuacion t textos configurados anteriormente
    screen.blit(text, [0, 0])
    if game.state == "gameover":
        screen.blit(text_game_over, [55, 200])
        screen.blit(text_game_over1, [35, 265])
#----Actualizar pantalla luego de cambios
    pygame.display.flip()
    clock.tick(fps)
    
#----Libera todos los recuros utilizados por los modulos Pygame para este programa
pygame.quit()

#--------------------------------------------------------------------------
#---------------------------  FIN DEL PROGRAMA ----------------------------
#--------------------------------------------------------------------------