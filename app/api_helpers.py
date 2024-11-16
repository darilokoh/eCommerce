import requests
from django.conf import settings

# Helper for Product API
class ProductAPI:
    @staticmethod
    def get_product(id):
        url = f"{settings.API_BASE_URL}product/{id}/"
        response = requests.get(url)
        if response.status_code == 200:
            product_data = response.json()
            product_data.pop('image', None)
            return product_data
        else:
            print(f'Error al obtener el producto: {response.content}')
            return None

    @staticmethod
    def get_products(params=None):
        url = f"{settings.API_BASE_URL}product/"
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        return []

    @staticmethod
    def create_product(data, files=None):
        url = f"{settings.API_BASE_URL}product/"
        response = requests.post(url, data=data, files=files)
        return response

    @staticmethod
    def update_product(id, data, files=None):
        url = f"{settings.API_BASE_URL}product/{id}/"
        response = requests.put(url, data=data, files=files)
        return response

    @staticmethod
    def delete_product(id):
        url = f"{settings.API_BASE_URL}product/{id}/"
        response = requests.delete(url)
        return response
    
# Helper for Location API
class LocationAPI:
    @staticmethod
    def get_regions():
        url = f"{settings.API_BASE_URL}regions/"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error al obtener las regiones: {response.content}")
            return []

    @staticmethod
    def get_municipalities(region_id=None):
        url = f"{settings.API_BASE_URL}municipalities/"
        params = {"region_id": region_id} if region_id else {}
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error al obtener las comunas: {response.content}")
            return []