from pathlib import Path

import pygame


class GestorAudio:
    """Gestiona la música de fondo y los efectos de sonido del juego."""

    def __init__(self):
        self._efectos: dict[Path, pygame.mixer.Sound] = {}

    @staticmethod
    def _validar_mixer():
        if pygame.mixer.get_init() is None:
            raise RuntimeError(
                "El mixer de Pygame no está inicializado. "
                "Inicializa pygame.mixer antes de reproducir audio."
            )

    def reproducir_musica(self, ruta_archivo):
        """Reproduce música de fondo en bucle hasta que se cambie o detenga."""
        self._validar_mixer()
        pygame.mixer.music.load(str(ruta_archivo))
        pygame.mixer.music.play(loops=-1)

    def reproducir_efecto(self, ruta_archivo):
        """Reproduce un efecto corto; llamadas sucesivas pueden superponerse."""
        self._validar_mixer()
        ruta = Path(ruta_archivo).resolve()
        efecto = self._efectos.get(ruta)
        if efecto is None:
            efecto = pygame.mixer.Sound(str(ruta))
            self._efectos[ruta] = efecto

        efecto.play()
