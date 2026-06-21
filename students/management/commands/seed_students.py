import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from academics.models import Programme, StudyYear, StudySemester, Intake
from students.models import Student

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed 300 sample students with user accounts'

    def handle(self, *args, **options):
        self.stdout.write('Seeding 300 students...')

        programmes = list(Programme.objects.filter(code__in=[
            'BSC-CS', 'BSC-IT', 'BBA', 'BSC-ENG',
            'DIP-CS', 'DIP-BUS', 'MSC-CS', 'MBA'
        ]).order_by('code'))
        years = list(StudyYear.objects.order_by('level'))
        semesters = list(StudySemester.objects.order_by('number'))
        intakes = list(Intake.objects.order_by('code'))

        if not programmes or not years or not semesters or not intakes:
            self.stdout.write(self.style.ERROR(
                'Academic data is missing. Run seed_academic_data first.'
            ))
            return

        first_names = [
            'Alex', 'Brian', 'Clara', 'Diana', 'Edward', 'Faith', 'George', 'Hannah',
            'Ibrahim', 'Joy', 'Kevin', 'Lydia', 'Michael', 'Nadia', 'Oscar', 'Patience',
            'Queen', 'Richard', 'Susan', 'Thomas', 'Umar', 'Victoria', 'William', 'Yasmine',
            'Zainab', 'Aaron', 'Bella', 'Charles', 'Dorothy', 'Elias',
        ]
        last_names = [
            'Akello', 'Baluku', 'Carter', 'Ddamulira', 'Ekwaro', 'Francis', 'Gonzalez',
            'Hassan', 'Ibrahim', 'Jackson', 'Kato', 'Lule', 'Mugisha', 'Nansubuga',
            'Okello', 'Patterson', 'Quinto', 'Rwabwogo', 'Ssemanda', 'Tumusiime',
            'Umaru', 'Vanguard', 'Waiswa', 'Yiga', 'Zziwa',
        ]
        nationality_choices = ['Ugandan', 'Kenyan', 'Tanzanian', 'Rwandan', 'South Sudanese']
        state_choices = ['Central', 'Eastern', 'Northern', 'Western']

        random.seed(42)
        created_count = 0

        for idx in range(1, 301):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f'student{idx:03}@ums.edu'
            username = f'student{idx:03}'
            student_id = f'STU{idx:03}'

            user, user_created = User.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'username': username,
                    'is_active': True,
                    'role': User.Role.STUDENT if hasattr(User, 'Role') else 'student',
                }
            )
            if user_created:
                user.set_password('Password123!')
                user.save()

            programme = programmes[(idx - 1) % len(programmes)]
            year = years[(idx - 1) % len(years)]
            semester = semesters[(idx - 1) % len(semesters)]
            intake = intakes[(idx - 1) % len(intakes)]

            admission_date = timezone.now() - timedelta(days=120 + (idx % 900))
            student_defaults = {
                'user': user,
                'programme': programme,
                'current_year': year,
                'current_semester_number': semester,
                'intake': intake,
                'status': Student.Status.ACTIVE,
                'admission_date': admission_date,
                'nationality': random.choice(nationality_choices),
                'state_of_origin': random.choice(state_choices),
            }

            student, student_created = Student.objects.get_or_create(
                student_id=student_id,
                defaults=student_defaults
            )

            if student_created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Created {created_count} students'))
        self.stdout.write(self.style.SUCCESS('Students seeded successfully!'))
