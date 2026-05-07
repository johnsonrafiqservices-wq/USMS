from django.core.management.base import BaseCommand
from finance.models import FeeStructure
from academics.models import Programme, AcademicSession


class Command(BaseCommand):
    help = 'Seed fee structures for different programmes'

    def handle(self, *args, **options):
        self.stdout.write('Seeding fee structures...')

        # Get or create an academic session
        session, created = AcademicSession.objects.get_or_create(
            name='2024-2025',
            defaults={'is_current': True}
        )
        if created:
            self.stdout.write(f'Created session: {session.name}')

        # Get programmes
        programmes = Programme.objects.all()
        
        if not programmes.exists():
            self.stdout.write(self.style.WARNING('No programmes found. Please seed programmes first.'))
            return

        # Fee types and their default amounts
        fee_config = [
            {'type': 'tuition', 'name': 'Tuition Fee', 'amount': 2500000},
            {'type': 'registration', 'name': 'Registration Fee', 'amount': 150000},
            {'type': 'library', 'name': 'Library Fee', 'amount': 100000},
            {'type': 'laboratory', 'name': 'Laboratory Fee', 'amount': 200000},
            {'type': 'ict', 'name': 'ICT Fee', 'amount': 80000},
            {'type': 'medical', 'name': 'Medical Fee', 'amount': 50000},
            {'type': 'examination', 'name': 'Examination Fee', 'amount': 120000},
            {'type': 'development', 'name': 'Development Levy', 'amount': 300000},
        ]

        # Create fee structures for each programme
        for programme in programmes:
            for config in fee_config:
                fee, created = FeeStructure.objects.get_or_create(
                    name=config['name'],
                    fee_type=config['type'],
                    programme=programme,
                    session=session,
                    defaults={
                        'amount': config['amount'],
                        'is_mandatory': True,
                        'description': f'{config["name"]} for {programme.name}',
                    }
                )
                if created:
                    self.stdout.write(f'Created: {fee.name} for {programme.name} - UGX {fee.amount}')

        # Create some general fees (not programme-specific)
        general_fees = [
            {'type': 'accommodation', 'name': 'Hostel Accommodation', 'amount': 800000},
            {'type': 'other', 'name': 'Student ID Card', 'amount': 25000},
        ]

        for config in general_fees:
            fee, created = FeeStructure.objects.get_or_create(
                name=config['name'],
                fee_type=config['type'],
                programme=None,
                session=session,
                defaults={
                    'amount': config['amount'],
                    'is_mandatory': False,
                    'description': f'{config["name"]} (optional)',
                }
            )
            if created:
                self.stdout.write(f'Created: {fee.name} (General) - UGX {fee.amount}')

        self.stdout.write(self.style.SUCCESS('Fee structures seeded successfully!'))
