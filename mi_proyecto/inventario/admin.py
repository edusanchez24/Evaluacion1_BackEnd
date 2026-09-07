from django.contrib import admin
from .models import Cliente, Producto, Venta

admin.site.register(Producto)
admin.site.register(Cliente)
admin.site.register(Venta)
