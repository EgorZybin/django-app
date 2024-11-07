from django.contrib.auth.models import User

from django.core.management import BaseCommand

from shopapp.models import Product


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write('Start demo selecting fields')
        users_info = User.objects.values_list('pk', 'username')
        for user_info in users_info:
            print(user_info)
        # products_values = Product.objects.values('pk', 'name')
        # for p_values in products_values:
        #     print(p_values)


        self.stdout.write("Done")
