from django.contrib import admin
from .models import Category, Product, QueryType, Contact,Order

# Register your models here.

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(QueryType)
admin.site.register(Contact)

admin.site.register(Order)
