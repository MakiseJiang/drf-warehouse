from rest_framework.test import APITestCase
from rest_framework import status
from .models import Material


class MaterialAPITests(APITestCase):
    def setUp(self):
        for i in range(15):
            Material.objects.create(
                material_id=f"M{i}",
                name=f"Item{i}",
                model_number=f"MN{i}",
                category="Cat",
                equipment="Equip",
                warehouse="W1",
                shelf="S1",
                quantity=i,
            )

    def test_list_materials(self):
        url = '/api/materials/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 10)

    def test_pagination_second_page(self):
        url = '/api/materials/?page=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)

    def test_search(self):
        url = '/api/materials/?search=M1'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(item['material_id'] == 'M1' for item in response.data['results']))

    def test_create(self):
        url = '/api/materials/'
        payload = {
            "material_id": "NEW1",
            "name": "New",
            "model_number": "ModelX",
            "category": "CatX",
            "equipment": "EquipX",
            "warehouse": "W2",
            "shelf": "S2",
            "quantity": 10,
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Material.objects.count(), 16)

    def test_retrieve_update_delete(self):
        m = Material.objects.create(
            material_id="TEMP",
            name="Tmp",
            model_number="T1",
            category="Cat",
            equipment="Eq",
            warehouse="W",
            shelf="S",
            quantity=1,
        )
        url = f'/api/materials/{m.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        patch = {"quantity": 5}
        response = self.client.patch(url, patch, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Material.objects.get(id=m.id).quantity, 5)
        put = {
            "material_id": "TEMP",
            "name": "Tmp2",
            "model_number": "T2",
            "category": "Cat2",
            "equipment": "Eq2",
            "warehouse": "W2",
            "shelf": "S2",
            "quantity": 7,
        }
        response = self.client.put(url, put, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Material.objects.filter(id=m.id).exists())

    def test_unique_material_id(self):
        url = '/api/materials/'
        payload = {
            "material_id": "M1",
            "name": "Dup",
            "model_number": "D",
            "category": "C",
            "equipment": "E",
            "warehouse": "W",
            "shelf": "S",
            "quantity": 1,
        }
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)