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
                    # Actualizar solo el stock usando PATCH
                    response = ProductAPI.update_product_stock(product_id, {"stock": new_stock}, use_patch=True)

                    # Verificar si la actualización fue exitosa
                    if response is None:
                        messages.error(self.request, f"Error al actualizar el producto {product_data['name']}.")
                else:
                    messages.error(self.request, f"Error: Stock insuficiente para el producto {value['product_name']}.")
            else:
                messages.error(self.request, f"Error al obtener datos del producto {value['product_name']} de la API.")


    def get_product_quantity(self, product):
        product_id = str(product["id"])  # Acceso por clave JSON
        if product_id in self.cart_items:
            return self.cart_items[product_id]["amount"]
        return 0
    
    def increment_item(self, product, quantity=1):
        product_id = str(product["id"])
        
        if product_id not in self.cart_items:
            self.cart_items[product_id] = {
                "product_id": product["id"],
                "product_name": product["name"],
                "product_price": product["price"],
                "accumulated": product["price"] * quantity,
                "amount": quantity,
            }
        else:
            # Aumenta la cantidad del producto
            if self.cart_items[product_id]["amount"] + quantity <= product["stock"]:
                self.cart_items[product_id]["amount"] += quantity
                self.cart_items[product_id]["accumulated"] += product["price"] * quantity
            else:
                raise ValueError("Error: Maximum stock limit reached.")
        
        self.save_cart()

    def decrement_item(self, product, quantity=1):
        product_id = str(product["id"])
        
        if product_id in self.cart_items:
            current_quantity = self.cart_items[product_id]["amount"]
            if current_quantity > quantity:
                self.cart_items[product_id]["amount"] -= quantity
                self.cart_items[product_id]["accumulated"] -= product["price"] * quantity
            else:
                # Si la cantidad llega a 0, eliminar el producto del carrito
                del self.cart_items[product_id]
            self.save_cart()
        else:
            raise ValueError("Error: Product not in cart.")
