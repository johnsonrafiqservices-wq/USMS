from django.core.management.base import BaseCommand
from finance.models import FeeStructure
from academics.models import Programme, AcademicSession


class Command(BaseCommand):
    help = 'Seed fee structures for different programmes and university fees'

    def handle(self, *args, **options):
        self.stdout.write('Seeding fee structures...')

        session = AcademicSession.objects.filter(is_current=True).first()
        if not session:
            session, created = AcademicSession.objects.get_or_create(
                name='2025/2026',
                defaults={'is_current': True}
            )
            if created:
                self.stdout.write(f'Created session: {session.name}')

        programmes = {programme.code: programme for programme in Programme.objects.all()}
        if not programmes:
            self.stdout.write(self.style.WARNING('No programmes found. Please seed programmes first.'))
            return

        programme_fees = [
            {
                'name': 'BSC-CS Tuition Fee',
                'fee_type': 'tuition',
                'amount': 2800000,
                'frequency': 'per_semester',
                'is_mandatory': True,
                'programme_codes': ['BSC-CS'],
                'description': 'Tuition fee for Bachelor of Science in Computer Science',
            },
            {
                'name': 'BSC-IT Tuition Fee',
                'fee_type': 'tuition',
                'amount': 2600000,
                'frequency': 'per_semester',
                'is_mandatory': True,
                'programme_codes': ['BSC-IT'],
                'description': 'Tuition fee for Bachelor of Science in Information Technology',
            },
            {
                'name': 'BBA Tuition Fee',
                'fee_type': 'tuition',
                'amount': 2400000,
                'frequency': 'per_semester',
                'is_mandatory': True,
                'programme_codes': ['BBA'],
                'description': 'Tuition fee for Bachelor of Business Administration',
            },
            {
                'name': 'BSC-ENG Tuition Fee',
                'fee_type': 'tuition',
                'amount': 3000000,
                'frequency': 'per_semester',
                'is_mandatory': True,
                'programme_codes': ['BSC-ENG'],
                'description': 'Tuition fee for Bachelor of Science in Engineering',
            },
            {
                'name': 'DIP-CS Tuition Fee',
                'fee_type': 'tuition',
                'amount': 1700000,
                'frequency': 'per_semester',
                'is_mandatory': True,
                'programme_codes': ['DIP-CS'],
                'description': 'Tuition fee for Diploma in Computer Science',
            },
            {
                'name': 'DIP-BUS Tuition Fee',
                'fee_type': 'tuition',
                'amount': 1600000,
                'frequency': 'per_semester',
                'is_mandatory': True,
                'programme_codes': ['DIP-BUS'],
                'description': 'Tuition fee for Diploma in Business Studies',
            },
            {
                'name': 'MSC-CS Tuition Fee',
                'fee_type': 'tuition',
                'amount': 3600000,
                'frequency': 'per_semester',
                'is_mandatory': True,
                'programme_codes': ['MSC-CS'],
                'description': 'Tuition fee for Master of Science in Computer Science',
            },
            {
                'name': 'MBA Tuition Fee',
                'fee_type': 'tuition',
                'amount': 3500000,
                'frequency': 'per_semester',
                'is_mandatory': True,
                'programme_codes': ['MBA'],
                'description': 'Tuition fee for Master of Business Administration',
            },
            {
                'name': 'General Registration Fee',
                'fee_type': 'registration',
                'amount': 180000,
                'frequency': 'per_year',
                'is_mandatory': True,
                'programme_codes': list(programmes.keys()),
                'description': 'Mandatory registration fee for all programmes',
            },
            {
                'name': 'Library Access Fee',
                'fee_type': 'library',
                'amount': 100000,
                'frequency': 'per_semester',
                'is_mandatory': True,
                'programme_codes': list(programmes.keys()),
                'description': 'Library access and resource maintenance fee',
            },
            {
                'name': 'Science & Engineering Laboratory Fee',
                'fee_type': 'laboratory',
                'amount': 330000,
                'frequency': 'per_semester',
                'is_mandatory': True,
                'programme_codes': ['BSC-CS', 'BSC-IT', 'BSC-ENG', 'MSC-CS'],
                'description': 'Laboratory support fee for science, technology and engineering programmes',
            },
            {
                'name': 'ICT Fee',
                'fee_type': 'ict',
                'amount': 90000,
                'frequency': 'per_semester',
                'is_mandatory': True,
                'programme_codes': list(programmes.keys()),
                'description': 'ICT infrastructure and online learning support fee',
            },
            {
                'name': 'Medical Insurance Fee',
                'fee_type': 'insurance',
                'amount': 90000,
                'frequency': 'per_year',
                'is_mandatory': True,
                'programme_codes': list(programmes.keys()),
                'description': 'Campus medical and health insurance premium',
            },
            {
                'name': 'Examination Fee',
                'fee_type': 'examination',
                'amount': 120000,
                'frequency': 'per_semester',
                'is_mandatory': True,
                'programme_codes': list(programmes.keys()),
                'description': 'Examination administration and grading fee',
            },
            {
                'name': 'Development Levy',
                'fee_type': 'development',
                'amount': 320000,
                'frequency': 'per_semester',
                'is_mandatory': True,
                'programme_codes': list(programmes.keys()),
                'description': 'Campus development levy for facilities and infrastructure',
            },
            {
                'name': 'Student Union Fee',
                'fee_type': 'union',
                'amount': 25000,
                'frequency': 'per_year',
                'is_mandatory': False,
                'programme_codes': list(programmes.keys()),
                'description': 'Optional student union and clubs support fee',
            },
            {
                'name': 'Orientation Fee',
                'fee_type': 'orientation',
                'amount': 75000,
                'frequency': 'once',
                'is_mandatory': True,
                'programme_codes': list(programmes.keys()),
                'description': 'Orientation and welcome activities fee',
            },
            {
                'name': 'Campus Security Levy',
                'fee_type': 'security',
                'amount': 65000,
                'frequency': 'per_semester',
                'is_mandatory': True,
                'programme_codes': list(programmes.keys()),
                'description': 'Campus security and safety service charge',
            },
            {
                'name': 'Internet Access Fee',
                'fee_type': 'internet',
                'amount': 50000,
                'frequency': 'per_semester',
                'is_mandatory': True,
                'programme_codes': list(programmes.keys()),
                'description': 'Student internet access and network support fee',
            },
            {
                'name': 'Graduation Fee',
                'fee_type': 'graduation',
                'amount': 125000,
                'frequency': 'graduation',
                'is_mandatory': False,
                'programme_codes': list(programmes.keys()),
                'description': 'Final graduation clearance and ceremony fee',
            },
            {
                'name': 'Transcript Fee',
                'fee_type': 'transcript',
                'amount': 45000,
                'frequency': 'once',
                'is_mandatory': False,
                'programme_codes': list(programmes.keys()),
                'description': 'Transcript issuance and mailing fee',
            },
            {
                'name': 'Research/Thesis Supervision Fee',
                'fee_type': 'research',
                'amount': 220000,
                'frequency': 'per_year',
                'is_mandatory': True,
                'programme_codes': ['MSC-CS', 'MBA'],
                'description': 'Research supervision and thesis support fee for graduate programmes',
            },
        ]

        seed_count = 0
        for fee_data in programme_fees:
            fee, created = FeeStructure.objects.update_or_create(
                name=fee_data['name'],
                fee_type=fee_data['fee_type'],
                session=session,
                defaults={
                    'amount': fee_data['amount'],
                    'frequency': fee_data['frequency'],
                    'is_mandatory': fee_data['is_mandatory'],
                    'description': fee_data['description'],
                }
            )
            fee_programmes = [programmes[code] for code in fee_data['programme_codes'] if code in programmes]
            fee.programmes.set(fee_programmes)
            fee.save()
            if created:
                self.stdout.write(f'Created fee: {fee.name} - UGX {fee.amount}')
            else:
                self.stdout.write(f'Updated fee: {fee.name} - UGX {fee.amount}')
            seed_count += 1

        self.stdout.write(self.style.SUCCESS(f'Seeded {seed_count} fee structures successfully!'))
