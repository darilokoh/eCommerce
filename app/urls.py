from django.urls import path, include

#Imports de views
from .views import home, rental_service, catalogue, contact,\
    add_product, list_product, update_product, delete_product,\
    product_detail, add_prod_cart, del_prod_cart, subtract_product_cart,\
    clean_cart, cart_page, buy_confirm, add_category,list_category, update_category,\
    delete_category, admin_panel, checkout_view, list_contact, update_contact_status,\
    add_query_type, list_query_type, update_query_type, delete_query_type, list_rental_order,\
    webpay_init_transaction, webpay_return

# Imports de ViewSets
from .views import ProductViewset, CategoryViewset, ContactViewSet, QueryTypeViewset, RentalOrderViewSet,\
    RentalOrderItemViewSet, RegionViewSet, MunicipalityViewSet, OrderViewSet, OrderItemViewSet

from . import views
from .views import Registrar, order_list
from django.contrib.auth.views import LoginView
from .views import Recuperar,login
from .views import user_login
from django.urls import path
from .views import CambiarPassword
from .views import payment_success
from .views import obtain_token
from rest_framework import routers

# Definición de Routers para API´s
router = routers.DefaultRouter()
router.register('product', ProductViewset)
router.register('category', CategoryViewset)
router.register('contact', ContactViewSet, basename='contact')
router.register('query-type', QueryTypeViewset, basename='query-type')
router.register(r'rental-orders', RentalOrderViewSet, basename='rental-orders')
router.register(r'rental-order-items', RentalOrderItemViewSet)
router.register('regions', RegionViewSet, basename='regions')
router.register('municipalities', MunicipalityViewSet, basename='municipalities')
router.register('orders', OrderViewSet, basename='orders')
router.register('order-items', OrderItemViewSet, basename='order-items')

urlpatterns = [
    path('CambiarPassword/', CambiarPassword, name='CambiarPassword'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', home, name="home"),
    path('catalogue/', catalogue, name="catalogue"),
    path('rental-service/', rental_service, name="rental_service"),
    path('contact/', contact, name="contact"),
    path('list-contact/', list_contact, name="list_contact"),
    path('update-status/<int:contact_id>/', update_contact_status, name='update_status'),
    path('add-query-type/', add_query_type, name="add_query_type"),
    path('list-query-type/', list_query_type, name="list_query_type"),
    path('update-query-type/<int:id>/', update_query_type, name="update_query_type"),
    path('delete-query-type/<id>/', delete_query_type, name="delete_query_type"),
    path('add-product/', add_product, name="add_product"),
    path('list-product/', list_product, name="list_product"),
    path('update-product/<int:id>/', update_product, name="update_product"),
    path('delete-product/<id>/', delete_product, name="delete_product"),
    path('product-detail/<int:id>/', product_detail, name="product_detail"),
    path('add-category/', add_category, name="add_category"),
    path('list-category/', list_category, name="list_category"),
    path('update-category/<id>/', update_category, name="update_category"),
    path('delete-category/<id>/', delete_category, name="delete_category"),
    path('api/', include(router.urls)),
    path("add/<int:product_id>", add_prod_cart, name="Add"),
    path("delete/<int:product_id>", del_prod_cart, name="Del"),
    path("subtract/<int:product_id>", subtract_product_cart, name="Sub"),
    path("clean/", clean_cart, name="Clean"),
    path("cart/", cart_page, name="Cart"),
    path("buy-confirm/", buy_confirm, name="buy_confirm"),
    path("admin-panel/", admin_panel, name="admin_panel"),
    path('checkout/', checkout_view, name="checkout_view"),
    path('Recuperar/', Recuperar, name='Recuperar'),
    path('payment_success/', payment_success, name='payment_success'),
    path('payment_success/', views.update_last_order_paid_status, name='update_last_order_paid_status'),
    path('orders/', order_list, name='order_list'),
    path('list-rental-order/', list_rental_order, name="list_rental_order"),
    path('Registrar/', Registrar, name='Registrar'),   
    path('payment_success/', payment_success, name='payment_success'),
    path('payment_success/', views.update_last_order_paid_status, name='update_last_order_paid_status'),
    path('api/token/', views.obtain_token, name='obtain_token'),
    path('login/', user_login, name='login'),
    path('api/token/', obtain_token, name='obtain_token'),
    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('api/login', login, name='login_api'),
    path("webpay/init/", webpay_init_transaction, name="webpay_init"),
    path("webpay/return/", webpay_return, name="webpay_return"),
]
