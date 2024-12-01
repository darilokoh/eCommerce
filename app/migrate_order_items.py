from app.models import OrderItem, Product

def migrate_order_items():
    for item in OrderItem.objects.all():
        product = Product.objects.filter(name=item.product_name).first()
        if product:
            item.product = product
            item.save()
            print(f"OrderItem {item.id} actualizado con Product {product.id}")
