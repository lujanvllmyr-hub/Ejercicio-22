
import pygame
import math


ANCHO_PANTALLA = 960
ALTO_PANTALLA = 540
FPS = 60


class Proyectil:
    def __init__(self, x, y, ancho, alto, velocidad, color, direccion=1):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.velocidad = velocidad
        self.color = color
        self.direccion = direccion

    def actualizar(self):
        self.rect.x += self.velocidad * self.direccion

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color, self.rect)

class Nave:
    def __init__(self, x, y, ancho, alto, velocidad, salud):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.velocidad = velocidad
        self.salud = salud

    def mover(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        self.rect.x = max(0, min(ANCHO_PANTALLA - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(ALTO_PANTALLA - self.rect.height, self.rect.y))

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, (255, 255, 255), self.rect)

class Jugador(Nave):
    def __init__(self, x, y):
        super().__init__(x, y, 46, 28, 6, 100)
        self.cooldown = 0.0

    def disparar(self):
        if self.cooldown > 0:
            return None

        bala = Proyectil(
            self.rect.centerx - 3,
            self.rect.centery - 2,
            8,
            4,
            12,
            (100, 255, 100),
            direccion=1,
        )
        self.cooldown = 0.25
        return bala

    def dibujar(self, pantalla):
        pygame.draw.polygon(
            pantalla,
            (80, 220, 255),
            [
                (self.rect.centerx, self.rect.top),
                (self.rect.left, self.rect.bottom),
                (self.rect.centerx, self.rect.centery + 8),
                (self.rect.right, self.rect.bottom),
            ],
        )
        pygame.draw.rect(pantalla, (180, 220, 255), self.rect)

class Enemigo(Nave):
    def __init__(self, x, y, velocidad, dificultad):
        super().__init__(x, y, 42, 30, velocidad * dificultad, 3)
        self.sentido = 1
        self.base_y = y
        self.velocidad_base = velocidad

    def actualizar(self, dificultad):
        self.velocidad = self.velocidad_base * dificultad
        self.rect.x += self.sentido * self.velocidad
        if self.rect.left <= 80 or self.rect.right >= ANCHO_PANTALLA - 80:
            self.sentido *= -1
            self.rect.y += 26

    def dibujar(self, pantalla):
        pygame.draw.polygon(
            pantalla,
            (255, 90, 90),
            [
                (self.rect.centerx, self.rect.top),
                (self.rect.right, self.rect.centery),
                (self.rect.centerx, self.rect.bottom),
                (self.rect.left, self.rect.centery),
            ],
        )

class JefeFinal(Enemigo):
    def __init__(self, x, y, dificultad):
        super().__init__(x, y, 2.2, dificultad)
        self.rect.width = 120
        self.rect.height = 90
        self.salud = 25
        self.velocidad_base = 2.2
        self.phase = 0

    def actualizar(self, dificultad):
        self.phase += 0.08
        self.velocidad = self.velocidad_base * dificultad
        self.rect.x += self.sentido * self.velocidad
        self.rect.y = self.base_y + math.sin(self.phase) * 40

        if self.rect.left <= 120 or self.rect.right >= ANCHO_PANTALLA - 120:
            self.sentido *= -1

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, (255, 180, 60), self.rect)
        pygame.draw.rect(pantalla, (120, 30, 30), (self.rect.x + 20, self.rect.y + 20, 80, 18))
        pygame.draw.rect(
            pantalla,
            (255, 50, 50),
            (self.rect.x + 20, self.rect.y + 20, 80 * (self.salud / 25), 18)
        )
        
class Obstaculo:
    def __init__(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, (70, 70, 90), self.rect)
        pygame.draw.rect(pantalla, (160, 160, 180), self.rect, 2)