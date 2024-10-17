#importaciones estándar de Python
from dataclasses import fields

#importaciones de terceros
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import MinValueValidator
from django.forms import ModelForm

#importaciones del proyecto
from .models import Contact, Product, Category, QueryType, RentalOrder, Usuarios
from .validators import MaxSizeFileValidator, validate_phone


# Definir constantes para etiquetas repetidas
EMAIL_LABEL = 'Correo electrónico'
PHONE_LABEL = 'Teléfono'
MAX_IMAGE_SIZE_MB = 20

class PhoneField(forms.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 9
        kwargs['validators'] = [validate_phone]
        kwargs['label'] = PHONE_LABEL
        super().__init__(*args, **kwargs)

class ContactForm(forms.ModelForm):
    name = forms.CharField(min_length=8, max_length=50, required=True, label='Nombre completo')
    email = forms.EmailField(required=True, label=EMAIL_LABEL)
    phone = PhoneField()
    message = forms.CharField(required=True, max_length=200, label='Mensaje', widget=forms.Textarea)
    query_type = forms.ModelChoiceField(queryset=QueryType.objects.all(), required=True, label='Tipo de consulta')

    class Meta:
        model = Contact
        fields = ["name", "email", "phone", "message", "query_type"]
        labels = {
            'name': 'Nombre completo',
            'email': EMAIL_LABEL,
            'phone': PHONE_LABEL,
            'message': 'Mensaje',
            'query_type': 'Tipo de consulta'
        }

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        query_type = cleaned_data.get('query_type')
        name = cleaned_data.get('name')

        if not email:
            self.add_error('email', 'Este campo es obligatorio.')
        if not query_type:
            self.add_error('query_type', 'Este campo es obligatorio.')
        if name and len(name) < 8:
            self.add_error(
                'name', 'El nombre debe tener al menos 8 caracteres.')

class QueryTypeForm(forms.ModelForm):
    name = forms.CharField(min_length=3, max_length=50)

    class Meta:
        model = QueryType
        fields = ['name', 'description']
        labels = {
            'name': 'Nombre',
            'description': 'Descripcion',
        }

class ProductForm(forms.ModelForm):
    image = forms.ImageField(required=False, validators=[MaxSizeFileValidator(MAX_IMAGE_SIZE_MB)])
    name = forms.CharField(min_length=3, max_length=50)
    price = forms.IntegerField(min_value=1, max_value=1500000)
    stock = forms.IntegerField(validators=[MinValueValidator(0)])
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=True)


    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'category', 'stock', 'is_new', 'is_featured', 'image', 'is_rentable']
        labels = {
            'name': 'Nombre',
            'description': 'Descripción',
            'price': 'Precio',
            'category': 'Categoría',
            'stock': 'Unidades',
            'is_new': '¿Nuevo?',
            'is_featured': '¿Destacado?',
            'image': 'Imagen',
            'is_rentable': '¿Arrendable?'
        }

class CustomUserCreationForm(UserCreationForm):
    pass

class CategoryForm(forms.ModelForm):

    image = forms.ImageField(required=False, validators=[MaxSizeFileValidator(MAX_IMAGE_SIZE_MB)])
    name = forms.CharField(min_length=3, max_length=50)

    class Meta:
        model = Category
        fields = ['name', 'description', 'image']
        labels = {
            'name': 'Nombre',
            'description': 'Descripcion',
            'image': 'Imagen'
        }

class UsuariosForm(ModelForm):
    #se da formato a cada uno de los campos dentro de la forma
    usrN = forms.CharField(widget=forms.EmailInput(attrs={'class':'login-username','placeholder':'Email'}),label='')
    pswrdN = forms.CharField(widget=forms.PasswordInput(attrs={'class':'login-password','placeholder':'Contraseña'}),label='')
    pswrdN2= forms.CharField(widget=forms.PasswordInput(attrs={'class':'login-password','placeholder':'Repetir Contraseña'}),label='')
    class Meta:
        #se asigna modelo y orden de aparicion en html
        model = Usuarios
        fields= ['usrN','pswrdN','pswrdN2']

class LoginForm(ModelForm):
    usrN = forms.CharField(widget=forms.TextInput(attrs={'class':'login-username','placeholder':'Username'}),label='')
    pswrdN = forms.CharField(widget=forms.PasswordInput(attrs={'class':'login-password','placeholder':'Contraseña'}),label='')
    class Meta:
        model=Usuarios
        fields= ['usrN','pswrdN']
        
class RentalOrderForm(forms.ModelForm):
    name = forms.CharField(min_length=3, max_length=50)
    phone = PhoneField()


    class Meta:
        model = RentalOrder
        fields = ['rut', 'name', 'address', 'email', 'phone', 'deliver_date']
        labels = {
            'rut': 'Rut',
            'name': 'Nombre',
            'address': 'Direccion',
            'email': EMAIL_LABEL,
            'phone': PHONE_LABEL,
            'deliver_date': 'Fecha de entrega'
        }

class RecuperarForm(forms.Form):
    email = forms.EmailField(label=EMAIL_LABEL)
