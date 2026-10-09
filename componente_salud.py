import math


class ComponenteSalud:
    def __init__(self, vida_inicial):
        self._validar_cantidad(vida_inicial, "La vida inicial")
        if vida_inicial <= 0:
            raise ValueError("La vida inicial debe ser mayor que cero.")

        self._vida_actual = vida_inicial

    @property
    def vida_actual(self):
        return self._vida_actual

    @staticmethod
    def _validar_cantidad(cantidad, nombre):
        if (
            isinstance(cantidad, bool)
            or not isinstance(cantidad, (int, float))
            or (isinstance(cantidad, float) and not math.isfinite(cantidad))
        ):
            raise TypeError(f"{nombre} debe ser un número finito.")

    def recibir_dano(self, cantidad):
        self._validar_cantidad(cantidad, "El daño")
        if cantidad < 0:
            raise ValueError("El daño no puede ser negativo.")

        self._vida_actual = max(0, self._vida_actual - cantidad)
        return self.vida_actual

    def establecer_vida(self, cantidad):
        self._validar_cantidad(cantidad, "La vida")
        if cantidad < 0:
            raise ValueError("La vida no puede ser negativa.")

        self._vida_actual = cantidad

    def esta_vivo(self):
        return self.vida_actual > 0
