from random import choices
from string import ascii_letters
from django.conf import settings
from django.contrib.auth.models import User, Group, Permission
from django.test import TestCase, Client

from shopapp.models import Product, Order
from shopapp.utils import add_two_numbers
from django.urls import reverse


# Create your tests here.

class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEqual(result, 5)


class ProductCreateViewTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        Group.objects.create(name='staff')

    def setUp(self):
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.force_login(self.user)
        group = Group.objects.get(name='staff')
        self.user.groups.add(group)
        self.user.save()
        self.user.user_permissions.add(Permission.objects.get(codename='add_product'))

    def test_product_create_view(self):
        response = self.client.post(
            reverse("shopapp:product_create"),
            {
                "name": self.product_name,
                "price": 9.99,
                "count": 10,
                "description": "Test description",
                "discount": 0,
                "created_by": self.user.id,
            },
            HTTP_USER_AGENT='Mozilla/5.0'
        )

        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(
            Product.objects.filter(name=self.product_name).exists()
        )


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='testuser', password='password')
        cls.client = Client()
        cls.client.force_login(cls.user)
        group, created = Group.objects.get_or_create(name='staff')
        cls.user.groups.add(group)
        cls.user.save()
        cls.user.user_permissions.add(Permission.objects.get(codename='add_product'))
        cls.product = Product.objects.create(name="Test Product", price=9.99, count=10, description="Test description",
                                             discount=0, created_by=cls.user)

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()

    def test_get_product(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk}), HTTP_USER_AGENT='Mozilla/5.0'
        )
        self.assertEqual(response.status_code, 200)

    def test_post_product(self):
        response = self.client.post(reverse("shopapp:product_details", kwargs={"pk": self.product.pk}),
                                    HTTP_USER_AGENT='Mozilla/5.0')
        self.assertEqual(response.status_code, 405)

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk}), HTTP_USER_AGENT='Mozilla/5.0'
        )
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = [
        'users-fixture.json',
        'products-fixture.json',
    ]

    def test_products(self):
        user = User.objects.get(username='admin')
        self.client.force_login(user)
        response = self.client.get(reverse("shopapp:products_list"), HTTP_USER_AGENT='Mozilla/5.0')
        products = Product.objects.filter(archived=False).all()
        self.assertQuerySetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context['products']),
            transform=lambda p: p.pk,
        )
        self.assertTemplateUsed(response, 'shopapp/products.html')


class OrdersListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='testuser', password='password')

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse("shopapp:orders_list"), HTTP_USER_AGENT='Mozilla/5.0')
        self.assertContains(response, "Orders")

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:orders_list"), HTTP_USER_AGENT='Mozilla/5.0')
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        'users-fixture.json',
        'products-fixture.json',
    ]

    def test_get_products_view(self):
        response = self.client.get(reverse("shopapp:products-export"), HTTP_USER_AGENT='Mozilla/5.0')
        self.assertEqual(response.status_code, 200)

        products = Product.objects.order_by('pk').all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "description": product.description,
                "price": str(product.price),
                "count": product.count,
                "discount": product.discount,
                "archived": product.archived,
                "created_by": product.created_by.pk
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(
            products_data['products'],
            expected_data,
        )


class OrderDetailViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser', password='testpass')
        cls.user.is_superuser = True
        cls.user.save()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()
        super().tearDownClass()

    def setUp(self):
        self.client.login(username='testuser', password='testpass')
        self.order = Order.objects.create(user=self.user, delivery_address='123 Main St', promocode='DISCOUNT10')

    def tearDown(self):
        self.order.delete()

    def test_order_details(self):
        response = self.client.get(reverse('shopapp:orders_details', args=[self.order.pk]),
                                   HTTP_USER_AGENT='Mozilla/5.0')

        self.assertEqual(response.status_code, 200)

        self.assertContains(response, self.order.delivery_address)

        self.assertContains(response, self.order.promocode)

        self.assertEqual(response.context['order'].pk, self.order.pk)


class OrdersExportTestCase(TestCase):
    fixtures = [
        'users-fixture.json',
        'products-fixture.json',
        'orders-fixture.json',
    ]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

    def setUp(self):
        self.user = User.objects.get(username='admin')
        self.client.force_login(self.user)

    def test_orders_export(self):
        response = self.client.get(reverse('shopapp:orders-export'), HTTP_USER_AGENT='Mozilla/5.0')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('orders', data)
        orders = Order.objects.all()
        self.assertEqual(len(data['orders']), len(orders))
        for i, order in enumerate(orders):
            self.assertEqual(data['orders'][i]['id'], order.id)
            self.assertEqual(data['orders'][i]['delivery_address'], order.delivery_address)
            self.assertEqual(data['orders'][i]['promocode'], order.promocode)
            self.assertEqual(data['orders'][i]['user_id'], order.user_id)
            self.assertEqual(data['orders'][i]['product_ids'], [product.id for product in order.products.all()])
