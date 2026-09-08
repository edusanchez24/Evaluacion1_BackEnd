from django.test import TestCase
from .forms import VentaForm
from .models import Cliente, Producto, Venta, VentaDetalle

# Create your tests here.
class VentaFlowTests(TestCase):
	def setUp(self):
		self.producto = Producto.objects.create(nombre='Teclado', codigo='TEC-001', precio=10000, stock=5)

	def test_venta_ocasional_guarda_rut_total_y_descuenta_stock(self):
		self.client.post('/ventas/nueva/', {
			'accion': 'agregar',
			'rut_cliente': '11.111.111-1',
			'producto': self.producto.pk,
			'cantidad': 2,
		})
		response = self.client.post('/ventas/nueva/', {'accion': 'registrar'})

		self.assertRedirects(response, '/ventas/')
		venta = Venta.objects.get()
		self.assertEqual(venta.rut_cliente, '11.111.111-1')
		self.assertIsNone(venta.cliente)
		self.assertEqual(venta.total, 20000)
		self.assertEqual(venta.detalles.get().cantidad, 2)
		self.assertEqual(Producto.objects.get(pk=self.producto.pk).stock, 3)

	def test_venta_puede_guardar_cliente_habitual(self):
		self.client.post('/ventas/nueva/', {
			'accion': 'agregar',
			'rut_cliente': '22.222.222-2',
			'producto': self.producto.pk,
			'cantidad': 1,
			'cliente_habitual': 'on',
			'nombre': 'Ana Perez',
			'telefono': '+56912345678',
			'direccion': 'Av. Central 123',
			'correo': 'ana@example.com',
		})
		response = self.client.post('/ventas/nueva/', {'accion': 'registrar'})

		self.assertRedirects(response, '/ventas/')
		self.assertEqual(Cliente.objects.get(rut='22.222.222-2').nombre, 'Ana Perez')
		self.assertEqual(Venta.objects.get().cliente.rut, '22.222.222-2')

	def test_selector_de_venta_muestra_codigo_y_nombre(self):
		form = VentaForm()

		self.assertIn('TEC-001 - Teclado', str(form['producto']))

	def test_no_permite_vender_mas_stock_disponible(self):
		response = self.client.post('/ventas/nueva/', {
			'accion': 'agregar',
			'rut_cliente': '33.333.333-3',
			'producto': self.producto.pk,
			'cantidad': 6,
		})

		self.assertEqual(response.status_code, 200)
		self.assertFalse(Venta.objects.exists())
		self.assertEqual(Producto.objects.get(pk=self.producto.pk).stock, 5)

	def test_no_permite_agregar_cantidad_cero(self):
		response = self.client.post('/ventas/nueva/', {
			'accion': 'agregar',
			'rut_cliente': '44.444.444-4',
			'producto': self.producto.pk,
			'cantidad': 0,
		})

		self.assertEqual(response.status_code, 200)
		self.assertFalse(Venta.objects.exists())
		self.assertContains(response, 'La cantidad debe ser al menos 1.')

	def test_puede_agregar_varios_productos_y_confirmar_una_venta(self):
		otro_producto = Producto.objects.create(nombre='Mouse', codigo='MOU-001', precio=5000, stock=4)
		cliente_data = {'rut_cliente': '55.555.555-5'}

		self.client.post('/ventas/nueva/', {
			'accion': 'agregar',
			**cliente_data,
			'producto': self.producto.pk,
			'cantidad': 2,
		})
		self.client.post('/ventas/nueva/', {
			'accion': 'agregar',
			**cliente_data,
			'producto': otro_producto.pk,
			'cantidad': 1,
		})
		confirmacion = self.client.post('/ventas/nueva/', {'accion': 'confirmar'})

		self.assertEqual(confirmacion.status_code, 200)
		self.assertContains(confirmacion, 'Confirmar venta')
		self.assertEqual(Venta.objects.count(), 0)

		respuesta = self.client.post('/ventas/nueva/', {'accion': 'registrar'})

		self.assertRedirects(respuesta, '/ventas/')
		self.assertEqual(Venta.objects.count(), 1)
		self.assertEqual(VentaDetalle.objects.count(), 2)
		self.assertEqual(Venta.objects.get().total, 25000)
		self.assertEqual(Producto.objects.get(pk=self.producto.pk).stock, 3)
		self.assertEqual(Producto.objects.get(pk=otro_producto.pk).stock, 3)

	def test_puede_eliminar_producto_del_carrito(self):
		self.client.post('/ventas/nueva/', {
			'accion': 'agregar',
			'rut_cliente': '66.666.666-6',
			'producto': self.producto.pk,
			'cantidad': 1,
		})

		respuesta = self.client.post('/ventas/nueva/', {
			'accion': 'eliminar',
			'producto_id': self.producto.pk,
		})

		self.assertRedirects(respuesta, '/ventas/nueva/')
		self.assertNotIn(str(self.producto.pk), self.client.session.get('venta_carrito', {}))

	def test_volver_desde_confirmacion_conserva_productos_y_datos(self):
		self.client.post('/ventas/nueva/', {
			'accion': 'agregar',
			'rut_cliente': '77.777.777-7',
			'producto': self.producto.pk,
			'cantidad': 1,
			'nombre': 'Luis Soto',
			'telefono': '999999999',
			'direccion': 'Calle 1',
			'correo': 'luis@example.com',
		})
		self.client.post('/ventas/nueva/', {'accion': 'confirmar'})

		respuesta = self.client.post('/ventas/nueva/', {'accion': 'volver'})

		self.assertRedirects(respuesta, '/ventas/nueva/')
		pagina = self.client.get('/ventas/nueva/')
		self.assertContains(pagina, 'Luis Soto')
		self.assertContains(pagina, 'TEC-001 - Teclado')

	def test_rut_de_cliente_habitual_devuelve_sus_datos(self):
		Cliente.objects.create(
			rut='88.888.888-8',
			nombre='Maria Perez',
			telefono='888888888',
			direccion='Avenida 2',
			correo='maria@example.com',
		)

		respuesta = self.client.get('/clientes/por-rut/?rut=88.888.888-8')

		self.assertJSONEqual(respuesta.content, {
			'encontrado': True,
			'nombre': 'Maria Perez',
			'telefono': '888888888',
			'direccion': 'Avenida 2',
			'correo': 'maria@example.com',
		})
