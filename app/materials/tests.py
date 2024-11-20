from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from materials.conftest import create_material, create_category



class CategoryAPITest(APITestCase):
    def setUp(self):
        self.category1 = create_category('Test Category')
        self.category2 = create_category('Test Category 2', parent_id=self.category1)
        self.category3 = create_category('Test Category 3')
        self.url_list = reverse('categories-list')
        self.url_flat_list = reverse('categories-flat')
        self.url_tree = reverse('categories-tree')

    def test_list_categories(self):
        response = self.client.get(self.url_list)
        self.assertEqual(response.data['count'], 3)
        self.assertIn('name', response.data['results'][0])

    def test_flat_categories(self):
        response = self.client.get(self.url_flat_list)
        self.assertEqual(len(response.data), 3)
        self.assertEqual('Test Category', response.data[0])
        self.assertEqual('Test Category 2', response.data[1])
        self.assertEqual('Test Category 3', response.data[2])

    def test_create_category(self):
        data = {
            'name': 'TEST CREATE CATEGORY',
        }
        response = self.client.post(self.url_list, data=data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['parent'], None)

    def test_update_category(self):
        data = {
            'name': 'PUT Test'
        }
        url = reverse('categories-detail', kwargs={'pk': self.category1.id})
        response = self.client.put(url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], data['name'])

    def test_delete_category(self):
        url = reverse('categories-detail', kwargs={'pk': self.category3.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)


class MaterialAPITest(APITestCase):
    def setUp(self):
        self.category = create_category(
            name='Test Category'
        )
        self.sub_category = create_category(
            name='Test SubCategory',
            parent_id=self.category
        )
        self.data = {
            'name': 'Test Material',
            'article': 123456,
            'price': 2000,
            'subcategory': self.sub_category.id
        }

        self.url_get = reverse('materials-list')
        self.material = create_material(
            self.data,
            category_id=self.sub_category.id
        )

    def test_get_materials(self):
        response = self.client.get(self.url_get)
        result = response.data['results']
        self.assertEqual(result[0]['name'], self.data['name'])
        self.assertEqual(result[0]['article'], self.data['article'])
        self.assertEqual(result[0]['price'], self.data['price'])
        self.assertEqual(result[0]['category'], self.data['subcategory'])


    def test_create_materials(self):
        url = reverse('materials-list')
        response = self.client.post(url, data=self.data)

        result = response.data
        self.assertEqual(result['name'], self.data['name'])
        self.assertEqual(result['article'], self.data['article'])
        self.assertEqual(result['price'], self.data['price'])
        self.assertEqual(result['category'], self.data['subcategory'])

    def test_patch_materials(self):
        url = reverse('materials-detail', kwargs={'pk': self.material.id})
        patch_data = {'name': 'Patched Test Material'}
        response = self.client.patch(url, data=patch_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], patch_data['name'])

    def test_put_materials(self):
        url = reverse('materials-detail', kwargs={'pk': self.material.id})
        put_data = {
            'name': 'Patched Test Material',
            'article': 12345,
            'price': 5000
        }
        response = self.client.put(url, data=put_data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], put_data['name'])
        self.assertEqual(response.data['article'], put_data['article'])
        self.assertEqual(response.data['price'], put_data['price'])
