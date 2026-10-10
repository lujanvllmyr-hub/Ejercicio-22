import pygame


class BotonUI:
    COLOR_FONDO = (40, 100, 150)
    COLOR_FONDO_RESALTADO = (70, 145, 200)
    COLOR_BORDE = (180, 220, 255)
    COLOR_TEXTO = (255, 255, 255)

    def __init__(self, x, y, ancho, alto, texto):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.font = pygame.font.SysFont(None, 36)
        self.color_fondo = self.COLOR_FONDO

    def comprobar_clic(self, posicion_mouse, clic_izquierdo):
        return clic_izquierdo and self.rect.collidepoint(posicion_mouse)

    def actualizar(self, posicion_mouse):
        if self.rect.collidepoint(posicion_mouse):
            self.color_fondo = self.COLOR_FONDO_RESALTADO
        else:
            self.color_fondo = self.COLOR_FONDO

    def dibujar(self, pantalla):
        pygame.draw.rect(pantalla, self.color_fondo, self.rect)
        pygame.draw.rect(pantalla, self.COLOR_BORDE, self.rect, 2)
        superficie_texto = self.font.render(self.texto, True, self.COLOR_TEXTO)
        ancho_texto, alto_texto = superficie_texto.get_size()
        x_texto = self.rect.x + (self.rect.width / 2) - (ancho_texto / 2)
        y_texto = self.rect.y + (self.rect.height / 2) - (alto_texto / 2)
        pantalla.blit(superficie_texto, (round(x_texto), round(y_texto)))


class GestorUI:
    ANCHO_BARRA_SALUD = 200
    ALTO_BARRA_SALUD = 18
    POSICION_BARRA_SALUD = (20, 80)
    COLOR_FONDO_SALUD = (80, 30, 30)
    COLOR_SALUD = (60, 210, 90)
    COLOR_BORDE = (255, 255, 255)

    def dibujar_barra_salud(self, pantalla, salud_actual, salud_maxima):
        if salud_maxima <= 0:
            raise ValueError("La salud máxima debe ser mayor que cero.")

        salud_actual = max(0, min(salud_actual, salud_maxima))
        ancho_actual = int(
            (salud_actual / salud_maxima) * self.ANCHO_BARRA_SALUD
        )
        barra = pygame.Rect(
            *self.POSICION_BARRA_SALUD,
            self.ANCHO_BARRA_SALUD,
            self.ALTO_BARRA_SALUD,
        )

        pygame.draw.rect(pantalla, self.COLOR_FONDO_SALUD, barra)
        if ancho_actual > 0:
            pygame.draw.rect(
                pantalla,
                self.COLOR_SALUD,
                (barra.x, barra.y, ancho_actual, barra.height),
            )
        pygame.draw.rect(pantalla, self.COLOR_BORDE, barra, 2)
