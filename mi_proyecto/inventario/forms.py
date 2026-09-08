from django import forms
from .models import Cliente, Producto, Venta

class ProductoChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.codigo} - {obj.nombre}'


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'codigo', 'precio', 'descripcion', 'stock']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border border-slate-300 bg-white/80 px-3 py-2.5 text-slate-950 shadow-sm outline-none transition duration-200 placeholder:text-slate-400 hover:border-slate-400 focus:border-sky-600 focus:bg-white focus:ring-4 focus:ring-sky-100',
                'placeholder': 'Ej. Auriculares inalambricos',
                'autocomplete': 'off',
            }),
            'codigo': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border border-slate-300 bg-white/80 px-3 py-2.5 text-slate-950 shadow-sm outline-none transition duration-200 placeholder:text-slate-400 hover:border-slate-400 focus:border-sky-600 focus:bg-white focus:ring-4 focus:ring-sky-100',
                'placeholder': 'Ej. AUD-001',
                'autocomplete': 'off',
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'w-full rounded-xl border border-slate-300 bg-white/80 px-3 py-2.5 text-slate-950 shadow-sm outline-none transition duration-200 placeholder:text-slate-400 hover:border-slate-400 focus:border-sky-600 focus:bg-white focus:ring-4 focus:ring-sky-100',
                'placeholder': '0',
                'min': '0',
                'inputmode': 'numeric',
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'min-h-28 w-full resize-y rounded-xl border border-slate-300 bg-white/80 px-3 py-2.5 text-slate-950 shadow-sm outline-none transition duration-200 placeholder:text-slate-400 hover:border-slate-400 focus:border-sky-600 focus:bg-white focus:ring-4 focus:ring-sky-100',
                'placeholder': 'Describe el producto brevemente',
                'rows': 4,
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'w-full rounded-xl border border-slate-300 bg-white/80 px-3 py-2.5 text-slate-950 shadow-sm outline-none transition duration-200 placeholder:text-slate-400 hover:border-slate-400 focus:border-sky-600 focus:bg-white focus:ring-4 focus:ring-sky-100',
                'placeholder': '0',
                'min': '0',
                'inputmode': 'numeric',
            }),
        }


class VentaForm(forms.Form):
    rut_cliente = forms.CharField(max_length=12, required=True, label='RUT del cliente')
    cliente_habitual = forms.BooleanField(required=False, label='Guardar como cliente habitual')
    nombre = forms.CharField(required=False, max_length=128)
    telefono = forms.CharField(required=False, max_length=30)
    direccion = forms.CharField(required=False, max_length=200)
    correo = forms.EmailField(required=False)
    producto = ProductoChoiceField(queryset=Producto.objects.all(), label='Producto')

    producto = ProductoChoiceField(queryset=Producto.objects.all(), label='Producto')
    cantidad = forms.IntegerField(
        min_value=1,
        error_messages={'min_value': 'La cantidad debe ser al menos 1.'},
        label='Cantidad',
        widget=forms.NumberInput(attrs={'min': '1', 'inputmode': 'numeric'}),
    )

    rut_cliente = forms.CharField(max_length=12, required=True, label='RUT del cliente', widget=forms.TextInput(attrs={'placeholder': '12.345.678-9', 'autocomplete': 'off'}))

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')
        if cantidad is not None and cantidad < 1:
            self.add_error('cantidad', 'La cantidad debe ser al menos 1.')
        if producto and cantidad and cantidad > producto.stock:
            self.add_error('cantidad', f'El producto solo tiene {producto.stock} unidades disponibles.')

        if cleaned_data.get('cliente_habitual'):
            required_fields = ('nombre', 'telefono', 'direccion', 'correo')
            for field_name in required_fields:
                if not cleaned_data.get(field_name):
                    self.add_error(field_name, 'Completa este dato para guardar el cliente habitual.')
        return cleaned_data

    def save(self, commit=True):
        venta = super().save(commit=False)
        if self.cleaned_data.get('cliente_habitual'):
            cliente, _ = Cliente.objects.update_or_create(
                rut=self.cleaned_data['rut_cliente'],
                defaults={
                    'nombre': self.cleaned_data['nombre'],
                    'telefono': self.cleaned_data['telefono'],
                    'direccion': self.cleaned_data['direccion'],
                    'correo': self.cleaned_data['correo'],
                },
            )
            venta.cliente = cliente
        if commit:
            venta.save()
        return venta