from typing import Sequence

from django.contrib.auth.models import User
from django.core.management import BaseCommand
from django.db import transaction
from shopapp.models import Order, Product


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write('Creating order with products')

        user = User.objects.get(username='admin')
        products: Sequence[Product] = Product.objects.defer('description', 'price', 'created_at').all()
        order, created = Order.objects.get_or_create(
            delivery_address='ul Ivanova, d 10, kv 1',
            promocode='promo1',
            user=user,
        )
        for product in products:
            order.products.add(product)

        order.save()
        self.stdout.write(f"Order {order} created!")
