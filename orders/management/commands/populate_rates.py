from django.core.management.base import BaseCommand
from orders.models import ShippingRate

class Command(BaseCommand):
    help = 'Populate shipping rates from tariff'

    def handle(self, *args, **options):
        rates = [
            ('Mostaganem', 600, 400),
            ('Mascara', 750, 450),
            ('Saida', 750, 450),
            ('Oran', 750, 450),
            ('Alger', 700, 450),
            ('Boumerdès', 800, 500),
            ('Blida', 800, 500),
            ('Tipaza', 800, 500),
            ('Tizi Ouzou', 800, 500),
            ('Bouira', 800, 500),
            ('Bejaia', 800, 500),
            ('Médéa', 800, 500),
            ('Ain Defla', 800, 500),
            ('AinTimouchent', 800, 500),
            ('Chlef', 800, 500),
            ('Constantine', 800, 500),
            ('Setif', 800, 500),
            ('Tiaret', 800, 500),
            ('Tlemcen', 800, 500),
            ('Relizane', 800, 500),
            ('Sidi Bel Abbes', 800, 500),
            ('Jijel', 900, 600),
            ('Bordj Bou Arreridj', 900, 600),
            ('Annaba', 900, 600),
            ('Batna', 900, 600),
            ('Tissemsilt', 900, 600),
            ('Skikda', 900, 600),
            ('Mila', 900, 600),
            ('M\'Sila', 900, 600),
            ('El Tarf', 950, 600),
            ('Guelma', 950, 600),
            ('Kenchela', 950, 600),
            ('Oum El Bouagui', 950, 600),
            ('Souk Ahrass', 950, 600),
            ('Tebessa', 1000, 600),
            ('Laghouat', 1000, 600),
            ('Djelfa', 1000, 600),
            ('Biskra', 1000, 600),
            ('Ouled Djellal', 1000, 0),
            ('Ghardaïa', 1100, 700),
            ('El Meniaa', 1100, 700),
            ('El Oued', 1100, 700),
            ('El M\'Ghair', 1100, 0),
            ('Ouargla', 1100, 700),
            ('Touggourt', 1100, 700),
            ('El Bayadh', 1200, 800),
            ('Naama', 1200, 800),
            ('Bechar', 1200, 800),
            ('Béni Abbès', 1200, 0),
            ('Adrar', 1500, 1000),
            ('Timimoun', 1500, 1000),
            ('Tindouf', 1700, 1000),
            ('In Salah', 1800, 1200),
            ('Ilizi', 1900, 1500),
            ('Tamenrasset', 2000, 1500),
            ('Djanet', 2200, 0),
        ]
        
        for wilaya, home, desk in rates:
            ShippingRate.objects.update_or_create(
                wilaya=wilaya,
                defaults={
                    'home_delivery_price': home,
                    'stop_desk_price': desk if desk > 0 else home,
                    'return_cost': 300
                }
            )
            self.stdout.write(f'✓ {wilaya}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ {len(rates)} shipping rates added!'))