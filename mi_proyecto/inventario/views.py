from django.contrib import messages
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from .models import Producto, Venta
from .forms import ProductoForm, VentaForm

from django.views.decorators.csrf import csrf_protect

# Create your views here.
def producto_list(request):
    productos = Producto.objects.order_by('nombre')
    return render(request, 'inventario/producto_list.html', {'object_list': productos})

def producto_detail(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'inventario/producto_detail.html', {'object': producto})

@csrf_protect
def producto_create(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('producto_list')

    else:
        form = ProductoForm()
        return render(request, 'inventario/producto_form.html', {'form': form})

@csrf_protect
def producto_update(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)

        if form.is_valid():
            form.save()
            return redirect('producto_list')

    else:
        form = ProductoForm(instance=producto)
        return render(request, 'inventario/producto_form.html', {'form': form})

@csrf_protect
def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk)

    if request.method == 'POST':
        producto.delete()
        return redirect('producto_list')

    return render(request, 'inventario/producto_confirm_delete.html', {'object': producto})


def venta_list(request):
    ventas = Venta.objects.select_related('producto', 'cliente').order_by('-fecha')
    return render(request, 'inventario/venta_list.html', {'ventas': ventas})


@csrf_protect
def venta_create(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                producto = Producto.objects.select_for_update().get(pk=form.cleaned_data['producto'].pk)
                cantidad = form.cleaned_data['cantidad']
                if cantidad > producto.stock:
                    form.add_error('cantidad', f'El producto solo tiene {producto.stock} unidades disponibles.')
                else:
                    form.instance.producto = producto
                    venta = form.save()
                    producto.stock -= cantidad
                    producto.save(update_fields=['stock'])
                    messages.success(request, f'Venta registrada por ${venta.total}.')
                    return redirect('venta_list')
    else:
        form = VentaForm()
    return render(request, 'inventario/venta_form.html', {'form': form})