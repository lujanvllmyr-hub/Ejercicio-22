import math
from abc import ABC, abstractmethod

import pygame


class EntidadBase(ABC):
    """Base para entidades con movimiento independiente del framerate."""

    def __init__(
        self,
        x: float,
        y: float,
        ancho: int,
        alto: int,
        vx: float = 0.0,
        vy: float = 0.0,
        g: float = 500.0,
        velocidad_horizontal: float = 300.0,
    ) -> None:
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.g = float(g)
        self.velocidad_horizontal = float(velocidad_horizontal)
        self.hitbox = pygame.Rect(round(self.x), round(self.y), ancho, alto)
        self.rect = self.hitbox

    def mover(self, dt: float) -> None:
        """Integra la velocidad en píxeles por segundo usando dt en segundos."""
        self._validar_dt(dt)

        self.x += self.vx * dt
        self.y += self.vy * dt
        self.hitbox.topleft = (round(self.x), round(self.y))

    def actualizar(self, dt: float) -> None:
        """Lee el teclado, aplica gravedad y actualiza la posición."""
        self._validar_dt(dt)
        teclas = pygame.key.get_pressed()
        direccion_x = int(teclas[pygame.K_RIGHT]) - int(teclas[pygame.K_LEFT])

        self.vx = direccion_x * self.velocidad_horizontal
        self.vy += self.g * dt
        self.mover(dt)

    @staticmethod
    def _validar_dt(dt: float) -> None:
        if not math.isfinite(dt) or dt < 0:
            raise ValueError("dt debe ser un número finito no negativo.")

    @abstractmethod
    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja la entidad en pantalla."""
        raise NotImplementedError
