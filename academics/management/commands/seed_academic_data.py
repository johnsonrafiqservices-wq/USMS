from django.core.management.base import BaseCommand
from academics.models import Programme, Intake, StudyYear, StudySemester, Faculty, Department


class Command(BaseCommand):
    help = 'Seed academic data (programmes, intakes, years, semesters)'

    def handle(self, *args, **options):
        self.stdout.write('Seeding academic data...')

        # Create Faculties
        faculties_data = [
            {'code': 'SCI', 'name': 'Faculty of Science'},
            {'code': 'ENG', 'name': 'Faculty of Engineering'},
            {'code': 'BUS', 'name': 'Faculty of Business'},
            {'code': 'ARTS', 'name': 'Faculty of Arts'},
        ]

        for fac_data in faculties_data:
            Faculty.objects.get_or_create(
                code=fac_data['code'],
                defaults={'name': fac_data['name']}
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(faculties_data)} faculties'))

        # Create Departments
        sci_fac = Faculty.objects.get(code='SCI')
        eng_fac = Faculty.objects.get(code='ENG')
        bus_fac = Faculty.objects.get(code='BUS')

        departments_data = [
            {'code': 'CS', 'name': 'Computer Science', 'faculty': sci_fac},
            {'code': 'IT', 'name': 'Information Technology', 'faculty': sci_fac},
            {'code': 'ENG', 'name': 'Engineering', 'faculty': eng_fac},
            {'code': 'BUS', 'name': 'Business Administration', 'faculty': bus_fac},
            {'code': 'ACC', 'name': 'Accounting', 'faculty': bus_fac},
        ]

        for dept_data in departments_data:
            Department.objects.get_or_create(
                code=dept_data['code'],
                defaults={
                    'name': dept_data['name'],
                    'faculty': dept_data['faculty']
                }
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(departments_data)} departments'))

        # Create Programmes
        cs_dept = Department.objects.get(code='CS')
        it_dept = Department.objects.get(code='IT')
        bus_dept = Department.objects.get(code='BUS')
        eng_dept = Department.objects.get(code='ENG')

        programmes_data = [
            {'code': 'BSC-CS', 'name': 'Bachelor of Science in Computer Science', 'level': 'bachelors', 'duration': 4, 'department': cs_dept},
            {'code': 'BSC-IT', 'name': 'Bachelor of Science in Information Technology', 'level': 'bachelors', 'duration': 4, 'department': it_dept},
            {'code': 'BBA', 'name': 'Bachelor of Business Administration', 'level': 'bachelors', 'duration': 4, 'department': bus_dept},
            {'code': 'BSC-ENG', 'name': 'Bachelor of Science in Engineering', 'level': 'bachelors', 'duration': 5, 'department': eng_dept},
            {'code': 'DIP-CS', 'name': 'Diploma in Computer Science', 'level': 'diploma', 'duration': 2, 'department': cs_dept},
            {'code': 'DIP-BUS', 'name': 'Diploma in Business Studies', 'level': 'diploma', 'duration': 2, 'department': bus_dept},
            {'code': 'MSC-CS', 'name': 'Master of Science in Computer Science', 'level': 'masters', 'duration': 2, 'department': cs_dept},
            {'code': 'MBA', 'name': 'Master of Business Administration', 'level': 'masters', 'duration': 2, 'department': bus_dept},
        ]

        for prog_data in programmes_data:
            Programme.objects.get_or_create(
                code=prog_data['code'],
                defaults={
                    'name': prog_data['name'],
                    'level': prog_data['level'],
                    'duration_years': prog_data['duration'],
                    'department': prog_data['department']
                }
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(programmes_data)} programmes'))

        # Create Intakes
        intakes_data = [
            {'code': 'JAN2024', 'name': 'January 2024 Intake'},
            {'code': 'AUG2024', 'name': 'August 2024 Intake'},
            {'code': 'JAN2025', 'name': 'January 2025 Intake'},
            {'code': 'AUG2025', 'name': 'August 2025 Intake'},
            {'code': 'JAN2026', 'name': 'January 2026 Intake'},
            {'code': 'AUG2026', 'name': 'August 2026 Intake'},
        ]

        for intake_data in intakes_data:
            Intake.objects.get_or_create(
                code=intake_data['code'],
                defaults={'name': intake_data['name']}
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(intakes_data)} intakes'))

        # Create Study Years
        years_data = [
            {'code': 'Y1', 'name': 'Year 1'},
            {'code': 'Y2', 'name': 'Year 2'},
            {'code': 'Y3', 'name': 'Year 3'},
            {'code': 'Y4', 'name': 'Year 4'},
            {'code': 'Y5', 'name': 'Year 5'},
        ]

        for year_data in years_data:
            StudyYear.objects.get_or_create(
                code=year_data['code'],
                defaults={'name': year_data['name']}
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(years_data)} study years'))

        # Create Semesters
        semesters_data = [
            {'code': 'SEM1', 'name': 'Semester 1', 'number': 1},
            {'code': 'SEM2', 'name': 'Semester 2', 'number': 2},
            {'code': 'SEM3', 'name': 'Semester 3', 'number': 3},
            {'code': 'SEM4', 'name': 'Semester 4', 'number': 4},
            {'code': 'SEM5', 'name': 'Semester 5', 'number': 5},
            {'code': 'SEM6', 'name': 'Semester 6', 'number': 6},
        ]

        for sem_data in semesters_data:
            StudySemester.objects.get_or_create(
                code=sem_data['code'],
                defaults={'name': sem_data['name'], 'number': sem_data['number']}
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(semesters_data)} semesters'))
        self.stdout.write(self.style.SUCCESS('Academic data seeded successfully!'))
