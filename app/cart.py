from django.contrib import messages
from .api_helpers import ProductAPI

class Cart:
    def __init__(self, request):
        self.request = request
        self.session = request.session
        cart_items = self.session.get("cart")
        if not cart_items:
            self.session["cart"] = {}
            self.cart_items = self.session["cart"]
        else:
            self.cart_items = cart_items

    def add(self, product):
        product_id = str(product["id"])  # Acceso por clave JSON
        if product_id not in self.cart_items.keys():
            self.cart_items[product_id] = {
                "product_id": product["id"],
                "product_name": product["name"],
                "product_price": product["price"],
                "accumulated": product["price"],
                "amount": 1,
            }
        else:
            if self.cart_items[product_id]["amount"] < product["stock"]:
                self.cart_items[product_id]["amount"] += 1
                self.cart_items[product_id]["accumulated"] += product["price"]
            else:
                messages.error(self.request, "Error: Maximum stock limit reached.")
                return

        self.save_cart()

    def save_cart(self):
        self.session["cart"] = self.cart_items
        self.session.modified = True

    def delete(self, product):
        product_id = str(product["id"])  # Acceso por clave JSON
        if product_id in self.cart_items:
            del self.cart_items[product_id]
            self.save_cart()

    def subtract(self, product):
        product_id = str(product["id"])  # Acceso por clave JSON
        if product_id in self.cart_items.keys():
            self.cart_items[product_id]["amount"] -= 1
            self.cart_items[product_id]["accumulated"] -= product["price"]
            if self.cart_items[product_id]["amount"] <= 0:
                self.delete(product)
                messages.success(self.request, "Producto Eliminado.")
            self.save_cart()

    def clean(self):
        self.session["cart"] = {}
        self.session.modified = True

    def buy(self):
        # Simulando la actualización de stock a través de la API
        for key, value in self.cart_items.items():
            product_id = int(value["product_id"])

            # Obtener el producto desde la API
            product_data = ProductAPI.get_product(product_id)

            if product_data:
                current_stock = product_data.get("stock", 0)
                new_stock = current_stock - int(value["amount"])

                if new_stock >= 0:
                    # Actualizar el producto en la API con el nuevo stock
                    ProductAPI.update_product(product_id, {"stock": new_stock})
                else:
                    messages.error(self.request, f"Error: Stock insuficiente para el producto {value['product_name']}.")
            else:
                messages.error(self.request, f"Error al obtener datos del producto {value['product_name']} de la API.")

    def get_product_quantity(self, product):
        product_id = str(product["id"])  # Acceso por clave JSON
        if product_id in self.cart_items:
            return self.cart_items[product_id]["amount"]
        return 0
