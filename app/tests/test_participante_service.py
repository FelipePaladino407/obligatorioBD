import unittest
from unittest.mock import patch
from datetime import date
from app.services.reserva_service import (
    validar_participantes_rol_sala,
    validar_capacidad
)
from app.models.reserva_model import ReservaCreate
from app.enums.estado_reserva import EstadoReserva


def dummy_reserva(participantes):
    return ReservaCreate(
        nombre_sala="Lab1",
        edificio="A",
        fecha=date.today(),
        id_turno=1,
        estado=EstadoReserva.ACTIVA,
        participantes_ci=participantes
    )


class TestValidarReserva(unittest.TestCase):

    # ----- validar_participantes_rol_sala -----

    @patch("app.services.reserva_service.get_participante_rol")
    @patch("app.services.reserva_service.get_sala")
    def test_uso_libre_permite_todos(self, mock_sala, mock_rol):
        mock_sala.return_value = {"tipo_sala": "uso_libre"}
        mock_rol.return_value = "estudiante_grado"

        validar_participantes_rol_sala(dummy_reserva(["1", "2"]))

    @patch("app.services.reserva_service.get_participante_rol")
    @patch("app.services.reserva_service.get_sala")
    def test_posgrado_permite_roles_validos(self, mock_sala, mock_rol):
        mock_sala.return_value = {"tipo_sala": "posgrado"}
        mock_rol.side_effect = ["estudiante_posgrado", "docente"]

        validar_participantes_rol_sala(dummy_reserva(["1", "2"]))

    @patch("app.services.reserva_service.get_participante_rol")
    @patch("app.services.reserva_service.get_sala")
    def test_posgrado_rechaza_grado(self, mock_sala, mock_rol):
        mock_sala.return_value = {"tipo_sala": "posgrado"}
        mock_rol.return_value = "estudiante_grado"

        with self.assertRaises(Exception):
            validar_participantes_rol_sala(dummy_reserva(["3"]))

    @patch("app.services.reserva_service.get_participante_rol")
    @patch("app.services.reserva_service.get_sala")
    def test_docente_solo_docentes(self, mock_sala, mock_rol):
        mock_sala.return_value = {"tipo_sala": "docente"}
        mock_rol.return_value = "docente"

        validar_participantes_rol_sala(dummy_reserva(["5"]))

    @patch("app.services.reserva_service.get_participante_rol")
    @patch("app.services.reserva_service.get_sala")
    def test_docente_rechaza_no_docente(self, mock_sala, mock_rol):
        mock_sala.return_value = {"tipo_sala": "docente"}
        mock_rol.return_value = "estudiante_posgrado"

        with self.assertRaises(Exception):
            validar_participantes_rol_sala(dummy_reserva(["10"]))

    # ----- validar_capacidad -----

    @patch("app.services.reserva_service.get_sala")
    def test_capacidad_ok(self, mock_sala):
        mock_sala.return_value = {"capacidad": 3}
        validar_capacidad(dummy_reserva(["1", "2", "3"]))

    @patch("app.services.reserva_service.get_sala")
    def test_capacidad_excedida(self, mock_sala):
        mock_sala.return_value = {"capacidad": 2}

        with self.assertRaises(Exception):
            validar_capacidad(dummy_reserva(["1", "2", "3"]))


if __name__ == "__main__":
    unittest.main()

