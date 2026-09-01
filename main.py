import math
import sys

import pygame

from entidades import Proyectil, Nave, Jugador, Enemigo, JefeFinal, Obstaculo

ANCHO_PANTALLA = 960
ALTO_PANTALLA = 540
FPS = 60



class Juego:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        self.reloj = pygame.time.Clock()
        self.escenario = 1
        self.dificultad = 1
        self.estado = "jugando"
        self.texto_fin = ""
        self.font = pygame.font.SysFont(None, 32)

        self.jugador = Jugador(60, ALTO_PANTALLA // 2)
        self.enemigos = []
        self.obstaculos = []
        self.proyectiles_jugador = []
        self.proyectiles_enemigos = []
        self.boss = None

        self.crear_escenario()

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

    def manejar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
                bala = self.jugador.disparar()
                if bala is not None:
                    self.proyectiles_jugador.append(bala)

        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            self.jugador.mover(-self.jugador.velocidad, 0)
        if teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            self.jugador.mover(self.jugador.velocidad, 0)
        if teclas[pygame.K_w] or teclas[pygame.K_UP]:
            self.jugador.mover(0, -self.jugador.velocidad)
        if teclas[pygame.K_s] or teclas[pygame.K_DOWN]:
            self.jugador.mover(0, self.jugador.velocidad)

        self.jugador.cooldown = max(0.0, self.jugador.cooldown - 1 / FPS)

        return True

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

    def actualizar(self):
        if self.estado != "jugando":
            return

        self.cambiar_escenario()
        if self.actualizar_enemigos():
            return
        self.detectar_colisiones()

        if self.jugador.salud <= 0:
            self.estado = "derrota"
            self.texto_fin = "Derrota. La nave fue destruida."

    def dibujar_hud(self):
        texto_escenario = self.font.render(f"Escenario: {self.escenario} | Dificultad: {self.dificultad}", True, (255, 255, 255))
        texto_salud = self.font.render(f"Salud: {max(0, self.jugador.salud)}", True, (255, 255, 255))
        self.pantalla.blit(texto_escenario, (20, 20))
        self.pantalla.blit(texto_salud, (20, 50))

    def dibujar(self):
        self.pantalla.fill((10, 12, 25))

        if self.escenario == 1:
            pygame.draw.rect(self.pantalla, (18, 40, 60), (0, 0, ANCHO_PANTALLA, ALTO_PANTALLA))
        elif self.escenario == 2:
            pygame.draw.rect(self.pantalla, (15, 24, 40), (0, 0, ANCHO_PANTALLA, ALTO_PANTALLA))
        else:
            pygame.draw.rect(self.pantalla, (28, 12, 24), (0, 0, ANCHO_PANTALLA, ALTO_PANTALLA))

        for obstaculo in self.obstaculos:
            obstaculo.dibujar(self.pantalla)

        for enemigo in self.enemigos:
            enemigo.dibujar(self.pantalla)

        if self.boss is not None:
            self.boss.dibujar(self.pantalla)

        self.jugador.dibujar(self.pantalla)

        for proyectil in self.proyectiles_jugador:
            proyectil.dibujar(self.pantalla)

        self.dibujar_hud()

        if self.estado != "jugando":
            overlay = pygame.Surface((ANCHO_PANTALLA, ALTO_PANTALLA), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            self.pantalla.blit(overlay, (0, 0))

            texto = self.font.render(self.texto_fin, True, (255, 255, 255))
            rect_texto = texto.get_rect(center=(ANCHO_PANTALLA // 2, ALTO_PANTALLA // 2))
            self.pantalla.blit(texto, rect_texto)

    def ejecutar(self):
        corriendo = True
        while corriendo:
            corriendo = self.manejar_eventos()
            self.actualizar()
            self.dibujar()
            pygame.display.flip()
            self.reloj.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
    pygame.display.set_caption("Ataque espacial")

    juego = Juego(pantalla)
    juego.ejecutar()


if __name__ == "__main__":
    main()
