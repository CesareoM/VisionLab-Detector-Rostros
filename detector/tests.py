
"""Pruebas unitarias y de integracion de VisionLab.
Ejecutar: python manage.py test detector -v 2
Las pruebas utilizan una base de datos temporal de Django.
"""

import base64
import json
from unittest.mock import patch

import cv2
import numpy as np
from django.test import Client, TestCase
from django.urls import reverse

from .models import DetectionRecord
from .services import detect_faces


def jpeg_data_url(image):
    success, data = cv2.imencode(".jpg", image)

    if not success:
        raise AssertionError("No se pudo codificar la imagen")

    encoded = base64.b64encode(data).decode("ascii")
    return "data:image/jpeg;base64," + encoded


class PruebasUnitariasOpenCV(TestCase):
    """Pruebas del modulo de deteccion facial."""

    def test_imagen_negra_sin_rostros(self):
        frame = np.zeros((200, 200, 3), dtype=np.uint8)
        resultado = detect_faces(frame)

        self.assertEqual(resultado, [])

    def test_formato_de_coordenadas(self):
        frame = np.zeros((200, 200, 3), dtype=np.uint8)

        with patch("detector.services.CASCADE") as cascade_mock:
            cascade_mock.detectMultiScale.return_value = np.array(
                [[10, 20, 60, 70]]
            )
            resultado = detect_faces(frame)

        esperado = [
            {
                "x": 10,
                "y": 20,
                "width": 60,
                "height": 70,
            }
        ]

        self.assertEqual(resultado, esperado)


class PruebasIntegracionDjango(TestCase):
    """Pruebas de rutas, solicitudes y almacenamiento."""

    def test_inicio_responde_200_y_csrf(self):
        respuesta = self.client.get(reverse("home"))

        self.assertEqual(respuesta.status_code, 200)
        self.assertIn("csrftoken", respuesta.cookies)
        self.assertContains(respuesta, "VisionLab")

    def test_analizar_rechaza_get(self):
        respuesta = self.client.get(reverse("analyze"))

        self.assertEqual(respuesta.status_code, 405)

    def test_guardar_rechaza_get(self):
        respuesta = self.client.get(reverse("save_count"))

        self.assertEqual(respuesta.status_code, 405)

    def test_analizar_rechaza_imagen_invalida(self):
        respuesta = self.client.post(
            reverse("analyze"),
            data=json.dumps({"image": "incorrecta"}),
            content_type="application/json",
        )

        self.assertEqual(respuesta.status_code, 400)

    def test_analizar_rechaza_json_malformado(self):
        respuesta = self.client.post(
            reverse("analyze"),
            data="{",
            content_type="application/json",
        )

        self.assertEqual(respuesta.status_code, 400)

    def test_analizar_rechaza_fotograma_excesivo(self):
        respuesta = self.client.post(
            reverse("analyze"),
            data="x" * 2_000_001,
            content_type="application/json",
        )

        self.assertEqual(respuesta.status_code, 413)

    def test_analizar_fotograma_negro(self):
        frame = np.zeros((200, 200, 3), dtype=np.uint8)

        respuesta = self.client.post(
            reverse("analyze"),
            data=json.dumps({"image": jpeg_data_url(frame)}),
            content_type="application/json",
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["count"], 0)
        self.assertEqual(respuesta.json()["boxes"], [])

    def test_analizar_dos_rostros_simulados(self):
        frame = np.zeros((200, 200, 3), dtype=np.uint8)

        rostros = [
            {"x": 5, "y": 10, "width": 40, "height": 50},
            {"x": 80, "y": 20, "width": 40, "height": 50},
        ]

        with patch(
            "detector.views.detect_faces",
            return_value=rostros,
        ):
            respuesta = self.client.post(
                reverse("analyze"),
                data=json.dumps({"image": jpeg_data_url(frame)}),
                content_type="application/json",
            )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json()["count"], 2)
        self.assertEqual(respuesta.json()["boxes"], rostros)

    def test_guardar_conteo_persiste_en_bd(self):
        respuesta = self.client.post(
            reverse("save_count"),
            data=json.dumps({"count": 2}),
            content_type="application/json",
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertTrue(respuesta.json()["saved"])

        registro = DetectionRecord.objects.get(
            pk=respuesta.json()["id"]
        )

        self.assertEqual(registro.face_count, 2)
        self.assertIsNotNone(registro.created_at)

    def test_guardar_cero_es_valido(self):
        respuesta = self.client.post(
            reverse("save_count"),
            data=json.dumps({"count": 0}),
            content_type="application/json",
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(
            DetectionRecord.objects.get().face_count,
            0,
        )

    def test_guardar_rechaza_numero_negativo(self):
        respuesta = self.client.post(
            reverse("save_count"),
            data=json.dumps({"count": -1}),
            content_type="application/json",
        )

        self.assertEqual(respuesta.status_code, 400)
        self.assertEqual(DetectionRecord.objects.count(), 0)

    def test_guardar_rechaza_decimal(self):
        respuesta = self.client.post(
            reverse("save_count"),
            data=json.dumps({"count": 1.5}),
            content_type="application/json",
        )

        self.assertEqual(respuesta.status_code, 400)

    def test_guardar_rechaza_mas_de_mil(self):
        respuesta = self.client.post(
            reverse("save_count"),
            data=json.dumps({"count": 1001}),
            content_type="application/json",
        )

        self.assertEqual(respuesta.status_code, 400)

    def test_guardar_rechaza_json_malformado(self):
        respuesta = self.client.post(
            reverse("save_count"),
            data="{",
            content_type="application/json",
        )

        self.assertEqual(respuesta.status_code, 400)

    def test_csrf_bloquea_post_sin_token(self):
        cliente = Client(enforce_csrf_checks=True)

        respuesta = cliente.post(
            reverse("save_count"),
            data=json.dumps({"count": 1}),
            content_type="application/json",
        )

        self.assertEqual(respuesta.status_code, 403)
        self.assertEqual(DetectionRecord.objects.count(), 0)