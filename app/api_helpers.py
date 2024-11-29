import requests
from django.conf import settings
from datetime import datetime, timedelta
from rest_framework import serializers

# Helpers for Product API
class ProductAPI:
    @staticmethod
    def get_product(id, exclude_image=False):
        """
        Obtiene los detalles de un producto desde la API.

        Args:
            id (int): ID del producto a obtener.
            exclude_image (bool): Si es True, elimina el campo 'image' del resultado.

        Returns:
            dict | None: Datos del producto si la solicitud fue exitosa, None en caso contrario.
        """
        url = f"{settings.API_BASE_URL}product/{id}/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                product_data = response.json()
                if exclude_image:
                    product_data.pop('image', None)
                return product_data
            else:
                print(f"Error al obtener el producto: {response.status_code}, {response.content}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Excepción al obtener el producto: {str(e)}")
            return None
        
    @staticmethod
    def check_duplicate_product(name, exclude_id=None):
        """
        Verifica si existe un producto con el mismo nombre a través de la API,
        excluyendo un producto específico si se proporciona un ID.

        Args:
            name (str): Nombre del producto.
            exclude_id (int, optional): ID del producto a excluir de la verificación.

        Returns:
            bool: True si existe un producto duplicado, False en caso contrario.
        """
        url = f"{settings.API_BASE_URL}product/"
        params = {'name': name}
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                products = response.json()
                # Verificar si hay productos con el mismo nombre excluyendo el ID proporcionado
                for product in products:
                    if product['name'].lower() == name.lower() and product['id'] != exclude_id:
                        return True
                return False
            else:
                print(f"Error al verificar duplicados: {response.status_code}, {response.content}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Excepción al verificar duplicados: {str(e)}")
            return False
        
    @staticmethod
    def create_product(data, files=None):
        """
        Crea un producto a través de la API.
    
        Args:
            data (dict): Datos del producto.
            files (dict): Archivos relacionados, como la imagen.
    
        Returns:
            dict | None: Respuesta de la API si es exitosa, None en caso contrario.
        """
        url = f"{settings.API_BASE_URL}product/"
        try:
            response = requests.post(url, data=data, files=files)
            if response.status_code == 201:
                return response.json()
            else:
                print(f"Error al crear el producto: {response.status_code}, {response.content}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Excepción al crear el producto: {str(e)}")
            return None
    
    @staticmethod
    def get_products_by_ids(ids):
        """
        Obtiene una lista de productos por sus IDs a través del API.

        Args:
            ids (list): Lista de IDs de los productos.

        Returns:
            list: Lista de productos obtenidos desde la API.
        """
        if not ids:
            return []

        # Filtramos productos por IDs utilizando un parámetro "id__in"
        url = f"{settings.API_BASE_URL}product/"
        params = {'id__in': ','.join(map(str, ids))}

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f'Error al obtener productos por IDs: {response.status_code}, {response.content}')
                return []
        except Exception as e:
            print(f"Excepción al obtener productos por IDs: {str(e)}")
            return []

    @staticmethod
    def list_products(params=None):
        """
        Obtiene una lista de productos desde la API con los filtros opcionales.

        Args:
            params (dict): Filtros para la búsqueda de productos.

        Returns:
            list: Lista de productos.
        """
        url = f"{settings.API_BASE_URL}product/"
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error al obtener productos: {response.status_code}, {response.content}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Excepción al obtener productos: {str(e)}")
            return []
        
    @staticmethod
    def update_product(id, data, files=None):
        """
        Actualiza un producto a través de la API.

        Args:
            id (int): ID del producto a actualizar.
            data (dict): Datos del producto.
            files (dict): Archivos relacionados, como la imagen.

        Returns:
            dict | None: Respuesta de la API si es exitosa, None en caso contrario.
        """
        url = f"{settings.API_BASE_URL}product/{id}/"
        try:
            response = requests.put(url, data=data, files=files)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error al actualizar el producto: {response.status_code}, {response.content}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Excepción al actualizar el producto: {str(e)}")
            return None
        
    @staticmethod
    def update_product_stock(id, data, files=None, use_patch=False):
        """
        Actualiza un producto a través de la API.

        Args:
            id (int): ID del producto a actualizar.
            data (dict): Datos del producto.
            files (dict): Archivos relacionados, como la imagen.
            use_patch (bool): Si es True, usa PATCH en lugar de PUT.

        Returns:
            dict | None: Respuesta de la API si es exitosa, None en caso contrario.
        """
        url = f"{settings.API_BASE_URL}product/{id}/"
        try:
            # Selecciona el método HTTP según use_patch
            if use_patch:
                response = requests.patch(url, data=data, files=files)
            else:
                response = requests.put(url, data=data, files=files)

            # Verifica el estado de la respuesta
            if response.status_code in [200, 204]:
                return response.json() if response.status_code == 200 else {"success": True}
            else:
                print(f"Error al actualizar el producto: {response.status_code}, {response.content}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Excepción al actualizar el producto: {str(e)}")
            return None
        
    @staticmethod
    def delete_product(id):
        """
        Elimina un producto a través de la API.

        Args:
            id (int): ID del producto a eliminar.

        Returns:
            bool: True si la eliminación fue exitosa, False en caso contrario.
        """
        url = f"{settings.API_BASE_URL}product/{id}/"
        try:
            response = requests.delete(url)
            if response.status_code == 204:
                return True
            else:
                print(f"Error al eliminar el producto: {response.status_code}, {response.content}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Excepción al eliminar el producto: {str(e)}")
            return False
    
# Helpers for Category API
class CategoryAPI:
    @staticmethod
    def get_categories(exclude_ids=None):
        """
        Obtiene las categorías desde la API, excluyendo las que tengan IDs en exclude_ids.
        """
        url = f"{settings.API_BASE_URL}category/"
        response = requests.get(url)
        if response.status_code == 200:
            categories = response.json()
            # Filtrar categorías si exclude_ids está definido
            if exclude_ids:
                categories = [
                    category for category in categories if category['id'] not in exclude_ids
                ]
            return categories
        return []
    
    @staticmethod
    def get_category_by_id(category_id, exclude_image=False):
        """
        Obtiene una categoría específica por su ID a través de la API.

        Args:
            category_id (int): ID de la categoría a obtener.
            exclude_image (bool): Si es True, elimina el campo 'image' del resultado.

        Returns:
            dict | None: Datos de la categoría si la solicitud fue exitosa, None en caso contrario.
        """
        url = f"{settings.API_BASE_URL}category/{category_id}/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                category_data = response.json()
                if exclude_image:
                    category_data.pop('image', None)
                return category_data
            else:
                print(f"Error al obtener la categoría: {response.status_code}, {response.content}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Excepción al obtener la categoría: {str(e)}")
            return None
        
    @staticmethod
    def create_category(data, files=None):
        """
        Crea una categoría a través de la API.

        Args:
            data (dict): Datos de la categoría.
            files (dict): Archivos relacionados, como la imagen.

        Returns:
            dict | None: Respuesta de la API si es exitosa, None en caso contrario.
        """
        url = f"{settings.API_BASE_URL}category/"
        try:
            response = requests.post(url, data=data, files=files)
            if response.status_code == 201:
                return response.json()
            else:
                print(f"Error al crear la categoría: {response.status_code}, {response.content}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Excepción al crear la categoría: {str(e)}")
            return None
        
    @staticmethod
    def check_duplicate_category(name, exclude_id=None):
        """
        Verifica si existe una categoría con el mismo nombre a través de la API,
        excluyendo una categoría específica si se proporciona un ID.

        Args:
            name (str): Nombre de la categoría.
            exclude_id (int, optional): ID de la categoría a excluir de la verificación.

        Returns:
            bool: True si existe una categoría duplicada, False en caso contrario.
        """
        if exclude_id is not None:
            exclude_id = int(exclude_id)  # Asegurar que exclude_id sea un entero

        url = f"{settings.API_BASE_URL}category/"
        params = {'name': name}
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                categories = response.json()
                # Verificar si hay categorías con el mismo nombre excluyendo el ID proporcionado
                for category in categories:
                    if category['name'].lower() == name.lower() and category['id'] != exclude_id:
                        return True
                return False
            else:
                print(f"Error al verificar duplicados: {response.status_code}, {response.content}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Excepción al verificar duplicados: {str(e)}")
            return False

    @staticmethod
    def update_category(category_id, data, files=None):
        """
        Actualiza una categoría a través de la API.

        Args:
            category_id (int): ID de la categoría a actualizar.
            data (dict): Datos de la categoría a actualizar.
            files (dict, optional): Archivos relacionados, como la imagen.

        Returns:
            dict | None: Respuesta de la API si es exitosa, None en caso contrario.
        """
        url = f"{settings.API_BASE_URL}category/{category_id}/"
        try:
            response = requests.put(url, data=data, files=files)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error al actualizar la categoría: {response.status_code}, {response.content}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Excepción al actualizar la categoría: {str(e)}")
            return None
        
    @staticmethod
    def delete_category(category_id):
        """
        Elimina una categoría a través de la API.

        Args:
            category_id (int): ID de la categoría a eliminar.

        Returns:
            bool: True si la eliminación fue exitosa, False en caso contrario.
        """
        url = f"{settings.API_BASE_URL}category/{category_id}/"
        try:
            response = requests.delete(url)
            if response.status_code == 204:
                return True
            else:
                print(f"Error al eliminar la categoría: {response.status_code}, {response.content}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Excepción al eliminar la categoría: {str(e)}")
            return False

#Helpers for Contact API
class ContactAPI:
    @staticmethod
    def update_contact_status(contact_id, status):
        """
        Actualiza el estado de un contacto a través de la API.

        Args:
            contact_id (int): ID del contacto.
            status (str): Nuevo estado del contacto.

        Returns:
            dict | None: Respuesta de la API si es exitosa, None en caso de error.
        """
        url = f"{settings.API_BASE_URL}contact/{contact_id}/"
        payload = {"status": status}

        try:
            response = requests.patch(url, json=payload)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error al actualizar el estado del contacto: {response.status_code}, {response.content}")
                return None
        except Exception as e:
            print(f"Excepción al actualizar el estado del contacto: {str(e)}")
            return None
        
    @staticmethod
    def list_contacts(filters=None):
        """
        Obtiene una lista de contactos desde la API.

        Args:
            filters (dict): Parámetros opcionales para filtrar los contactos.

        Returns:
            list: Lista de contactos.
        """
        url = f"{settings.API_BASE_URL}contact/"
        try:
            response = requests.get(url, params=filters)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error al obtener contactos: {response.status_code}, {response.content}")
                return []
        except Exception as e:
            print(f"Excepción al obtener contactos: {str(e)}")
            return []

# Helpers for QueryTypeAPI
class QueryTypeAPI:
    @staticmethod
    def list_query_types():
        """
        Obtiene una lista de tipos de consulta desde la API.

        Returns:
            list: Lista de tipos de consulta.
        """
        url = f"{settings.API_BASE_URL}query-type/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error al obtener tipos de consulta: {response.status_code}, {response.content}")
                return []
        except Exception as e:
            print(f"Excepción al obtener tipos de consulta: {str(e)}")
            return []
        
    @staticmethod
    def get_object_query_type(id):
        """
        Obtiene un tipo de consulta específico por ID desde la API.

        Args:
            id (int): ID del tipo de consulta.

        Returns:
            dict | None: Datos del tipo de consulta si se encuentra, None en caso contrario.
        """
        url = f"{settings.API_BASE_URL}query-type/{id}/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error al obtener el tipo de consulta: {response.status_code}, {response.content}")
                return None
        except Exception as e:
            print(f"Excepción al obtener el tipo de consulta: {str(e)}")
            return None
        
    @staticmethod
    def create_query_type(data):
        """
        Crea un nuevo tipo de consulta a través de la API.

        Args:
            data (dict): Datos del tipo de consulta a crear.

        Returns:
            dict | None: Datos del tipo de consulta creado si es exitoso, None en caso de error.
        """
        url = f"{settings.API_BASE_URL}query-type/"
        try:
            response = requests.post(url, json=data)
            if response.status_code == 201:
                return response.json()
            elif response.status_code == 400:
                raise serializers.ValidationError(response.json())
            else:
                print(f"Error al crear el tipo de consulta: {response.status_code}, {response.content}")
                return None
        except Exception as e:
            print(f"Excepción al crear el tipo de consulta: {str(e)}")
            return None
        
    @staticmethod
    def check_duplicate_query_type(name, exclude_id=None):
        """
        Verifica si existe un tipo de consulta con el mismo nombre.

        Args:
            name (str): Nombre del tipo de consulta.
            exclude_id (int): ID a excluir en la verificación (para evitar conflicto con el actual).

        Returns:
            bool: True si existe un duplicado, False en caso contrario.
        """
        url = f"{settings.API_BASE_URL}query-type/"
        params = {"name": name}
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                query_types = response.json()
                for query_type in query_types:
                    # Verifica si el nombre coincide y no es el mismo ID
                    if query_type['name'].lower() == name.lower() and query_type['id'] != exclude_id:
                        return True
                return False
            else:
                print(f"Error al verificar duplicados: {response.status_code}, {response.content}")
                return False
        except Exception as e:
            print(f"Excepción al verificar duplicados: {str(e)}")
            return False
        
    @staticmethod
    def update_query_type(id, data):
        """
        Actualiza un tipo de consulta a través de la API.

        Args:
            id (int): ID del tipo de consulta.
            data (dict): Datos actualizados del tipo de consulta.

        Returns:
            bool: True si la actualización fue exitosa, False en caso contrario.
        """
        url = f"{settings.API_BASE_URL}query-type/{id}/"
        try:
            response = requests.put(url, json=data)
            if response.status_code == 200:
                return True
            else:
                print(f"Error al actualizar el tipo de consulta: {response.status_code}, {response.content}")
                return False
        except Exception as e:
            print(f"Excepción al actualizar el tipo de consulta: {str(e)}")
            return False
        
    @staticmethod
    def delete_query_type(id):
        """
        Elimina un tipo de consulta a través de la API.

        Args:
            id (int): ID del tipo de consulta a eliminar.

        Returns:
            bool: True si la eliminación fue exitosa, False en caso contrario.
        """
        url = f"{settings.API_BASE_URL}query-type/{id}/"
        try:
            response = requests.delete(url)
            if response.status_code == 204:
                return True
            else:
                print(f"Error al eliminar el tipo de consulta: {response.status_code}, {response.content}")
                return False
        except Exception as e:
            print(f"Excepción al eliminar el tipo de consulta: {str(e)}")
            return False

# Helpers for RentalOrder API
class RentalOrderAPI:
    @staticmethod
    def create_rental_order(data):
        """
        Crea una orden de renta en la API.
        Args:
            data (dict): Datos para la orden de renta.
        Returns:
            dict | None: Respuesta de la API en formato JSON si tiene éxito, None en caso de error.
        """
        url = f"{settings.API_BASE_URL}rental-orders/"
        try:
            response = requests.post(url, json=data)
            if response.status_code == 201:
                return response.json()
            else:
                print(f"Error al crear la orden de renta: {response.status_code}, {response.content}")
                return None
        except Exception as e:
            print(f"Excepción al crear la orden de renta: {str(e)}")
            return None

    @staticmethod
    def get_rental_orders(params=None):
        """
        Obtiene una lista de órdenes de renta desde la API.
        Args:
            params (dict): Parámetros para filtrar las órdenes.
        Returns:
            list: Lista de órdenes de renta.
        """
        url = f"{settings.API_BASE_URL}rental-orders/"
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error al obtener órdenes de renta: {response.status_code}, {response.content}")
                return []
        except Exception as e:
            print(f"Excepción al obtener órdenes de renta: {str(e)}")
            return []

    @staticmethod
    def get_rental_order_by_id(order_id):
        """
        Obtiene una orden de renta específica por ID.
        Args:
            order_id (int): ID de la orden de renta.
        Returns:
            dict | None: Datos de la orden de renta si existe, None en caso contrario.
        """
        url = f"{settings.API_BASE_URL}rental-orders/{order_id}/"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error al obtener la orden de renta: {response.status_code}, {response.content}")
                return None
        except Exception as e:
            print(f"Excepción al obtener la orden de renta: {str(e)}")
            return None

    @staticmethod
    def update_rental_order(order_id, data):
        """
        Actualiza una orden de renta por ID.
        Args:
            order_id (int): ID de la orden de renta.
            data (dict): Datos actualizados de la orden de renta.
        Returns:
            bool: True si la actualización fue exitosa, False en caso contrario.
        """
        url = f"{settings.API_BASE_URL}rental-orders/{order_id}/"
        try:
            response = requests.put(url, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Excepción al actualizar la orden de renta: {str(e)}")
            return False

    @staticmethod
    def delete_rental_order(order_id):
        """
        Elimina una orden de renta por ID.
        Args:
            order_id (int): ID de la orden de renta.
        Returns:
            bool: True si la eliminación fue exitosa, False en caso contrario.
        """
        url = f"{settings.API_BASE_URL}rental-orders/{order_id}/"
        try:
            response = requests.delete(url)
            return response.status_code == 204
        except Exception as e:
            print(f"Excepción al eliminar la orden de renta: {str(e)}")
            return False

    @staticmethod
    def check_duplicate_order(rut, time_window_minutes=15):
        """
        Verifica si existe una orden de renta duplicada dentro de un rango de tiempo.

        Args:
            rut (str): RUT del cliente.
            time_window_minutes (int): Rango de tiempo en minutos para verificar duplicados.

        Returns:
            bool: True si existe una orden duplicada, False en caso contrario.
        """
        url = f"{settings.API_BASE_URL}rental-orders/"
        # Calculamos la fecha y hora límite
        time_threshold = datetime.now() - timedelta(minutes=time_window_minutes)
        try:
            response = requests.get(url, params={'rut': rut})
            if response.status_code == 200:
                orders = response.json()
                for order in orders:
                    # Parsear el campo created_at para su comparación
                    order_created_at = datetime.strptime(order["created_at"], "%d-%m-%Y %H:%M")
                    if order_created_at >= time_threshold:
                        return True
                return False
            else:
                print(f"Error al verificar duplicados: {response.status_code}, {response.content}")
                return False
        except Exception as e:
            print(f"Excepción al verificar duplicados: {str(e)}")
            return False

    @staticmethod
    def list_rental_orders(params=None):
        """
        Obtiene una lista de órdenes de renta desde la API con filtros opcionales.
        """
        url = f"{settings.API_BASE_URL}rental-orders/"
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error al obtener órdenes de renta: {response.status_code}, {response.content}")
                return []
        except Exception as e:
            print(f"Excepción al obtener órdenes de renta: {str(e)}")
            return []
         
# Helpers for RentalOrderItem API
class RentalOrderItemAPI:
        
    @staticmethod
    def bulk_create_rental_order_items(order_id, products_selected, quantities):
        """
        Crea múltiples RentalOrderItems en la API.
    
        Args:
            order_id (int): ID de la orden de renta.
            products_selected (list): Lista de IDs de productos seleccionados.
            quantities (list): Lista de cantidades correspondientes a los productos.
    
        Returns:
            bool: True si todos los items se crearon correctamente, False si alguno falló.
        """
        for product_id, quantity in zip(products_selected, quantities):
            # Obtener datos del producto desde la API
            product = ProductAPI.get_product(product_id)
            if not product:
                print(f"Error al obtener los datos del producto con ID {product_id}")
                return False
    
            # Crear el RentalOrderItem en la API
            item_created = RentalOrderItemAPI.create_rental_order_item(
                order_id=order_id,
                product_id=product_id,
                product_name=product['name'],
                product_price=product['price'],
                quantity=quantity
            )
            if not item_created:
                print(f"Error al crear RentalOrderItem para el producto ID {product_id}")
                return False
    
        return True
    
    @staticmethod
    def create_rental_order_item(order_id, product_id, product_name, product_price, quantity):
        """
        Crea un RentalOrderItem en la API.
    
        Args:
            order_id (int): ID de la orden de renta.
            product_id (int): ID del producto.
            product_name (str): Nombre del producto.
            product_price (float): Precio del producto.
            quantity (int): Cantidad del producto.
    
        Returns:
            dict | None: Respuesta de la API si es exitosa, None en caso contrario.
        """
        url = f"{settings.API_BASE_URL}rental-order-items/"
        payload = {
            "rental_order": order_id,  # Clave foránea enviada como ID
            "product_name": product_name,
            "product_price": product_price,
            "amount": quantity
        }
    
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 201:
                return response.json()
            else:
                print(f"Error al crear RentalOrderItem: {response.status_code}, {response.content}")
                return None
        except Exception as e:
            print(f"Excepción al crear RentalOrderItem: {str(e)}")
            return None

    @staticmethod
    def get_items_by_order(order_id):
        """
        Obtiene todos los items de una orden de renta específica desde la API.

        Args:
            order_id (int): ID de la orden de renta.

        Returns:
            list: Lista de items de la orden obtenidos desde la API.
        """
        url = f"{settings.API_BASE_URL}rental-order-items/"
        params = {'rental_order_id': order_id}  # Filtramos por ID de la orden

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()  # Lista de items
            else:
                print(f"Error al obtener items por orden: {response.status_code}, {response.content}")
                return []
        except Exception as e:
            print(f"Excepción al obtener items por orden: {str(e)}")
            return []

    @staticmethod
    def delete_items_by_order(order_id):
        """
        Elimina todos los items relacionados con una orden de renta específica a través de la API.

        Args:
            order_id (int): ID de la orden de renta.

        Returns:
            bool: True si los items fueron eliminados exitosamente, False en caso contrario.
        """
        url = f"{settings.API_BASE_URL}rental-order-items/"
        params = {'rental_order_id': order_id}  # Pasamos el ID de la orden como filtro

        try:
            response = requests.delete(url, params=params)
            if response.status_code == 204:  # Código 204 indica eliminación exitosa
                return True
            else:
                print(f"Error al eliminar items por orden: {response.status_code}, {response.content}")
                return False
        except Exception as e:
            print(f"Excepción al eliminar items por orden: {str(e)}")
            return False
        
# Helpers for Order API
class OrderAPI:
    @staticmethod
    def get_last_order_by_user(user_id):
        """
        Obtiene la última orden de un usuario por ID.
        """
        url = f"{settings.API_BASE_URL}orders/"
        params = {'user': user_id}
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                orders = response.json()
                # Devuelve la última orden según el ID más alto
                if orders:
                    return max(orders, key=lambda x: x["order_id"])
                return None
            else:
                print(f"Error al obtener órdenes: {response.status_code}, {response.content}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Excepción al obtener órdenes: {str(e)}")
            return None

    @staticmethod
    def update_order(order_id, data):
        """
        Actualiza una orden específica.
        """
        url = f"{settings.API_BASE_URL}orders/{order_id}/"
        try:
            response = requests.put(url, data=data)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error al actualizar la orden: {response.status_code}, {response.content}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Excepción al actualizar la orden: {str(e)}")
            return None
        
    @staticmethod
    def create_order(data):
        """
        Crea una orden a través de la API.

        Args:
            data (dict): Datos de la orden.

        Returns:
            dict | None: Respuesta de la API si es exitosa, None en caso contrario.
        """
        url = f"{settings.API_BASE_URL}orders/"
        try:
            response = requests.post(url, json=data)
            if response.status_code == 201:
                return response.json()
            else:
                print(f"Error al crear la orden: {response.status_code}, {response.content}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Excepción al crear la orden: {str(e)}")
            return None
        
    @staticmethod
    def list_orders(params):
        url = f"{settings.API_BASE_URL}orders/"
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                # Verifica si el resultado es una lista o un diccionario
                data = response.json()
                if isinstance(data, list):  # Si es una lista, envuélvela en un diccionario
                    return {'results': data, 'paginator': {}}
                return data  # Si ya es un diccionario, retorna tal cual
            else:
                print(f"Error al obtener órdenes: {response.status_code}, {response.content}")
                return {'results': [], 'paginator': {}}
        except requests.exceptions.RequestException as e:
            print(f"Excepción al obtener órdenes: {str(e)}")
            return {'results': [], 'paginator': {}}

    @staticmethod
    def get_statistics(params):
        url = f"{settings.API_BASE_URL}orders/statistics/"
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error al obtener estadísticas: {response.status_code}, {response.content}")
                return {}
        except requests.exceptions.RequestException as e:
            print(f"Excepción al obtener estadísticas: {str(e)}")
            return {}
        
# Helpers for OrderItem API
class OrderItemAPI:
    @staticmethod
    def create_order_item(data):
        """
        Crea un ítem de orden a través de la API.

        Args:
            data (dict): Datos del ítem de la orden.

        Returns:
            dict | None: Respuesta de la API si es exitosa, None en caso contrario.
        """
        url = f"{settings.API_BASE_URL}order-items/"
        try:
            response = requests.post(url, data=data)
            if response.status_code == 201:
                return response.json()
            else:
                print(f"Error al crear el ítem de orden: {response.status_code}, {response.content}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Excepción al crear el ítem de orden: {str(e)}")
            return None
        
# Helpers for Location API
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