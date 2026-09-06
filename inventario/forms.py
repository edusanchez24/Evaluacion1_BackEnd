from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'descripcion', 'stock']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full rounded-xl border border-slate-300 bg-white/80 px-3 py-2.5 text-slate-950 shadow-sm outline-none transition duration-200 placeholder:text-slate-400 hover:border-slate-400 focus:border-sky-600 focus:bg-white focus:ring-4 focus:ring-sky-100',
                'placeholder': 'Ej. Auriculares inalambricos',
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