from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

#categorias para producto
class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=200)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)

    def __str__(self):
        return self.name

    def delete(self, *args, **kwargs):
        sin_categoria, _ = Category.objects.get_or_create(name='Sin categoría', defaults={'description': 'Categoría predeterminada para productos sin categoría'})
        products = self.product_set.all()
        for product in products:
            product.category = sin_categoria
            product.save()
        super().delete(*args, **kwargs)

#producto
class Product(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nombre")
    price = models.IntegerField(verbose_name="Precio")
    description = models.TextField(max_length=200, verbose_name="Descripción")
    is_new = models.BooleanField(default=True, verbose_name="¿Nuevo?")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Categoría"
    )
    stock = models.IntegerField(verbose_name="Unidades")
    is_featured = models.BooleanField(default=False, verbose_name="¿Destacado?")
    image = models.ImageField(
        upload_to='products/', blank=True, null=True, verbose_name="Imagen"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    is_rentable = models.BooleanField(default=False, verbose_name="¿Arrendable?")

    def __str__(self):
        return self.name

#tipo de consulta
class QueryType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=200)

    def __str__(self):
        return self.name

#consulta
class Contact(models.Model):
    STATUS_CHOICES = (
        ('Nuevo', 'Nuevo'),
        ('En progreso', 'En progreso'),
        ('Finalizado', 'Finalizado'),
    )

    name = models.CharField(max_length=50)
    email = models.EmailField()
    phone = models.CharField(max_length=9, blank=True)
    message = models.TextField(max_length=200)
    query_type = models.ForeignKey(QueryType, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Nuevo')

    def __str__(self):
        return self.name

class Usuarios(models.Model):
    usrN= models.CharField(max_length=100,verbose_name="Nombre de Usuario")
    pswrdN= models.CharField(max_length=15, verbose_name="Contraseña")
    pswrdN2=models.CharField(max_length=15, verbose_name="Contraseña2")
#fin modelos para usuarios

#se crea modelo de token
class Tokens(models.Model):
    token= models.CharField(max_length=256)
    user = models.CharField(max_length=256)    

# Región
class Region(models.Model):  
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Comuna
class Municipality(models.Model):  
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="municipalities")

    def __str__(self):
        return self.name

# Orden de compra
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    order_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(null=True, blank=True)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    municipality = models.ForeignKey(Municipality, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=9, null=True)
    accumulated = models.DecimalField(max_digits=10, decimal_places=2)
    pagado = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    def __str__(self):
        return f"Order {self.order_id} - User: {self.user.username if self.user else 'None'}"
    
# Items de orden de compra
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True, blank=True, verbose_name="Producto")
    amount = models.IntegerField()

    def __str__(self):
        return f"{self.product_name} - Amount: {self.amount}"

# Orden de renta    
class RentalOrder(models.Model):
    rut = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=9)
    deliver_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
# Items de orden de renta
class RentalOrderItem(models.Model):
    rental_order = models.ForeignKey(RentalOrder, on_delete=models.CASCADE, related_name='items')
    product_name = models.CharField(max_length=100)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.IntegerField()

    def __str__(self):
        return f"{self.product_name} - Amount: {self.amount}"
