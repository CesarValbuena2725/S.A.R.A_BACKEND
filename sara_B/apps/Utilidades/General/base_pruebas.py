# tests/base_api_test.py
import unittest
from rest_framework.test import APITestCase
from rest_framework import status

class AbstractBaseAPI(APITestCase):
    model = None          # Modelo Django
    namemodel = ""        # Nombre en la URL
    validate_instancie= {}
    valid_data = {}       # Datos válidos para crear
    invalid_data = {}     # Datos inválidos

    def setUp(self):
        assert self.model is not None, "Debes definir un modelo en la subclase"
        assert self.namemodel != "", "Debes definir el namemodel"
        # Crear registro inicial
        self.instance = self.model.objects.create(**self.validate_instancie)

    def get_url(self, action, pk=None):
        if action == "post":
            return f"/api/{self.namemodel}/post/"
        return f"/api/{self.namemodel}/{action}/{pk}/"

    def _create_valid(self):
        url = self.get_url("post")
        response = self.client.post(url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def _create_invalid(self):
        url = self.get_url("post")
        response = self.client.post(url, self.invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _update_put(self):
        url = self.get_url("put", self.instance.id)
        response = self.client.put(url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def _patch(self):
        url = self.get_url("patch", self.instance.id)
        response = self.client.patch(url, self.valid_data, format="json")
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_202_ACCEPTED])

    def _delete(self):
        url = self.get_url("delete", self.instance.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)



