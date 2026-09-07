from django.test import TestCase
from .models import Cliente, Producto, Venta

# Create your tests here.
class VentaFlowTests(TestCase):
	def setUp(self):
		self.producto = Producto.objects.create(nombre='Teclado', codigo='TEC-001', precio=10000, stock=5)

	def test_venta_ocasional_guarda_rut_total_y_descuenta_stock(self):
		response = self.client.post('/ventas/nueva/', {
			'rut_cliente': '11.111.111-1',
			'producto': self.producto.pk,
			'cantidad': 2,
		})

		self.assertRedirects(response, '/ventas/')
		venta = Venta.objects.get()
		self.assertEqual(venta.rut_cliente, '11.111.111-1')
		self.assertIsNone(venta.cliente)
		self.assertEqual(venta.total, 20000)
		self.assertEqual(Producto.objects.get(pk=self.producto.pk).stock, 3)

	def test_venta_puede_guardar_cliente_habitual(self):
		response = self.client.post('/ventas/nueva/', {
			'rut_cliente': '22.222.222-2',
			'producto': self.producto.pk,
			'cantidad': 1,
			'cliente_habitual': 'on',
			'nombre': 'Ana Perez',
			'telefono': '+56912345678',
			'direccion': 'Av. Central 123',
			'correo': 'ana@example.com',
		})

		self.assertRedirects(response, '/ventas/')
		self.assertEqual(Cliente.objects.get(rut='22.222.222-2').nombre, 'Ana Perez')
		self.assertEqual(Venta.objects.get().cliente.rut, '22.222.222-2')

	def test_no_permite_vender_mas_stock_disponible(self):
		response = self.client.post('/ventas/nueva/', {
			'rut_cliente': '33.333.333-3',
			'producto': self.producto.pk,
			'cantidad': 6,
		})

		self.assertEqual(response.status_code, 200)
		self.assertFalse(Venta.objects.exists())
		self.assertEqual(Producto.objects.get(pk=self.producto.pk).stock, 5)
