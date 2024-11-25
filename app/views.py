from django.shortcuts import render, redirect
from .forms import CambiarPasswordForm, ContactForm, ProductForm, CategoryForm, QueryTypeForm, RentalOrderForm, RecuperarForm, OrderForm
from django.contrib import messages
from datetime import timedelta
from django.contrib.auth import authenticate, login
from .models import Product, Category, Contact, QueryType, RentalOrder, RentalOrderItem, Order, OrderItem, Tokens, Region, Municipality
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponse, JsonResponse, HttpRequest
from rest_framework import viewsets, serializers
from .serializers import ProductSerializer, CategorySerializer, ContactSerializer, QueryTypeSerializer, RentalOrderSerializer,\
      RentalOrderItemSerializer, LoginSerializer, RegionSerializer, MunicipalitySerializer, OrderSerializer, OrderItemSerializer
import requests
from django.contrib.auth.decorators import login_required, permission_required, user_passes_test
from app.cart import Cart
from rest_framework.response import Response
from django.conf import settings
from django.db.models import Sum, Q
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, action
from django.middleware.csrf import get_token
from django.views.decorators.http import require_http_methods
from .serializers import TokenSerializer
from .forms import UsuariosForm, LoginForm
from django.contrib.auth.models import User
import requests
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.utils import timezone
from dateutil.parser import parse
from collections import Counter
from django.contrib.auth.hashers import make_password

# IMPORTS API TRANSBANK
from transbank.webpay.webpay_plus.transaction import Transaction, WebpayOptions
from transbank.common.integration_type import IntegrationType

# API HELPERS
from .api_helpers import LocationAPI, CategoryAPI, ProductAPI, RentalOrderAPI, RentalOrderItemAPI, ContactAPI, QueryTypeAPI, OrderAPI, OrderItemAPI

from django.utils.crypto import get_random_string
from django.contrib.auth import update_session_auth_hash
tok = None


def is_staff(user):
    return (user.is_authenticated and user.is_superuser)

def is_admin(user):
    return user.groups.filter(name='admin').exists()

# VIEWSETS PARA APIS
class CategoryViewset(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewset(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        products = Product.objects.all()

        name = self.request.GET.get('name')
        is_featured = self.request.GET.get('is_featured')
        category = self.request.GET.get('category')
        is_new = self.request.GET.get('is_new')
        min_price = self.request.GET.get('min_price_filter')
        max_price = self.request.GET.get('max_price_filter')
        is_rentable = self.request.GET.get('is_rentable')

        if name:
            products = products.filter(name__icontains=name)
        if category:
            products = products.filter(category=category)
        if min_price and max_price:
            products = products.filter(price__range=(min_price, max_price))
        elif min_price:
            products = products.filter(price__gte=min_price)
        elif max_price:
            products = products.filter(price__lte=max_price)

        # Aplicar los filtros de featured y new
        if is_featured:
            products = products.filter(is_featured=True)
        if is_new:
            products = products.filter(is_new=True)
        # Filtro para rentable
        if is_rentable is not None:
            if is_rentable.lower() == 'true':
                products = products.filter(is_rentable=True)
            elif is_rentable.lower() == 'false':
                products = products.filter(is_rentable=False)

        return products

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def perform_create(self, serializer):
        serializer.save()

@require_http_methods(["GET", "POST"])
@login_required
def CambiarPassword(request):
    if request.method == 'POST':
        form = CambiarPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()

            messages.success(
                request, 'Tu contraseña ha sido actualizada exitosamente.')
            # Redirige a la página de inicio o donde prefieras
            return redirect('home')
        else:
            messages.error(
                request, 'Por favor corrige los errores a continuación.')
    else:
        form = CambiarPasswordForm(user=request.user)

    return render(request, 'registration/CambiarPassword.html', {'form': form})

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer

    def get_queryset(self):
        queryset = Contact.objects.all()

        # Obtener el parámetro de consulta 'status' de la URL
        status = self.request.query_params.get('status', None)
        if status is not None and status != '':
            # Filtrar los contactos por estado
            queryset = queryset.filter(status=status)

        # Obtener el parámetro de consulta 'query_type_id' de la URL
        query_type_id = self.request.query_params.get('query_type_id', None)
        if query_type_id is not None and query_type_id != '':
            # Filtrar los contactos por ID del tipo de consulta
            queryset = queryset.filter(query_type_id=query_type_id)

        # Filtro por nombre del tipo de consulta (query_type_name)
        query_type_name = self.request.query_params.get('query_type_name', None)
        if query_type_name:
            queryset = queryset.filter(query_type__name__iexact=query_type_name)

        return queryset

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        status = request.data.get('status')
        instance.status = status
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class QueryTypeViewset(viewsets.ModelViewSet):
    queryset = QueryType.objects.all()
    serializer_class = QueryTypeSerializer

class RentalOrderViewSet(viewsets.ModelViewSet):
    # def list(self, request):
    #     rental_orders = RentalOrder.objects.all()
    #     serializer = RentalOrderSerializer(rental_orders, many=True)
    #     return Response(serializer.data)
    queryset = RentalOrder.objects.all()
    serializer_class = RentalOrderSerializer

class RentalOrderItemViewSet(viewsets.ModelViewSet):
    queryset = RentalOrderItem.objects.all()
    serializer_class = RentalOrderItemSerializer

class RegionViewSet(viewsets.ReadOnlyModelViewSet):  # Solo lectura
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

class MunicipalityViewSet(viewsets.ReadOnlyModelViewSet):  # Solo lectura
    serializer_class = MunicipalitySerializer

    def get_queryset(self):
        region_id = self.request.query_params.get('region_id')
        if region_id:
            return Municipality.objects.filter(region_id=region_id)
        return Municipality.objects.all()

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items').all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtro por rango de fechas
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])

        # Filtro por nombre de OrderItem
        order_item_name = self.request.query_params.get('order_item_name')
        if order_item_name:
            queryset = queryset.filter(items__product__name__icontains=order_item_name)

        return queryset

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        queryset = self.get_queryset()

        # Total acumulado
        total_accumulated = queryset.aggregate(total_accumulated=Sum('accumulated'))['total_accumulated']

        # Total de productos vendidos
        total_products_sold = OrderItem.objects.filter(order__in=queryset).aggregate(total_sold=Sum('amount'))['total_sold']

        # Productos más vendidos
        top_products = (
            OrderItem.objects.filter(order__in=queryset)
            .values('product__name')
            .annotate(total_amount=Sum('amount'))
            .order_by('-total_amount')[:4]
        )

        return Response({
            'total_accumulated': total_accumulated,
            'total_products_sold': total_products_sold,
            'top_products': top_products,
        })

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

# VISTAS INICIALES
@require_http_methods(["GET"])
def home(request):
    # Parámetros para filtrar productos
    params = {
        'is_new__in': 'true,false',
        'is_featured__in': 'true,false',
        'is_rentable': 'false',  # Filtrar solo productos no arrendables
    }

    # Obtener los productos desde el helper
    product_response = ProductAPI.list_products(params)

    # Obtener categorías desde el helper
    categories_response = CategoryAPI.get_categories()

    # Preparar datos para la plantilla
    data = {
        'products': product_response,
        'categories': categories_response
    }

    return render(request, 'app/home.html', data)

@require_http_methods(["GET", "POST"])
@api_view(['GET', 'POST'])
def catalogue(request):
    # Obtenemos los filtros desde el request
    name_filter = request.GET.get('name', '')
    category_filter = request.GET.get('category', '')
    min_price_filter = request.GET.get('min_price_filter', '')
    max_price_filter = request.GET.get('max_price_filter', '')

    # Definimos los parámetros para filtrar productos
    params = {
        'name': name_filter,
        'category': category_filter,
        'min_price_filter': min_price_filter,
        'max_price_filter': max_price_filter,
        'is_rentable': 'false',  # Siempre excluir productos arrendables
    }

    # Verificar si se solicita limpiar filtros
    if 'clear_filters' in request.GET:
        params = {'is_rentable': 'false'}  # Solo aplica el filtro de no arrendables

    # Obtenemos los productos desde el helper
    products = ProductAPI.list_products(params=params)

    # Excluir categorías con id = 3 y 5 al obtenerlas desde el helper
    categories = CategoryAPI.get_categories(exclude_ids=[3, 5])

    # Preparar datos para la plantilla
    data = {
        'products': products,
        'categories': categories,
    }

    return render(request, 'app/catalogue.html', data)

@api_view(['GET', 'POST'])
def rental_service(request):
    if request.method == 'POST':
        form = RentalOrderForm(request.POST)
        if form.is_valid():
            deliver_date = form.cleaned_data['deliver_date']
            deliver_date_iso = deliver_date.strftime('%Y-%m-%dT%H:%M')

            rental_order_data = {
                'rut': form.cleaned_data['rut'],
                'name': form.cleaned_data['name'],
                'address': form.cleaned_data['address'],
                'email': form.cleaned_data['email'],
                'phone': form.cleaned_data['phone'],
                'deliver_date': deliver_date_iso,
            }

            # Validar duplicados a través del helper
            is_duplicate = RentalOrderAPI.check_duplicate_order(rental_order_data['rut'])
            if is_duplicate:
                return JsonResponse({'error': 'Ya existe una orden de renta con los mismos datos'})

            # Crear la orden de renta usando la API
            rental_order = RentalOrderAPI.create_rental_order(rental_order_data)
            if rental_order:
                rental_order_id = rental_order['id']

                # Obtener productos seleccionados y cantidades
                products_selected = request.POST.getlist('products')
                quantities = [
                    int(request.POST.get(f'quantity_{product_id}', 1)) for product_id in products_selected
                ]

                # Obtener los detalles de los productos desde la API
                products = ProductAPI.get_products_by_ids(products_selected)

                # Crear los RentalOrderItems en la API
                items_created = RentalOrderItemAPI.bulk_create_rental_order_items(
                    rental_order_id, products_selected, quantities
                )
                if items_created:
                    # Procesar información para el correo
                    product_names = [product['name'] for product in products]
                    total_price = sum(
                        product['price'] * quantity for product, quantity in zip(products, quantities)
                    )

                    email_subject = 'Confirmación de orden de renta'
                    email_body = f'Se ha creado una nueva orden de renta con los siguientes detalles:\n\n' \
                                 f'RUT: {rental_order_data["rut"]}\n' \
                                 f'Nombre: {rental_order_data["name"]}\n' \
                                 f'Dirección: {rental_order_data["address"]}\n' \
                                 f'Correo electrónico: {rental_order_data["email"]}\n' \
                                 f'Teléfono: {rental_order_data["phone"]}\n' \
                                 f'Fecha de entrega: {rental_order_data["deliver_date"]}\n\n' \
                                 f'Productos:\n'
                    for name, quantity, product in zip(product_names, quantities, products):
                        email_body += f'- {name}: {quantity}\nPrecio: {product["price"]}\n'
                    email_body += f'Total de la orden: {total_price}\n\n' \
                                  f'Gracias por su solicitud.'

                    send_mail(email_subject, email_body, settings.EMAIL_HOST_USER, [rental_order_data['email']])

                    return JsonResponse({'message': 'La solicitud de arriendo ha sido enviada correctamente, recibirás un correo con la información'})
                else:
                    return JsonResponse({'error': 'Error al crear los items de la orden de renta'})

        return JsonResponse({'error': 'Error en los datos del formulario'})

    # Método GET
    form = RentalOrderForm()
    params = {'is_rentable': 'true'}
    product_response = ProductAPI.list_products(params=params)

    data = {
        'form': form,
        'products': product_response,
        'csrf_token': get_token(request)
    }
    return render(request, 'app/rental_service.html', data)

# CONTACTO
@api_view(['GET','POST'])
def contact(request):
    data = {
        'form': ContactForm()
    }

    return render(request, 'app/contact/contact.html', data)

@require_http_methods(["POST"])
def update_contact_status(request, contact_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        if not status:
            return JsonResponse({'error': 'El estado es requerido'}, status=400)

        # Llamar al helper para actualizar el estado
        updated_contact = ContactAPI.update_contact_status(contact_id, status)
        if not updated_contact:
            return JsonResponse({'error': 'Error al actualizar el contacto'}, status=500)

    return redirect('list_contact')

@user_passes_test(is_admin)
@require_http_methods(["GET"])
def list_contact(request):
    status = request.GET.get('status', '')
    query_type = request.GET.get('query_type', '')

    # Obtener los tipos de consulta desde QueryTypeAPI
    query_types = QueryTypeAPI.list_query_types()

    # Definir filtros para los contactos
    filters = {}
    if status and status != 'Todos':
        filters['status'] = status
    if query_type and query_type != 'Todos':
        filters['query_type_name'] = query_type  # Cambiar a query_type_name para filtrar por API

    # Obtener los contactos desde ContactAPI
    contacts = ContactAPI.list_contacts(filters=filters)

    # Paginación
    paginator = Paginator(contacts, 5)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        contacts = paginator.page(1)
    except EmptyPage:
        contacts = paginator.page(paginator.num_pages)

    data = {
        'entity': contacts,
        'paginator': paginator,
        'query_types': query_types,
        'selected_status': status,
        'selected_query_type': query_type,
    }

    return render(request, 'app/contact/list.html', data)

# VISTAS DE QUERYTYPE
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def add_query_type(request):
    if request.method == 'POST':
        form = QueryTypeForm(request.POST, request.FILES)
        if form.is_valid():
            error_message = None  # Inicializamos la variable error_message
            try:
                # Usar el helper para crear el QueryType
                data = form.cleaned_data
                QueryTypeAPI.create_query_type(data)
                
                # Si se crea exitosamente, redirigir
                messages.success(
                    request, 'Tipo de consulta agregado exitosamente.')
                return redirect('list_query_type')
            except serializers.ValidationError as e:
                # Manejar errores del helper
                form.add_error('name', e.detail.get('name', ['Error desconocido'])[0])
        else:
            error_message = "Error en los datos del formulario"
        data = {
            'form': form,
            'error_message': error_message
        }
    else:
        data = {
            'form': QueryTypeForm()
        }

    return render(request, 'app/querytype/add.html', data)

@user_passes_test(is_admin)
@require_http_methods(["GET"])
def list_query_type(request):
    # Obtener los tipos de consulta desde el helper
    query_types = QueryTypeAPI.list_query_types()
    
    if not query_types:  # Manejar el caso de error al obtener los datos
        messages.error(request, "Error al cargar los tipos de consulta.")
        query_types = []

    # Manejo de paginación
    page = request.GET.get('page', 1)
    try:
        paginator = Paginator(query_types, 5)
        query_types = paginator.page(page)
    except:
        raise Http404

    # Preparar datos para la plantilla
    data = {
        'entity': query_types,
        'paginator': paginator
    }
    return render(request, 'app/querytype/list.html', data)

@require_http_methods(["GET", "POST"])
def update_query_type(request, id):
    querytype_data = QueryTypeAPI.get_object_query_type(id)

    if querytype_data:
        error_message = ""

        if request.method == 'POST':
            form = QueryTypeForm(request.POST)

            if form.is_valid():
                name = form.cleaned_data['name']
                description = form.cleaned_data['description']

                # Verificar duplicados a través del helper
                if QueryTypeAPI.check_duplicate_query_type(name, exclude_id=int(id)):
                    form.add_error('name', 'Este tipo de consulta ya existe')
                    error_message = "Este tipo de consulta ya existe"
                else:
                    # Actualizar el tipo de consulta
                    updated_data = {'name': name, 'description': description}
                    if QueryTypeAPI.update_query_type(id, updated_data):
                        messages.success(request, "Modificado correctamente")
                        return redirect(to="list_query_type")
                    else:
                        error_message = "Error al actualizar el tipo de consulta a través de la API"
            else:
                error_message = "Error en los datos del formulario"
        else:
            form = QueryTypeForm(initial=querytype_data)
            error_message = ""

        data = {
            'form': form,
            'error_message': error_message
        }
        return render(request, 'app/querytype/update.html', data)

    else:
        # Manejar el caso si no se puede obtener el tipo de consulta de la API
        messages.error(request, "Error al obtener el tipo de consulta de la API")
        return redirect(to="list_query_type")

@require_http_methods(["GET", "POST"])
def delete_query_type(request, id):
    # Obtener datos del tipo de consulta
    querytype_data = QueryTypeAPI.get_object_query_type(id)

    if querytype_data:
        # Intentar eliminar el tipo de consulta utilizando el helper
        if QueryTypeAPI.delete_query_type(id):
            messages.success(request, "Eliminado correctamente")
            return redirect(to="list_query_type")
        else:
            # Manejar el caso de error al eliminar
            error_message = "Error al eliminar el tipo de consulta a través de la API"
    else:
        # Manejar el caso si no se puede obtener el tipo de consulta
        error_message = "Error al obtener el tipo de consulta a través de la API"

    # Renderizar la página de error
    messages.error(request, error_message)
    return redirect(to="list_query_type")

# VISTAS DE PRODUCT
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']

            # Verificar duplicados a través del helper
            if ProductAPI.check_duplicate_product(name):
                form.add_error('name', 'Este producto ya existe')
                error_message = "Este producto ya existe"
            else:
                # Preparar datos del producto
                product_data = {
                    'name': name,
                    'price': form.cleaned_data['price'],
                    'description': form.cleaned_data['description'],
                    'is_new': form.cleaned_data['is_new'],
                    'category': form.cleaned_data['category'].id if form.cleaned_data['category'] else None,
                    'stock': form.cleaned_data['stock'],
                    'is_featured': form.cleaned_data['is_featured'],
                    'is_rentable': form.cleaned_data['is_rentable'],
                }

                # Crear el producto a través del helper
                created_product = ProductAPI.create_product(data=product_data, files={'image': form.cleaned_data['image']})
                if created_product:
                    messages.success(request, 'Producto agregado exitosamente.')
                    return redirect('list_product')
                else:
                    error_message = "Error al crear el producto a través de la API"
        else:
            error_message = "Error en los datos del formulario"

        data = {'form': form, 'error_message': error_message}
    else:
        data = {'form': ProductForm()}

    return render(request, 'app/product/add.html', data)

@user_passes_test(is_admin)
@require_http_methods(["GET"])
def list_product(request):
    name_filter = request.GET.get('name', '')
    category_filter = request.GET.get('category', '')

    # Filtros para productos
    params = {}
    if name_filter:
        params['name'] = name_filter
    if category_filter:
        params['category'] = category_filter

    # Obtener productos y todas las categorías
    products = ProductAPI.list_products(params=params)
    categories = CategoryAPI.get_categories()

    # Paginación
    paginator = Paginator(products, 5)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    data = {
        'entity': products,
        'paginator': paginator,
        'name_filter': name_filter,
        'category_filter': category_filter,
        'categories': categories,
    }
    return render(request, 'app/product/list.html', data)

@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def update_product(request, id):
    product_data = ProductAPI.get_product(id)

    if product_data:
        error_message = ""

        if request.method == 'POST':
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                name = form.cleaned_data['name']
                # Verificar duplicados excluyendo el producto actual
                if ProductAPI.check_duplicate_product(name, exclude_id=int(id)):
                    form.add_error('name', 'Este producto ya existe')
                    error_message = "Este producto ya existe"
                else:
                    updated_data = {
                        'name': name,
                        'description': form.cleaned_data['description'],
                        'price': form.cleaned_data['price'],
                        'is_new': form.cleaned_data['is_new'],
                        'category': form.cleaned_data['category'].id if form.cleaned_data['category'] else None,
                        'stock': form.cleaned_data['stock'],
                        'is_featured': form.cleaned_data['is_featured'],
                        'is_rentable': form.cleaned_data['is_rentable']
                    }

                    files = {'image': form.cleaned_data['image']} if form.cleaned_data['image'] else None
                    updated_product = ProductAPI.update_product(id, updated_data, files)

                    if updated_product:
                        messages.success(request, "Modificado correctamente")
                        return redirect(to="list_product")
                    else:
                        error_message = "Error al actualizar el producto a través de la API"
            else:
                error_message = "Error en los datos del formulario"
        else:
            form = ProductForm(initial=product_data, product_image_url=product_data.get('image'))
            error_message = ""

        data = {
            'form': form,
            'error_message': error_message
        }

        return render(request, 'app/product/update.html', data)
    else:
        messages.error(request, "Error al obtener el producto de la API")
        return redirect(to="list_product")

@user_passes_test(is_admin)
@require_http_methods(["GET"])
def delete_product(request, id):
    # Obtener los datos del producto
    product_data = ProductAPI.get_product(id)

    if product_data:
        # Intentar eliminar el producto a través del helper
        if ProductAPI.delete_product(id):
            messages.success(request, "Eliminado correctamente")
        else:
            # Manejar el caso de error en la solicitud DELETE
            error_message = "Error al eliminar el producto a través de la API"
            messages.error(request, error_message)
    else:
        # Manejar el caso de error al obtener el producto
        error_message = "Error al obtener el producto a través de la API"
        messages.error(request, error_message)

    # Redireccionar a la página de listado
    return redirect(to="list_product")

@require_http_methods(["GET"])
def product_detail(request, id):
    # Obtener los detalles del producto
    product_data = ProductAPI.get_product(id)

    if product_data:
        # Obtener la categoría del producto
        category_id = product_data.get('category')
        category_data = CategoryAPI.get_category_by_id(category_id)

        if category_data:
            # Crear instancia de categoría
            category = Category(**category_data)

            # Actualizar el producto con la instancia de categoría
            product_data['category'] = category
            product_data.pop('category_name', None)

            # Crear la instancia del producto
            product = Product(**product_data)

            return render(request, 'app/product/detail.html', {'product': product})
        else:
            # Manejar error al obtener categoría
            messages.error(request, "Error al obtener la categoría de la API.")
            return render(request, 'app/product/detail.html', {'error_message': "Error al obtener la categoría."})
    else:
        # Manejar error al obtener producto
        messages.error(request, "Error al obtener el producto de la API.")
        return render(request, 'app/product/detail.html', {'error_message': "Error al obtener el producto."})

# METODOS DEL CARRITO
@require_http_methods(["GET"])
def add_prod_cart(request, product_id):
    cart = Cart(request)

    # Obtener los detalles del producto desde el helper
    product_data = ProductAPI.get_product(product_id)

    if product_data:
        if product_data['stock'] <= 0:
            messages.error(request, "Error: Product is out of stock.")
        elif cart.get_product_quantity(product_data) >= product_data['stock']:
            messages.error(request, "Error: Maximum stock limit reached.")
        else:
            # Agregar el producto al carrito
            cart.add(product_data)
            #messages.success(request, "Product added to cart successfully.")
    else:
        messages.error(request, "Error: Could not retrieve product details.")

    return redirect(to="Cart")

@require_http_methods(["GET"])
def del_prod_cart(request, product_id):
    cart = Cart(request)
    product = ProductAPI.get_product(product_id)  # Obtener el producto desde la API
    if product:  # Verificar que el producto exista en la API
        cart.delete(product)
    else:
        messages.error(request, "Error: Producto no encontrado en el sistema.")
    return redirect(to="Cart")

@require_http_methods(["GET"])
def subtract_product_cart(request, product_id):
    cart = Cart(request)
    product = ProductAPI.get_product(product_id)  # Obtener el producto desde la API
    if product:  # Verificar que el producto exista en la API
        cart.subtract(product)
    else:
        messages.error(request, "Error: Producto no encontrado en el sistema.")
    return redirect("Cart")

@require_http_methods(["GET"])
def clean_cart(request):
    cart = Cart(request)
    cart.clean()
    return redirect("Cart")

@require_http_methods(["GET"])
def cart_page(request):
    # Obtener todos los productos desde la API
    products = ProductAPI.list_products()

    # Preparar los datos para la plantilla
    data = {
        'products': products
    }

    return render(request, 'app/cart_page.html', data)

@require_http_methods(["GET", "POST"])
def buy_confirm(request):
    cart = Cart(request)
    cart.buy()
    cart.clean()
    messages.success(request, "Compra de prueba Completada")
    return redirect('home')

# VISTAS CATEGORY
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']

            # Verificar duplicados a través del helper
            if CategoryAPI.check_duplicate_category(name):
                form.add_error('name', 'Esta categoría ya existe')
                error_message = "Esta categoría ya existe"
            else:
                # Preparar datos de la categoría
                category_data = {
                    'name': name,
                    'description': form.cleaned_data['description'],
                }
                category_image = form.cleaned_data['image']

                # Crear categoría a través del helper
                created_category = CategoryAPI.create_category(
                    data=category_data,
                    files={'image': category_image} if category_image else None
                )

                if created_category:
                    messages.success(request, 'Categoría agregada exitosamente.')
                    return redirect('list_category')
                else:
                    error_message = "Error al crear la categoría a través de la API"
        else:
            error_message = "Error en los datos del formulario"

        data = {
            'form': form,
            'error_message': error_message
        }
    else:
        data = {
            'form': CategoryForm()
        }

    return render(request, 'app/category/add.html', data)

@user_passes_test(is_admin)
@require_http_methods(["GET"])
def list_category(request):
    # Obtener las categorías desde el helper
    categories = CategoryAPI.get_categories()

    # Manejo de paginación
    page = request.GET.get('page', 1)
    try:
        paginator = Paginator(categories, 5)
        categories = paginator.page(page)
    except PageNotAnInteger:
        categories = paginator.page(1)
    except EmptyPage:
        categories = paginator.page(paginator.num_pages)

    # Preparar datos para la plantilla
    data = {
        'entity': categories,
        'paginator': paginator
    }
    return render(request, 'app/category/list.html', data)

@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def update_category(request, id):
    # Obtener los datos de la categoría desde el helper
    category_data = CategoryAPI.get_category_by_id(id)

    if category_data:
        error_message = ""

        if request.method == 'POST':
            form = CategoryForm(request.POST, request.FILES)

            if form.is_valid():
                name = form.cleaned_data['name']

                # Verificar duplicados excluyendo el ID actual
                if CategoryAPI.check_duplicate_category(name, exclude_id=int(id)):
                    form.add_error('name', 'Esta categoría ya existe')
                    error_message = "Esta categoría ya existe"
                else:
                    description = form.cleaned_data['description']
                    image = form.cleaned_data.get('image')

                    # Crear un diccionario con los datos actualizados
                    updated_data = {
                        'name': name,
                        'description': description
                    }

                    # Actualizar la categoría a través del helper
                    files = {'image': image} if image else None
                    updated_category = CategoryAPI.update_category(id, updated_data, files)

                    if updated_category:
                        messages.success(request, "Categoría modificada correctamente.")
                        return redirect(to="list_category")
                    else:
                        error_message = "Error al actualizar la categoría a través de la API."
            else:
                error_message = "Error en los datos del formulario."
        else:
            form = CategoryForm(initial=category_data)
            error_message = ""

        data = {
            'form': form,
            'error_message': error_message
        }
        return render(request, 'app/category/update.html', data)
    else:
        # Manejar el caso de error al obtener la categoría
        messages.error(request, "Error al obtener la categoría de la API.")
        return redirect(to="list_category")

@user_passes_test(is_admin)
@require_http_methods(["GET"])
def delete_category(request, id):
    # Obtener los datos de la categoría desde el helper
    category_data = CategoryAPI.get_category_by_id(id)

    if category_data:
        # Intentar eliminar la categoría a través del helper
        if CategoryAPI.delete_category(id):
            messages.success(request, "Eliminado correctamente")
            return redirect(to="list_category")
        else:
            # Manejar error al eliminar la categoría a través de la API
            error_message = "Error al eliminar la categoría a través de la API"
            messages.error(request, error_message)
    else:
        # Manejar error al obtener la categoría
        error_message = "Error al obtener la categoría a través de la API"
        messages.error(request, error_message)

    return redirect(to="list_category")

# PANEL DE ADMIN
@user_passes_test(is_admin)
@require_http_methods(["GET", "POST"])
def admin_panel(request):

    return render(request, 'app/admin_panel.html')

@require_http_methods(["GET", "POST"])
def checkout_view(request):
    # Obtén las regiones y comunas desde la API
    regiones = LocationAPI.get_regions()
    comunas = LocationAPI.get_municipalities()
    
    # Calcula el cart_total sumando los precios y cantidades de los productos en el carrito
    cart_items = request.session.get('cart', {}).items()
    cart_total = sum(value.get('product_price', 0) * value.get('amount', 1) for key, value in cart_items)

    # Prepara las opciones de región para pasarlas al formulario
    region_choices = [('', 'Seleccione una región')] + [(region['id'], region['name']) for region in regiones]
    municipality_choices = [('', 'Seleccione una comuna')] + [(comuna['id'], comuna['name']) for comuna in comunas]

    # Inicializa el formulario con datos iniciales y opciones dinámicas
    initial_data = {
        "user": request.user.id if request.user.is_authenticated else None,
        "accumulated": cart_total,
    }
    form = OrderForm(initial=initial_data, region_choices=region_choices, municipality_choices=municipality_choices)

    context = {
        "form": form,
        "regiones": regiones,
        "comunas": comunas,
        "cart_total": cart_total,
    }
    return render(request, "app/checkout.html", context)

# pendiente a revisar comportamiento de api
@require_http_methods(["GET", "POST"])
def user_login(request):
    global tok
    datos = {
        'form': LoginForm()
    }
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            usernameU = request.POST['usrN']
            passwordU = request.POST['pswrdN']
            user = authenticate(username=usernameU, password=passwordU)
            if user is not None:
                login(request, user)
                refresh = RefreshToken.for_user(user)
                token = str(refresh.access_token)

                # Guardar el token en el modelo Tokens
                token_data = {
                    'token': token,
                    'user': usernameU
                }
                token_serializer = TokenSerializer(data=token_data)
                if token_serializer.is_valid():
                    token_serializer.save()

                tok = token
                messages.success(request, "has iniciado sesión")
                return redirect(to="home")
    return render(request, "registration/login.html", datos)

@require_http_methods(["GET", "POST"])
def Recuperar(request):
    form = RecuperarForm(request.POST or None)
    if form.is_valid():
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None
        if user:
            # Generar una nueva contraseña temporal
            new_password = get_random_string(length=12)

            # Actualizar la contraseña del usuario
            user.set_password(new_password)
            user.save()

            # Enviar la nueva contraseña por correo
            subject = 'Recuperación de contraseña'
            message = f'Tu nueva contraseña temporal es: {new_password}. Por favor, cámbiala inmediatamente después de iniciar sesión.'
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]
            send_mail(subject, message, from_email,
                      recipient_list, fail_silently=False)

            # Mostrar mensaje de éxito
            messages.success(
                request, "Se ha enviado una nueva contraseña temporal a tu correo.")
            # Redirige al formulario de login después de enviar el correo
            return redirect('login')

        else:
            messages.error(
                request, 'No se encontró una cuenta con ese correo electrónico.')

    return render(request, 'registration/Recuperar.html', {'form': form})

# se crea usuario nuevo y token
class LoginView(APIView):
    def post(self, request, format=None):
        django_request = HttpRequest()
        django_request.method = request.method
        django_request.POST = request.data
        django_request._request = request._request

        serializer = LoginSerializer(data=django_request.POST)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})

@require_http_methods(["GET", "POST"])
def Registrar(request):
    datos = {
        'form': UsuariosForm()
    }
    if request.method == 'POST':
        form = UsuariosForm(request.POST)
        if form.is_valid():
            # Obtiene los datos del usuario desde el formulario
            usernameN = form.cleaned_data.get('usrN')
            passwordN = form.cleaned_data.get('pswrdN')
            passwordN2 = form.cleaned_data.get('pswrdN2')
            try:
                # Verifica la existencia del usuario
                user = User.objects.get(username=usernameN)
            except User.DoesNotExist:
                # Si no existe, se genera un nuevo usuario validando si las contraseñas son idénticas
                if passwordN == passwordN2:
                    user = User.objects.create_user(
                        username=usernameN, email=usernameN, password=passwordN)
                    # Autentifica las credenciales del usuario
                    user = authenticate(username=usernameN, password=passwordN)
                    if user is not None:
                        login(request, user)
                        refresh = RefreshToken.for_user(user)
                        token = str(refresh.access_token)

                        # Guardar el token en el modelo Tokens
                        token_data = {
                            'token': token,
                            'user': usernameN
                        }
                        token_instance = Tokens.objects.create(**token_data)

                        messages.success(
                            request, "Te has registrado correctamente")
                        return redirect('home')

    return render(request, "registration/Registrar.html", datos)

@require_http_methods(["GET", "POST"])
def update_last_order_paid_status(user):
    try:
        # Obtener la última orden del usuario
        last_order = OrderAPI.get_last_order_by_user(user.id)
        if last_order:
            # Actualizar el estado de pago de la última orden
            updated_order = OrderAPI.update_order(last_order["order_id"], {"pagado": True})
            if updated_order:
                print("Orden actualizada exitosamente.")
            else:
                print("Error al actualizar la orden.")
        else:
            print("No se encontró ninguna orden para el usuario.")
    except Exception as e:
        print(f"Excepción al actualizar el estado de la última orden: {str(e)}")

@require_http_methods(["GET", "POST"])
def payment_success(request):
    if request.method == 'POST':
        user = request.user if request.user.is_authenticated else None
        name = request.POST.get('name')
        email = request.POST.get('email')
        region_id = request.POST.get('region')
        municipality_id = request.POST.get('municipality')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        accumulated = request.POST.get('accumulated')

        region = Region.objects.filter(id=region_id).first()
        municipality = Municipality.objects.filter(id=municipality_id).first()

        # Crear la orden a través del helper
        order_data = {
            'user': user.id if user else None,
            'name': name,
            'email': email,
            'region': region.id if region else None,
            'municipality': municipality.id if municipality else None,
            'address': address,
            'phone': phone,
            'accumulated': accumulated,
        }
        order_response = OrderAPI.create_order(order_data)

        if order_response:
            order_id = order_response['order_id']
            cart = Cart(request)

            for key, value in cart.cart_items.items():
                product_id = value.get("product_id")
                amount = value.get("amount")
                order_item_data = {
                    'order': order_id,
                    'product': product_id,
                    'amount': amount,
                }
                OrderItemAPI.create_order_item(order_item_data)

            # Vaciar el carrito después de que se procesen la orden y los ítems
            cart.clean()

            # Renderizar la página de éxito
            return render(request, 'app/payment_success.html', {'order': order_response})

        # Si algo falla en el proceso, mostrar un mensaje de error
        messages.error(request, "Error al procesar la orden. Intente nuevamente.")
        return redirect('checkout_view')

    return render(request, 'app/checkout.html')

# Como mejora se puede hacer que la cantidad de productos vendidos se actualize segun el paginador
@require_http_methods(["GET", "POST"])
def order_list(request):
    # Parámetros de filtro
    params = {
        'start_date': request.GET.get('start_date'),
        'end_date': request.GET.get('end_date'),
        'order_item_name': request.GET.get('order_item_name'),
    }

    # Obtener órdenes desde el helper
    orders_response = OrderAPI.list_orders(params)
    orders = orders_response.get('results', [])  # Lista de órdenes

    # Crear una instancia de Paginator local para manejar la paginación
    paginator = Paginator(orders, 5)  # Paginación con 5 elementos por página
    page_number = int(request.GET.get('page', 1))  # Convertir a entero
    try:
        orders = paginator.page(page_number)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)

    # Obtener estadísticas desde el helper
    statistics = OrderAPI.get_statistics(params)

    data = {
        'entity': orders,
        'paginator': paginator,  # Información de paginación
        'total_accumulated': statistics.get('total_accumulated', 0),
        'total_products_sold': statistics.get('total_products_sold', 0),
        'top_products': statistics.get('top_products', []),
    }
    return render(request, 'app/order_list.html', data)

@api_view(['POST'])
def obtain_token(request):
    username = request.data.get('username')
    password = request.data.get('password')

    if username and password:
        user = authenticate(username=username, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
            })
    return Response({'error': 'Credenciales inválidas.'}, status=400)

# (aca vamos con el update de api_helpers)
@require_http_methods(["GET", "POST"])
def list_rental_order(request):
    product_name = request.GET.get('product_name')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Obtener las órdenes de renta desde la API
    rental_orders = RentalOrderAPI.list_rental_orders()

    # Función auxiliar para filtrar por nombre de producto
    def filter_by_product_name(rental_orders, product_name):
        return [
            ro for ro in rental_orders
            if any(product_name.lower() in item['product_name'].lower() for item in ro['items'])
        ]

    # Función auxiliar para filtrar por fechas
    def filter_by_date(rental_orders, start_date, end_date):
        start_date = parse(start_date).date()
        end_date = parse(end_date).date()
        return [
            ro for ro in rental_orders
            if start_date <= parse(ro['deliver_date']).date() <= end_date
        ]

    # Aplicar filtros
    if product_name:
        rental_orders = filter_by_product_name(rental_orders, product_name)
    if start_date and end_date:
        rental_orders = filter_by_date(rental_orders, start_date, end_date)

    # Calcular totales
    total_accumulated = sum(
        float(item['product_price']) * item['amount']
        for ro in rental_orders
        for item in ro['items']
    )
    total_products_sold = sum(
        item['amount']
        for ro in rental_orders
        for item in ro['items']
    )

    # Añadir total_price a cada orden
    for rental_order in rental_orders:
        rental_order['total_price'] = sum(
            float(item['product_price']) * item['amount']
            for item in rental_order['items']
        )

    # Obtener los productos más vendidos
    all_products = [
        item['product_name']
        for ro in rental_orders
        for item in ro['items']
    ]
    product_counts = Counter(all_products)
    top_products = [
        (product, sum(
            item['amount']
            for ro in rental_orders
            for item in ro['items']
            if item['product_name'] == product
        )) for product, _ in product_counts.most_common(4)
    ]

    # Crear un paginador
    paginator = Paginator(rental_orders, 5)
    page = request.GET.get('page', 1)

    try:
        rental_orders = paginator.page(page)
    except PageNotAnInteger:
        rental_orders = paginator.page(1)
    except EmptyPage:
        rental_orders = paginator.page(paginator.num_pages)

    data = {
        'entity': rental_orders,
        'paginator': paginator,
        'total_accumulated': total_accumulated,
        'total_products_sold': total_products_sold,
        'top_products': top_products,
    }
    return render(request, "app/rental_order/list.html", data)

# Implementacion API Transbank
def webpay_init_transaction(request):
    if request.method == 'POST':
        buy_order = request.POST.get("buy_order")
        session_id = request.POST.get("session_id")
        amount = request.POST.get("amount")

        # Verificar si los valores están vacíos
        if not buy_order or not amount or not session_id:
            return JsonResponse({"error": "Datos faltantes en la solicitud de transacción"})

        # Configuración de Transbank para el ambiente de integración
        return_url = "http://127.0.0.1:8000/webpay/return/"
        tx = Transaction(
            WebpayOptions(
                "597055555532",                       
                "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C",  
                IntegrationType.TEST              # Modo de prueba, cambiar a .LIVE para PRODUCCION    
            )
        )

        response = tx.create(buy_order, session_id, amount, return_url)

        if "token" in response and "url" in response:
            return redirect(response["url"] + "?token_ws=" + response["token"])
        else:
            return JsonResponse({"error": "Error al iniciar la transacción con Webpay.", "detalle": response})

    return JsonResponse({"error": "Método no permitido"}, status=405)

def webpay_return(request):
    """
    Confirma la transacción cuando el usuario regresa desde Webpay.
    Maneja casos de éxito, rechazo o cancelación.
    """
    token_ws = request.GET.get("token_ws")
    tbk_token = request.GET.get("TBK_TOKEN")
    tbk_orden_compra = request.GET.get("TBK_ORDEN_COMPRA")
    tbk_id_sesion = request.GET.get("TBK_ID_SESION")

    # Si el token_ws está presente, intentamos confirmar la transacción
    if token_ws:
        tx = Transaction(
            WebpayOptions(
                "597055555532",                        # Código de comercio de prueba
                "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C",  # API Key de prueba
                IntegrationType.TEST                   # Modo de prueba
            )
        )
        try:
            response = tx.commit(token_ws)
            # Confirmar éxito
            if response.get("response_code") == 0:
                return render(request, "app/transbank/payment_success.html", {"response": response})
            else:
                return render(request, "app/transbank/payment_failed.html", {"error": "Transacción rechazada."})
        except Exception as e:
            return render(request, "app/transbank/payment_failed.html", {"error": f"Error al confirmar transacción: {str(e)}"})

    # Si TBK_TOKEN está presente, significa que la compra fue anulada
    elif tbk_token:
        return render(request, "app/transbank/payment_failed.html", {
            "error": "Compra anulada por el usuario.",
            "tbk_token": tbk_token,
            "tbk_orden_compra": tbk_orden_compra,
            "tbk_id_sesion": tbk_id_sesion,
        })

    # Si no hay parámetros relevantes, mostramos un error genérico
    return render(request, "app/transbank/payment_failed.html", {"error": "Error desconocido al procesar la transacción."})

