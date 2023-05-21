from django.shortcuts import render, redirect, get_object_or_404
from .forms import ContactForm, ProductForm, CustomUserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate ,login 
from .models import Product, Category
from django.core.paginator import Paginator
from django.http import Http404
from rest_framework import viewsets
from .serializers import ProductSerializer, CategorySerializer
import requests
from django.contrib.auth.decorators import login_required, permission_required
from django.core.cache import cache
from app.cart import Cart

# Create your views here.
class CategoryViewset(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewset(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        products = Product.objects.all()

        name = self.request.GET.get('name')
        featured = self.request.GET.get('featured')
        category = self.request.GET.get('category')
        new = self.request.GET.get('new')

        if name:
            products = products.filter(name__contains=name)
        if featured:
            products = products.filter(featured=True)
        if category:
            products = products.filter(category=category)
        if new:
            products = products.filter(new=True)
        return products

def home(request):
    products = Product.objects.all()
    data = {
        'products': products
    }
    # response = requests.get('http://127.0.0.1:8000/api/product/?featured=True&new=True').json()
    # data = {
    #      'products': response
    #  }
    return render(request, 'app/home.html', data)

def catalogue(request):
    name_filter = request.GET.get('name', '')
    category_filter = request.GET.get('category', '')
    min_price_filter = request.GET.get('min_price', '')
    max_price_filter = request.GET.get('max_price', '')

    products = Product.objects.all()
    categories = Category.objects.all()  # Obtener todas las categorías

    if name_filter:
        products = products.filter(name__icontains=name_filter)

    if category_filter:
        products = products.filter(category_id=category_filter)

    if min_price_filter:
        products = products.filter(price__gte=min_price_filter)

    if max_price_filter:
        products = products.filter(price__lte=max_price_filter)

    if 'clear_filters' in request.GET:
        # Si se hizo clic en el botón de eliminar filtros, reiniciar los filtros
        products = Product.objects.all()

    data = {
        'products': products,
        'categories': categories,
    }

    return render(request, 'app/catalogue.html', data)

def services(request):
    return render(request, 'app/services.html')

def contact(request):
    data = {
        'form': ContactForm()
    }

    if request.method == 'POST':
        form = ContactForm(data=request.POST)
        if form.is_valid():
            form.save()
            data["message"] = "Enviado exitosamente"
        else:
            data["form"] = form
    return render(request, 'app/contact.html', data)

@permission_required('app.add_product')
def add_product(request):

    data = {
        'form': ProductForm()
    }

    if request.method == 'POST':
        form = ProductForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto Agregado")
            return redirect(to="list_product")
        else:
            data["form"] = form
    return render(request, 'app/product/add.html',data)

@permission_required('app.view_product')
def list_product(request):
    products = Product.objects.all()
    page = request.GET.get('page', 1)

    try:
        paginator = Paginator(products, 5)
        products = paginator.page(page)
    except:
        raise Http404


    data = {
        'entity': products,
        'paginator': paginator
    }
    return render(request, 'app/product/list.html', data)

@permission_required('app.change_product')
def update_product(request, id):

    product = get_object_or_404(Product, id=id)

    data = {
        'form':ProductForm(instance=product)
    }

    if request.method == 'POST':
        form = ProductForm(data=request.POST, instance=product, files=request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Modificado correctamente")
            return redirect(to="list_product")
        data["form"] = form


    return render(request, 'app/product/update.html',data)

@permission_required('app.delete_product')
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    messages.success(request, "Eliminado correctamente")
    return redirect(to="list_product")

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    data = {
        'product':product
    }

    return render(request, 'app/product/detail.html',data)

def register(request):
    data = {
        'form' : CustomUserCreationForm()
    }
    if request.method == 'POST':
        formulario = CustomUserCreationForm(data=request.POST)
        if formulario.is_valid():
            formulario.save()
            user = authenticate(username=formulario.cleaned_data["username"], password=formulario.cleaned_data["password1"])
            login(request, user)
            messages.success(request, "Te has registrado correctamente")
            #redirigir al home 
            return redirect(to="home") 
        data ["form"] = formulario    
    return render(request,'registration/register.html', data)

def add_prod_cart(request, product_id):
    cart = Cart(request)
    product = Product.objects.get(id=product_id)
    
    if product.stock <= 0:
        messages.error(request, "Error: Product is out of stock.")
    elif cart.get_product_quantity(product) >= product.stock:
        messages.error(request, "Error: Maximum stock limit reached.")
    else:
        cart.add(product)
        # messages.success(request, "Product added to cart successfully.")
    
    return redirect(to="Cart")

def del_prod_cart(request, product_id):
    cart = Cart(request)
    product = Product.objects.get(id=product_id)
    cart.delete(product)
    return redirect(to="Cart")

def subtract_product_cart(request, product_id):
    cart = Cart(request)
    product = Product.objects.get(id=product_id)
    cart.subtract(product)
    return redirect("Cart")

def clean_cart(request):
    cart = Cart(request)
    cart.clean()
    return redirect("Cart")

def cart_page(request):
    products = Product.objects.all()
    data = {
        'products': products
    }
    
    return render(request, 'app/cart_page.html', data)

# def checkout(request):

#     return render(request,'core/checkout.html')

def buy_confirm(request):
    cart = Cart(request)
    cart.buy()
    cart.clean()
    return redirect('cart')

# def pago_exitoso(request):

#     return render(request,'core/pago_exitoso.html')