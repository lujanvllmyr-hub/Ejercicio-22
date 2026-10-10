import math
import random

import pygame


class _Particula:
    RADIO_MAXIMO = 4

    def __init__(self):
        self.superficie = pygame.Surface(
            (self.RADIO_MAXIMO * 2, self.RADIO_MAXIMO * 2),
            pygame.SRCALPHA,
        )
        self.activa = False
        self.x = 0.0
        self.y = 0.0
        self.velocidad_x = 0.0
        self.velocidad_y = 0.0
        self.tiempo_total = 0.0
        self.tiempo_restante = 0.0

    @property
    def alpha(self):
        if self.tiempo_total <= 0:
            return 0.0
        return (self.tiempo_restante / self.tiempo_total) * 255

    def activar(self, x, y, velocidad, duracion, color, radio):
        angulo = random.uniform(0, math.tau)
        self.x = float(x)
        self.y = float(y)
        self.velocidad_x = math.cos(angulo) * velocidad
        self.velocidad_y = math.sin(angulo) * velocidad
        self.tiempo_total = duracion
        self.tiempo_restante = duracion
        self.activa = True

        self.superficie.fill((0, 0, 0, 0))
        pygame.draw.circle(
            self.superficie,
            color,
            (self.RADIO_MAXIMO, self.RADIO_MAXIMO),
            radio,
        )

    def actualizar(self, dt):
        self.tiempo_restante = max(0.0, self.tiempo_restante - dt)
        if self.tiempo_restante == 0:
            self.activa = False
            return

        self.x += self.velocidad_x * dt
        self.y += self.velocidad_y * dt

    def dibujar(self, pantalla):
        if not self.activa:
            return

        self.superficie.set_alpha(round(self.alpha))
        pantalla.blit(
            self.superficie,
            (
                round(self.x - self.RADIO_MAXIMO),
                round(self.y - self.RADIO_MAXIMO),
            ),
        )


class EmisorParticulas:
    """Emisor con un pool fijo de partículas reutilizables."""

    MAX_PARTICULAS = 100
    CANTIDAD_EXPLOSION = 15
    DURACION_PARTICULA = 0.8
    COLORES_EXPLOSION = (
        (255, 90, 40),
        (255, 160, 40),
        (255, 220, 90),
    )

    def __init__(self):
        self._particulas = [
            _Particula() for _ in range(self.MAX_PARTICULAS)
        ]

    @property
    def particulas_activas(self):
        return sum(particula.activa for particula in self._particulas)

    @property
    def particulas_inactivas(self):
        return self.MAX_PARTICULAS - self.particulas_activas

    def emitir(self, x, y, cantidad=CANTIDAD_EXPLOSION):
        """Reutiliza partículas inactivas y, si faltan, las próximas a expirar."""
        if isinstance(cantidad, bool) or not isinstance(cantidad, int):
            raise TypeError("La cantidad de partículas debe ser un entero.")
        if cantidad < 0:
            raise ValueError("La cantidad de partículas no puede ser negativa.")
        if cantidad > self.MAX_PARTICULAS:
            raise ValueError(
                f"No se pueden emitir más de {self.MAX_PARTICULAS} partículas."
            )
        if cantidad == 0:
            return 0
        if any(
            isinstance(valor, bool)
            or not isinstance(valor, (int, float))
            or not math.isfinite(valor)
            for valor in (x, y)
        ):
            raise TypeError("La posición de emisión debe contener números finitos.")

        disponibles = [
            particula for particula in self._particulas if not particula.activa
        ]
        disponibles.extend(
            sorted(
                (
                    particula
                    for particula in self._particulas
                    if particula.activa
                ),
                key=lambda particula: particula.tiempo_restante,
            )
        )

        for particula in disponibles[:cantidad]:
            particula.activar(
                x=x,
                y=y,
                velocidad=random.uniform(50, 180),
                duracion=random.uniform(0.45, self.DURACION_PARTICULA),
                color=random.choice(self.COLORES_EXPLOSION),
                radio=random.randint(2, particula.RADIO_MAXIMO),
            )

        return cantidad

    def actualizar(self, dt):
        if (
            isinstance(dt, bool)
            or not isinstance(dt, (int, float))
            or not math.isfinite(dt)
            or dt < 0
        ):
            raise ValueError("dt debe ser un número finito no negativo.")

        for particula in self._particulas:
            if particula.activa:
                particula.actualizar(dt)

    def dibujar(self, pantalla):
        for particula in self._particulas:
            particula.dibujar(pantalla)
