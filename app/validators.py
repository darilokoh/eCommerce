from django.forms import ValidationError

class MaxSizeFileValidator:
    def __init__(self, max_file_size=20):  # El tamaño máximo en MB
        self.max_file_size = max_file_size

    def __call__(self, value):
        size = value.size
        max_size = self.max_file_size * 1048576  # Convertir MB a bytes

        if size > max_size:
            raise ValidationError(f"El tamaño máximo del archivo debe ser de {self.max_file_size}MB")
        return value
    
def validate_phone(phone):
    if len(str(phone)) != 9:
        raise ValidationError("El número de teléfono debe contener 9 dígitos.")
    return phone
    