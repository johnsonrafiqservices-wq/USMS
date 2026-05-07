from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from students.models import Student
from academics.models import Programme, StudyYear, StudySemester, Intake
from django.utils import timezone
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed 5 sample students'

    def handle(self, *args, **options):
        self.stdout.write('Seeding students...')

        # Get existing academic data
        bsc_cs = Programme.objects.get(code='BSC-CS')
        bsc_it = Programme.objects.get(code='BSC-IT')
        bba = Programme.objects.get(code='BBA')
        
        year1 = StudyYear.objects.get(code='Y1')
        year2 = StudyYear.objects.get(code='Y2')
        year3 = StudyYear.objects.get(code='Y3')
        
        sem1 = StudySemester.objects.get(code='SEM1')
        sem2 = StudySemester.objects.get(code='SEM2')
        
        jan2024 = Intake.objects.get(code='JAN2024')
        aug2024 = Intake.objects.get(code='AUG2024')

        students_data = [
            {
                'student_id': 'STU001',
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'john.doe@ums.edu',
                'programme': bsc_cs,
                'year': year2,
                'semester': sem1,
                'intake': jan2024,
            },
            {
                'student_id': 'STU002',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'email': 'jane.smith@ums.edu',
                'programme': bsc_it,
                'year': year1,
                'semester': sem2,
                'intake': aug2024,
            },
            {
                'student_id': 'STU003',
                'first_name': 'Michael',
                'last_name': 'Johnson',
                'email': 'michael.johnson@ums.edu',
                'programme': bba,
                'year': year3,
                'semester': sem1,
                'intake': jan2024,
            },
            {
                'student_id': 'STU004',
                'first_name': 'Emily',
                'last_name': 'Williams',
                'email': 'emily.williams@ums.edu',
                'programme': bsc_cs,
                'year': year1,
                'semester': sem1,
                'intake': aug2024,
            },
            {
                'student_id': 'STU005',
                'first_name': 'David',
                'last_name': 'Brown',
                'email': 'david.brown@ums.edu',
                'programme': bsc_it,
                'year': year2,
                'semester': sem2,
                'intake': jan2024,
            },
        ]

        for student_data in students_data:
            # Create or get user
            user, created = User.objects.get_or_create(
                email=student_data['email'],
                defaults={
                    'first_name': student_data['first_name'],
                    'last_name': student_data['last_name'],
                    'username': student_data['email'].split('@')[0],
                    'is_active': True,
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                self.stdout.write(f'Created user: {user.email}')
            else:
                self.stdout.write(f'User already exists: {user.email}')

            # Create or get student
            student, created = Student.objects.get_or_create(
                student_id=student_data['student_id'],
                defaults={
                    'user': user,
                    'programme': student_data['programme'],
                    'current_year': student_data['year'],
                    'current_semester_number': student_data['semester'],
                    'intake': student_data['intake'],
                    'status': 'active',
                    'admission_date': timezone.now() - timedelta(days=365),
                    'nationality': 'Ugandan',
                    'state_of_origin': 'Central',
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created student: {student.student_id}'))
            else:
                self.stdout.write(f'Student already exists: {student.student_id}')

        self.stdout.write(self.style.SUCCESS('Students seeded successfully!'))
