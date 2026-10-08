import math
import os
import sys
import time
from abc import ABC, abstractmethod

import pygame

from entidades import Proyectil, Nave, Jugador, Enemigo, JefeFinal, Obstaculo

ANCHO_PANTALLA = 960
ALTO_PANTALLA = 540
FPS = 60


class EscenaBase(ABC):
    def manejar_evento(self, evento):
        pass

    @abstractmethod
    def actualizar(self, dt):
        raise NotImplementedError

    @abstractmethod
    def dibujar(self, pantalla):
        raise NotImplementedError


class GestorEscenas:
    def __init__(self):
        self.estados = {}
        self.estado_actual = None

    def registrar_escena(self, nombre, escena):
        if not isinstance(escena, EscenaBase):
            raise TypeError("La escena debe heredar de EscenaBase.")

        self.estados[nombre] = escena
        if self.estado_actual is None:
            self.estado_actual = nombre

    def cambiar_escena(self, nombre):
        if nombre not in self.estados:
            raise ValueError(f"No existe la escena '{nombre}'.")
        self.estado_actual = nombre

    def _obtener_escena_actual(self):
        if self.estado_actual is None:
            raise RuntimeError("No hay una escena activa.")
        return self.estados[self.estado_actual]

    def actualizar(self, dt):
        self._obtener_escena_actual().actualizar(dt)

    def dibujar(self, pantalla):
        self._obtener_escena_actual().dibujar(pantalla)

    def manejar_evento(self, evento):
        self._obtener_escena_actual().manejar_evento(evento)


class EscenaMenu(EscenaBase):
    def __init__(self, gestor_escenas):
        self.gestor_escenas = gestor_escenas
        self.font = pygame.font.SysFont(None, 40)

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key in (
            pygame.K_RETURN,
            pygame.K_KP_ENTER,
        ):
            self.gestor_escenas.cambiar_escena("nivel1")

    def actualizar(self, dt):
        pass

    def dibujar(self, pantalla):
        pantalla.fill((10, 12, 25))
        texto = self.font.render("Presionar ENTER para comenzar", True, (255, 255, 255))
        rect_texto = texto.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2))
        pantalla.blit(texto, rect_texto)



class Juego(EscenaBase):
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.reloj = pygame.time.Clock()
        self.escenario = 1
        self.dificultad = 1
        self.estado = "jugando"
        self.texto_fin = ""
        self.font = pygame.font.SysFont(None, 32)

        self.jugador = Jugador(60, ALTO_PANTALLA // 2)
        self._jugador_x = float(self.jugador.rect.x)
        self._jugador_y = float(self.jugador.rect.y)
        self.enemigos = []
        self.obstaculos = []
        self.proyectiles_jugador = []
        self.proyectiles_enemigos = []
        self.boss = None

        self.crear_escenario()

        self.gestor_escenas = GestorEscenas()
        self.gestor_escenas.registrar_escena(
            "menu", EscenaMenu(self.gestor_escenas)
        )
        self.gestor_escenas.registrar_escena("nivel1", self)

    def crear_escenario(self):
        self.dificultad = self.escenario
        self.proyectiles_jugador.clear()
        self.proyectiles_enemigos.clear()
        self.obstaculos.clear()
        self.enemigos.clear()
        self.boss = None

        if self.escenario == 1:
            self.enemigos = [
                Enemigo(700, 90, 1.8, self.dificultad),
                Enemigo(770, 220, 2.0, self.dificultad),
                Enemigo(830, 360, 2.2, self.dificultad),
            ]

        elif self.escenario == 2:
            self.obstaculos = [
                Obstaculo(280, 150, 140, 20),
                Obstaculo(460, 250, 140, 20),
                Obstaculo(640, 350, 140, 20),
            ]
            self.enemigos = [
                Enemigo(700, 100, 2.5, self.dificultad),
                Enemigo(760, 180, 2.9, self.dificultad),
                Enemigo(820, 260, 3.1, self.dificultad),
                Enemigo(760, 360, 3.4, self.dificultad),
            ]

        elif self.escenario == 3:
            self.boss = JefeFinal(700, 180, self.dificultad)

    def cambiar_escenario(self):
        if self.escenario == 1 and self.jugador.rect.x >= 750:
            self.escenario = 2
            self.crear_escenario()
        elif self.escenario == 2 and not self.enemigos:
            self.escenario = 3
            self.crear_escenario()

    def manejar_eventos(self, dt):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            self.gestor_escenas.manejar_evento(evento)

        if self.gestor_escenas.estado_actual == "nivel1":
            teclas = pygame.key.get_pressed()
            movimiento_x = int(teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) - int(
                teclas[pygame.K_a] or teclas[pygame.K_LEFT]
            )
            movimiento_y = int(teclas[pygame.K_s] or teclas[pygame.K_DOWN]) - int(
                teclas[pygame.K_w] or teclas[pygame.K_UP]
            )
            velocidad = self.jugador.velocidad * FPS
            self._jugador_x = max(
                0.0,
                min(
                    ANCHO_PANTALLA - self.jugador.rect.width,
                    self._jugador_x + movimiento_x * velocidad * dt,
                ),
            )
            self._jugador_y = max(
                0.0,
                min(
                    ALTO_PANTALLA - self.jugador.rect.height,
                    self._jugador_y + movimiento_y * velocidad * dt,
                ),
            )
            self.jugador.rect.x = round(self._jugador_x)
            self.jugador.rect.y = round(self._jugador_y)

            self.jugador.cooldown = max(0.0, self.jugador.cooldown - 1 / FPS)

        return True

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
            bala = self.jugador.disparar()
            if bala is not None:
                self.proyectiles_jugador.append(bala)

    def actualizar_enemigos(self):
        for enemigo in self.enemigos:
            enemigo.actualizar(self.dificultad)
            if enemigo.rect.colliderect(self.jugador.rect):
                self.crear_escenario()
                return True

            if enemigo.rect.bottom >= ALTO_PANTALLA:
                enemigo.rect.y = ALTO_PANTALLA - enemigo.rect.height

        if self.boss is not None:
            self.boss.actualizar(self.dificultad)
            if self.boss.rect.colliderect(self.jugador.rect):
                self.crear_escenario()
                return True

        return False

    def _actualizar_proyectiles_jugador(self):
        """Actualiza la posición de cada proyectil del jugador."""
        for proyectil in self.proyectiles_jugador[:]:
            proyectil.actualizar()

    def _detectar_colisiones_proyectiles_enemigos(self):
        """Detecta impactos de proyectiles contra enemigos."""
        for proyectil in self.proyectiles_jugador[:]:
            for enemigo in self.enemigos[:]:
                if proyectil.rect.colliderect(enemigo.rect):
                    enemigo.salud -= 1
                    self.proyectiles_jugador.remove(proyectil)
                    if enemigo.salud <= 0:
                        self.enemigos.remove(enemigo)
                    break

    def _detectar_colisiones_proyectiles_jefe(self):
        """Detecta impactos de proyectiles contra el jefe final."""
        if self.boss is not None:
            for proyectil in self.proyectiles_jugador[:]:
                if proyectil.rect.colliderect(self.boss.rect):
                    self.boss.salud -= 1
                    self.proyectiles_jugador.remove(proyectil)
                    if self.boss.salud <= 0:
                        self.estado = "victoria"
                        self.texto_fin = "¡Victoria! Has derrotado al jefe final."
                    break

    def _limpiar_proyectiles_fuera_de_pantalla(self):
        """Elimina proyectiles que salen de la pantalla por la derecha."""
        for proyectil in self.proyectiles_jugador[:]:
            if proyectil.rect.x > ANCHO_PANTALLA:
                self.proyectiles_jugador.remove(proyectil)

    def _detectar_colisiones_proyectiles_obstaculos(self):
        """Detecta impactos de proyectiles contra obstáculos."""
        for obstaculo in self.obstaculos:
            for proyectil in self.proyectiles_jugador[:]:
                if proyectil.rect.colliderect(obstaculo.rect):
                    self.proyectiles_jugador.remove(proyectil)

    def _detectar_colisiones_enemigos_jugador(self):
        """Detecta colisiones entre enemigos/jefe y jugador, aplicando daño."""
        if self.estado == "jugando":
            for enemigo in self.enemigos:
                if enemigo.rect.colliderect(self.jugador.rect):
                    self.jugador.salud -= 1

            if self.boss is not None and self.boss.rect.colliderect(self.jugador.rect):
                self.jugador.salud -= 1

            if self.jugador.salud <= 0:
                self.estado = "derrota"
                self.texto_fin = "Derrota. La nave cayó en combate."

    def detectar_colisiones(self):
        """Coordina todas las detecciones de colisión del juego."""
        self._actualizar_proyectiles_jugador()
        self._detectar_colisiones_proyectiles_enemigos()
        self._detectar_colisiones_proyectiles_jefe()
        self._limpiar_proyectiles_fuera_de_pantalla()
        self._detectar_colisiones_proyectiles_obstaculos()
        self._detectar_colisiones_enemigos_jugador()

    def actualizar(self, dt):
        if self.estado != "jugando":
            return

        self.cambiar_escenario()
        if self.actualizar_enemigos():
            return
        self.detectar_colisiones()

        if self.jugador.salud <= 0:
            self.estado = "derrota"
            self.texto_fin = "Derrota. La nave fue destruida."

    def dibujar_hud(self, pantalla):
        texto_escenario = self.font.render(f"Escenario: {self.escenario} | Dificultad: {self.dificultad}", True, (255, 255, 255))
        texto_salud = self.font.render(f"Salud: {max(0, self.jugador.salud)}", True, (255, 255, 255))
        pantalla.blit(texto_escenario, (20, 20))
        pantalla.blit(texto_salud, (20, 50))

    def dibujar(self, pantalla):
        pantalla.fill((10, 12, 25))

        if self.escenario == 1:
            pygame.draw.rect(pantalla, (18, 40, 60), (0, 0, ANCHO_PANTALLA, ALTO_PANTALLA))
        elif self.escenario == 2:
            pygame.draw.rect(pantalla, (15, 24, 40), (0, 0, ANCHO_PANTALLA, ALTO_PANTALLA))
        else:
            pygame.draw.rect(pantalla, (28, 12, 24), (0, 0, ANCHO_PANTALLA, ALTO_PANTALLA))

        for obstaculo in self.obstaculos:
            obstaculo.dibujar(pantalla)

        for enemigo in self.enemigos:
            enemigo.dibujar(pantalla)

        if self.boss is not None:
            self.boss.dibujar(pantalla)

        self.jugador.dibujar(pantalla)

        for proyectil in self.proyectiles_jugador:
            proyectil.dibujar(pantalla)

        self.dibujar_hud(pantalla)

        if self.estado != "jugando":
            overlay = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            pantalla.blit(overlay, (0, 0))

            texto = self.font.render(self.texto_fin, True, (255, 255, 255))
            rect_texto = texto.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2))
            pantalla.blit(texto, rect_texto)

    def ejecutar(self):
        corriendo = True
        ejecutando = True
        estado_juego = "jugando"
        while corriendo:
            dt = self.reloj.tick(FPS) / 1000.0
            corriendo = self.manejar_eventos(dt)
            self.gestor_escenas.actualizar(dt)
            self.gestor_escenas.dibujar(self.pantalla)
            pygame.display.flip()
        pygame.quit()
        sys.exit()


class EscenaNive1(Juego):
    pass


def main():
    # Leer variables de entorno
    db_usuario = os.getenv('DB_USUARIO')
    db_password = os.getenv('DB_PASSWORD')

    # Imprimir mensaje de conexión (NUNCA imprimir la contraseña)
    if db_usuario:
        print(f"Conectando usuario: {db_usuario}")

    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
    pygame.display.set_caption("Ataque espacial")

    juego = EscenaNive1(pantalla)
    juego.ejecutar()


if __name__ == "__main__":
    main()
