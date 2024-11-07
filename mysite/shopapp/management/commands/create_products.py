from django.core.management import BaseCommand
from shopapp.models import Product


class Command(BaseCommand):
    """
    Create Products
    """

    def handle(self, *args, **options):
        self.stdout.write('Creating products...')

        products_names = [
            ['Laptop', 1999, 10],
            ['Desktop', 2999, 5],
            ['Smartphone', 999, 20],
        ]

        for products_name in products_names:
            product, created = Product.objects.get_or_create(name=products_name[0], price=products_name[1],
                                                             count=products_name[2])
            self.stdout.write(f"Product {product.name} created!")

        self.stdout.write(self.style.SUCCESS('Products created!'))
