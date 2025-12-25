from django.core.management.base import BaseCommand
from orders.models import StopDesk

class Command(BaseCommand):
    help = 'Populate sample Stop Desk locations across Algeria'

    def handle(self, *args, **options):
        # Sample Stop Desk locations (you can add real ones later)
        stop_desks = [
            # Oran
            {
                'name': 'Stop Desk Oran Centre',
                'wilaya': 'Oran',
                'city': 'Oran',
                'address': 'Place du 1er Novembre, Centre Ville, Oran',
                'phone': '+213 41 XX XX XX',
                'latitude': 35.6976,
                'longitude': -0.6337,
                'working_hours': '08:00 - 19:00',
                'working_days': 'Sunday - Thursday'
            },
            {
                'name': 'Stop Desk Es Senia',
                'wilaya': 'Oran',
                'city': 'Es Senia',
                'address': 'Route de l\'Aéroport, Es Senia, Oran',
                'phone': '+213 41 XX XX XX',
                'latitude': 35.6471,
                'longitude': -0.6216,
                'working_hours': '08:00 - 18:00',
                'working_days': 'Sunday - Thursday'
            },
            
            # Alger
            {
                'name': 'Stop Desk Alger Centre',
                'wilaya': 'Alger',
                'city': 'Alger',
                'address': 'Rue Didouche Mourad, Alger Centre',
                'phone': '+213 21 XX XX XX',
                'latitude': 36.7538,
                'longitude': 3.0588,
                'working_hours': '08:00 - 20:00',
                'working_days': 'Sunday - Thursday'
            },
            {
                'name': 'Stop Desk Bab Ezzouar',
                'wilaya': 'Alger',
                'city': 'Bab Ezzouar',
                'address': 'Cité CNEP, Bab Ezzouar, Alger',
                'phone': '+213 21 XX XX XX',
                'latitude': 36.7189,
                'longitude': 3.1847,
                'working_hours': '08:00 - 19:00',
                'working_days': 'Sunday - Thursday'
            },
            {
                'name': 'Stop Desk Hydra',
                'wilaya': 'Alger',
                'city': 'Hydra',
                'address': 'Chemin Mackley, Hydra, Alger',
                'phone': '+213 21 XX XX XX',
                'latitude': 36.7464,
                'longitude': 3.0351,
                'working_hours': '09:00 - 18:00',
                'working_days': 'Sunday - Thursday'
            },
            
            # Constantine
            {
                'name': 'Stop Desk Constantine Centre',
                'wilaya': 'Constantine',
                'city': 'Constantine',
                'address': 'Boulevard de la Soummam, Constantine',
                'phone': '+213 31 XX XX XX',
                'latitude': 36.3650,
                'longitude': 6.6147,
                'working_hours': '08:00 - 19:00',
                'working_days': 'Sunday - Thursday'
            },
            {
                'name': 'Stop Desk Zouaghi',
                'wilaya': 'Constantine',
                'city': 'Constantine',
                'address': 'Cité Zouaghi, Constantine',
                'phone': '+213 31 XX XX XX',
                'latitude': 36.3400,
                'longitude': 6.6100,
                'working_hours': '08:00 - 18:00',
                'working_days': 'Sunday - Thursday'
            },
            
            # Sétif
            {
                'name': 'Stop Desk Sétif Centre',
                'wilaya': 'Sétif',
                'city': 'Sétif',
                'address': 'Avenue 8 Mai 1945, Sétif',
                'phone': '+213 36 XX XX XX',
                'latitude': 36.1910,
                'longitude': 5.4131,
                'working_hours': '08:00 - 19:00',
                'working_days': 'Sunday - Thursday'
            },
            
            # Annaba
            {
                'name': 'Stop Desk Annaba Centre',
                'wilaya': 'Annaba',
                'city': 'Annaba',
                'address': 'Cours de la Révolution, Annaba',
                'phone': '+213 38 XX XX XX',
                'latitude': 36.9000,
                'longitude': 7.7667,
                'working_hours': '08:00 - 19:00',
                'working_days': 'Sunday - Thursday'
            },
            
            # Tlemcen
            {
                'name': 'Stop Desk Tlemcen Centre',
                'wilaya': 'Tlemcen',
                'city': 'Tlemcen',
                'address': 'Boulevard du 1er Novembre, Tlemcen',
                'phone': '+213 43 XX XX XX',
                'latitude': 34.8783,
                'longitude': -1.3150,
                'working_hours': '08:00 - 18:00',
                'working_days': 'Sunday - Thursday'
            },
            
            # Béjaïa
            {
                'name': 'Stop Desk Béjaïa Centre',
                'wilaya': 'Béjaïa',
                'city': 'Béjaïa',
                'address': 'Boulevard Amirouche, Béjaïa',
                'phone': '+213 34 XX XX XX',
                'latitude': 36.7525,
                'longitude': 5.0689,
                'working_hours': '08:00 - 19:00',
                'working_days': 'Sunday - Thursday'
            },
            
            # Blida
            {
                'name': 'Stop Desk Blida Centre',
                'wilaya': 'Blida',
                'city': 'Blida',
                'address': 'Boulevard Larbi Tebessi, Blida',
                'phone': '+213 25 XX XX XX',
                'latitude': 36.4703,
                'longitude': 2.8277,
                'working_hours': '08:00 - 18:00',
                'working_days': 'Sunday - Thursday'
            },
            
            # Mostaganem
            {
                'name': 'Stop Desk Mostaganem Centre',
                'wilaya': 'Mostaganem',
                'city': 'Mostaganem',
                'address': 'Boulevard de l\'ALN, Mostaganem',
                'phone': '+213 45 XX XX XX',
                'latitude': 35.9310,
                'longitude': 0.0892,
                'working_hours': '08:00 - 18:00',
                'working_days': 'Sunday - Thursday'
            },
            
            # Batna
            {
                'name': 'Stop Desk Batna Centre',
                'wilaya': 'Batna',
                'city': 'Batna',
                'address': 'Avenue de l\'Indépendance, Batna',
                'phone': '+213 33 XX XX XX',
                'latitude': 35.5559,
                'longitude': 6.1742,
                'working_hours': '08:00 - 18:00',
                'working_days': 'Sunday - Thursday'
            },
        ]

        created_count = 0
        updated_count = 0

        for desk_data in stop_desks:
            desk, created = StopDesk.objects.update_or_create(
                name=desk_data['name'],
                wilaya=desk_data['wilaya'],
                defaults=desk_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {desk.name}'))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f'↻ Updated: {desk.name}'))

        self.stdout.write(self.style.SUCCESS(f'\n📍 Total: {created_count} created, {updated_count} updated'))
        self.stdout.write(self.style.SUCCESS('✓ Stop Desks populated successfully!'))
        self.stdout.write(self.style.WARNING('\n⚠️  Note: These are sample locations. Add real Stop Desk addresses in Django Admin.'))