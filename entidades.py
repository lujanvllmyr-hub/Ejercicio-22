import math
import pygame

from componente_salud import ComponenteSalud


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
    DURACION_INVULNERABILIDAD = 1.0

    def __init__(self, x, y, ancho, alto, velocidad, salud):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.hurtbox = self.rect.copy()
        self.velocidad = velocidad
        self.componente_salud = ComponenteSalud(salud)
        self.temporizador_invulnerable = 0

    @property
    def salud(self):
        return self.componente_salud.vida_actual

    @salud.setter
    def salud(self, cantidad):
        self.componente_salud.establecer_vida(cantidad)

    def recibir_dano(self, cantidad):
        if self.temporizador_invulnerable > 0:
            return self.salud

        salud_anterior = self.salud
        salud_actual = self.componente_salud.recibir_dano(cantidad)
        if salud_actual < salud_anterior:
            self.temporizador_invulnerable = self.DURACION_INVULNERABILIDAD
        return salud_actual

    def esta_vivo(self):
        return self.componente_salud.esta_vivo()

    def actualizar_temporizador_invulnerable(self, dt):
        self.temporizador_invulnerable = max(
            0.0, self.temporizador_invulnerable - dt
        )

    def sincronizar_hurtbox(self):
        self.hurtbox.update(self.rect)

    def mover(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy
        self.rect.x = max(0, min(ANCHO_PANTALLA - self.rect.width, self.rect.x))
        self.rect.y = max(0, min(ALTO_PANTALLA - self.rect.height, self.rect.y))
        self.sincronizar_hurtbox()

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, (255, 255, 255), self.rect)

class Jugador(Nave):
    DURACION_ATAQUE = 0.15
    ANCHO_ATAQUE = 44

    def __init__(self, x, y):
        super().__init__(x, y, 46, 28, 6, 100)
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.cooldown = 0.0
        self.attackbox = None
        self.ataque_restante = 0.0
        self.ataque_aplicado = False

    def iniciar_ataque(self):
        if self.attackbox is not None:
            return

        self.attackbox = pygame.Rect(
            self.hurtbox.right,
            self.hurtbox.top,
            self.ANCHO_ATAQUE,
            self.hurtbox.height,
        )
        self.ataque_restante = self.DURACION_ATAQUE
        self.ataque_aplicado = False

    def actualizar_ataque(self, dt):
        if self.attackbox is None:
            return

        self.ataque_restante = max(0.0, self.ataque_restante - dt)
        if self.ataque_restante == 0.0:
            self.attackbox = None
            return

        self.attackbox.topleft = (self.hurtbox.right, self.hurtbox.top)

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
        color_nave = (
            (255, 70, 70)
            if self.temporizador_invulnerable > 0
            else (80, 220, 255)
        )
        color_borde = (
            (255, 190, 190)
            if self.temporizador_invulnerable > 0
            else (180, 220, 255)
        )
        pygame.draw.polygon(
            pantalla,
            color_nave,
            [
                (self.rect.centerx, self.rect.top),
                (self.rect.left, self.rect.bottom),
                (self.rect.centerx, self.rect.centery + 8),
                (self.rect.right, self.rect.bottom),
            ],
        )
        pygame.draw.rect(pantalla, color_borde, self.rect)


def resolver_colisiones_aabb(
    jugador: Jugador,
    objetos_estaticos: list[pygame.Rect],
    dt: float,
) -> None:
    """Mueve al jugador por ejes y detiene la velocidad al colisionar."""
    if not math.isfinite(dt) or dt < 0:
        raise ValueError("dt debe ser un número finito no negativo.")

    jugador.x += jugador.vx * dt
    jugador.rect.x = round(jugador.x)

    if jugador.rect.left < 0:
        jugador.rect.left = 0
        jugador.vx = 0.0
    elif jugador.rect.right > ANCHO_PANTALLA:
        jugador.rect.right = ANCHO_PANTALLA
        jugador.vx = 0.0

    for objeto in objetos_estaticos:
        if jugador.rect.colliderect(objeto):
            if jugador.vx > 0:
                jugador.rect.right = objeto.left
            elif jugador.vx < 0:
                jugador.rect.left = objeto.right
            jugador.vx = 0.0
            jugador.x = float(jugador.rect.x)

    jugador.y += jugador.vy * dt
    jugador.rect.y = round(jugador.y)

    if jugador.rect.top < 0:
        jugador.rect.top = 0
        jugador.vy = 0.0

    for objeto in objetos_estaticos:
        if jugador.rect.colliderect(objeto):
            if jugador.vy > 0:
                jugador.rect.bottom = objeto.top
            elif jugador.vy < 0:
                jugador.rect.top = objeto.bottom
            jugador.vy = 0.0
            jugador.y = float(jugador.rect.y)

    jugador.x = float(jugador.rect.x) if jugador.vx == 0 else jugador.x
    jugador.y = float(jugador.rect.y) if jugador.vy == 0 else jugador.y


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
        self.sincronizar_hurtbox()

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
        self.sincronizar_hurtbox()
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
        self.sincronizar_hurtbox()

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, (255, 180, 60), self.rect)
        pygame.draw.rect(pantalla, (120, 30, 30), (self.rect.x + 20, self.rect.y + 20, 80, 18))
        pygame.draw.rect(
            pantalla,
            (255, 50, 50),
            (self.rect.x + 20, self.rect.y + 20, 80 * (self.salud / 25), 18)
        )
        

class EnemigoPrueba(Nave):
    def __init__(self, x, y):
        super().__init__(x, y, 42, 30, 0, 3)

    def actualizar(self, dificultad):
        pass

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, (180, 90, 255), self.rect)
        pygame.draw.rect(pantalla, (230, 200, 255), self.hurtbox, 2)


class Obstaculo:
    def __init__(self, x, y, ancho, alto):
        self.rect = pygame.Rect(x, y, ancho, alto)

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, (70, 70, 90), self.rect)
        pygame.draw.rect(pantalla, (160, 160, 180), self.rect, 2)