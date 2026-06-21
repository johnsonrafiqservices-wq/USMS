from django.core.management.base import BaseCommand
from academics.models import (
    Programme,
    Intake,
    StudyYear,
    StudySemester,
    Faculty,
    Department,
    StudyLevel,
    AcademicSession,
    Course,
)


class Command(BaseCommand):
    help = 'Seed academic data (study levels, faculties, departments, programmes, intakes, years, semesters, sessions, and courses)'

    def handle(self, *args, **options):
        self.stdout.write('Seeding academic data...')

        self.create_study_levels()
        self.create_academic_sessions()
        self.create_faculties()
        self.create_departments()
        self.create_programmes()
        self.create_intakes()
        self.create_study_years()
        self.create_study_semesters()
        self.create_courses()

        self.stdout.write(self.style.SUCCESS('Academic data seeded successfully!'))

    def create_study_levels(self):
        levels_data = [
            {'code': 'CERT', 'name': 'Certificate', 'level_number': 1},
            {'code': 'DIP', 'name': 'Diploma', 'level_number': 2},
            {'code': 'BSC', 'name': 'Bachelor', 'level_number': 3},
            {'code': 'MSC', 'name': 'Masters', 'level_number': 4},
        ]

        for level_data in levels_data:
            StudyLevel.objects.get_or_create(
                code=level_data['code'],
                defaults={
                    'name': level_data['name'],
                    'level_number': level_data['level_number'],
                }
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(levels_data)} study levels'))

    def create_academic_sessions(self):
        sessions_data = [
            {'name': '2024/2025', 'is_current': False},
            {'name': '2025/2026', 'is_current': True},
        ]

        for session_data in sessions_data:
            AcademicSession.objects.update_or_create(
                name=session_data['name'],
                defaults={'is_current': session_data['is_current']}
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(sessions_data)} academic sessions'))

    def create_faculties(self):
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

    def create_departments(self):
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
                    'faculty': dept_data['faculty'],
                }
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(departments_data)} departments'))

    def create_programmes(self):
        cs_dept = Department.objects.get(code='CS')
        it_dept = Department.objects.get(code='IT')
        bus_dept = Department.objects.get(code='BUS')
        eng_dept = Department.objects.get(code='ENG')

        bsc_level = StudyLevel.objects.get(code='BSC')
        dip_level = StudyLevel.objects.get(code='DIP')
        msc_level = StudyLevel.objects.get(code='MSC')

        programmes_data = [
            {
                'code': 'BSC-CS',
                'name': 'Bachelor of Science in Computer Science',
                'level': bsc_level,
                'duration_years': 4,
                'department': cs_dept,
            },
            {
                'code': 'BSC-IT',
                'name': 'Bachelor of Science in Information Technology',
                'level': bsc_level,
                'duration_years': 4,
                'department': it_dept,
            },
            {
                'code': 'BBA',
                'name': 'Bachelor of Business Administration',
                'level': bsc_level,
                'duration_years': 4,
                'department': bus_dept,
            },
            {
                'code': 'BSC-ENG',
                'name': 'Bachelor of Science in Engineering',
                'level': bsc_level,
                'duration_years': 5,
                'department': eng_dept,
            },
            {
                'code': 'DIP-CS',
                'name': 'Diploma in Computer Science',
                'level': dip_level,
                'duration_years': 2,
                'department': cs_dept,
            },
            {
                'code': 'DIP-BUS',
                'name': 'Diploma in Business Studies',
                'level': dip_level,
                'duration_years': 2,
                'department': bus_dept,
            },
            {
                'code': 'MSC-CS',
                'name': 'Master of Science in Computer Science',
                'level': msc_level,
                'duration_years': 2,
                'department': cs_dept,
            },
            {
                'code': 'MBA',
                'name': 'Master of Business Administration',
                'level': msc_level,
                'duration_years': 2,
                'department': bus_dept,
            },
        ]

        for prog_data in programmes_data:
            Programme.objects.get_or_create(
                code=prog_data['code'],
                defaults={
                    'name': prog_data['name'],
                    'level': prog_data['level'],
                    'duration_years': prog_data['duration_years'],
                    'department': prog_data['department'],
                }
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(programmes_data)} programmes'))

    def create_intakes(self):
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

    def create_study_years(self):
        years_data = [
            {'code': 'Y1', 'name': 'Year 1', 'level': 1},
            {'code': 'Y2', 'name': 'Year 2', 'level': 2},
            {'code': 'Y3', 'name': 'Year 3', 'level': 3},
            {'code': 'Y4', 'name': 'Year 4', 'level': 4},
            {'code': 'Y5', 'name': 'Year 5', 'level': 5},
        ]

        for year_data in years_data:
            StudyYear.objects.get_or_create(
                code=year_data['code'],
                defaults={'name': year_data['name'], 'level': year_data['level']}
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(years_data)} study years'))

    def create_study_semesters(self):
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

    def create_courses(self):
        cs_dept = Department.objects.get(code='CS')
        it_dept = Department.objects.get(code='IT')
        eng_dept = Department.objects.get(code='ENG')
        bus_dept = Department.objects.get(code='BUS')

        bsc_cs = Programme.objects.get(code='BSC-CS')
        bsc_it = Programme.objects.get(code='BSC-IT')
        bba = Programme.objects.get(code='BBA')
        bsc_eng = Programme.objects.get(code='BSC-ENG')
        dip_cs = Programme.objects.get(code='DIP-CS')
        dip_bus = Programme.objects.get(code='DIP-BUS')
        msc_cs = Programme.objects.get(code='MSC-CS')
        mba = Programme.objects.get(code='MBA')

        sem1 = StudySemester.objects.get(code='SEM1')
        sem2 = StudySemester.objects.get(code='SEM2')

        courses_data = [
            {'code': 'CS101', 'title': 'Introduction to Programming', 'department': cs_dept, 'programmes': [bsc_cs, dip_cs, msc_cs], 'credit_units': 3, 'course_type': 'core', 'level': 100, 'semester': sem1},
            {'code': 'CS102', 'title': 'Discrete Mathematics', 'department': cs_dept, 'programmes': [bsc_cs, dip_cs], 'credit_units': 3, 'course_type': 'core', 'level': 100, 'semester': sem2},
            {'code': 'CS201', 'title': 'Data Structures and Algorithms', 'department': cs_dept, 'programmes': [bsc_cs, msc_cs], 'credit_units': 4, 'course_type': 'core', 'level': 200, 'semester': sem1},
            {'code': 'CS202', 'title': 'Database Systems', 'department': cs_dept, 'programmes': [bsc_cs, dip_cs, msc_cs], 'credit_units': 3, 'course_type': 'core', 'level': 200, 'semester': sem2},
            {'code': 'CS301', 'title': 'Operating Systems', 'department': cs_dept, 'programmes': [bsc_cs, msc_cs], 'credit_units': 4, 'course_type': 'core', 'level': 300, 'semester': sem1},
            {'code': 'CS302', 'title': 'Software Engineering', 'department': cs_dept, 'programmes': [bsc_cs, msc_cs], 'credit_units': 3, 'course_type': 'core', 'level': 300, 'semester': sem2},
            {'code': 'IT101', 'title': 'Information Systems Fundamentals', 'department': it_dept, 'programmes': [bsc_it], 'credit_units': 3, 'course_type': 'core', 'level': 100, 'semester': sem1},
            {'code': 'IT102', 'title': 'Computer Networking', 'department': it_dept, 'programmes': [bsc_it], 'credit_units': 3, 'course_type': 'core', 'level': 100, 'semester': sem2},
            {'code': 'IT201', 'title': 'Web Development', 'department': it_dept, 'programmes': [bsc_it], 'credit_units': 3, 'course_type': 'core', 'level': 200, 'semester': sem1},
            {'code': 'IT202', 'title': 'Systems Analysis and Design', 'department': it_dept, 'programmes': [bsc_it], 'credit_units': 3, 'course_type': 'core', 'level': 200, 'semester': sem2},
            {'code': 'ENG101', 'title': 'Engineering Mathematics', 'department': eng_dept, 'programmes': [bsc_eng], 'credit_units': 4, 'course_type': 'core', 'level': 100, 'semester': sem1},
            {'code': 'ENG102', 'title': 'Engineering Mechanics', 'department': eng_dept, 'programmes': [bsc_eng], 'credit_units': 4, 'course_type': 'core', 'level': 100, 'semester': sem2},
            {'code': 'ENG201', 'title': 'Thermodynamics', 'department': eng_dept, 'programmes': [bsc_eng], 'credit_units': 4, 'course_type': 'core', 'level': 200, 'semester': sem1},
            {'code': 'ENG202', 'title': 'Fluid Mechanics', 'department': eng_dept, 'programmes': [bsc_eng], 'credit_units': 4, 'course_type': 'core', 'level': 200, 'semester': sem2},
            {'code': 'BA101', 'title': 'Principles of Management', 'department': bus_dept, 'programmes': [bba, dip_bus, mba], 'credit_units': 3, 'course_type': 'core', 'level': 100, 'semester': sem1},
            {'code': 'BA102', 'title': 'Financial Accounting', 'department': bus_dept, 'programmes': [bba, dip_bus, mba], 'credit_units': 3, 'course_type': 'core', 'level': 100, 'semester': sem2},
            {'code': 'BA201', 'title': 'Marketing Management', 'department': bus_dept, 'programmes': [bba, mba], 'credit_units': 3, 'course_type': 'core', 'level': 200, 'semester': sem1},
            {'code': 'BA202', 'title': 'Organizational Behaviour', 'department': bus_dept, 'programmes': [bba, mba], 'credit_units': 3, 'course_type': 'core', 'level': 200, 'semester': sem2},
            {'code': 'AC101', 'title': 'Introductory Accounting', 'department': bus_dept, 'programmes': [dip_bus], 'credit_units': 3, 'course_type': 'core', 'level': 100, 'semester': sem1},
            {'code': 'AC102', 'title': 'Business Finance', 'department': bus_dept, 'programmes': [dip_bus], 'credit_units': 3, 'course_type': 'core', 'level': 100, 'semester': sem2},
            {'code': 'MS101', 'title': 'Advanced Data Analytics', 'department': cs_dept, 'programmes': [msc_cs, mba], 'credit_units': 3, 'course_type': 'core', 'level': 500, 'semester': sem1},
            {'code': 'MS102', 'title': 'Machine Learning', 'department': cs_dept, 'programmes': [msc_cs], 'credit_units': 3, 'course_type': 'core', 'level': 500, 'semester': sem2},
            {'code': 'MB101', 'title': 'Business Strategy', 'department': bus_dept, 'programmes': [mba], 'credit_units': 3, 'course_type': 'core', 'level': 500, 'semester': sem1},
            {'code': 'MB102', 'title': 'Leadership and Change', 'department': bus_dept, 'programmes': [mba], 'credit_units': 3, 'course_type': 'core', 'level': 500, 'semester': sem2},
        ]

        created = 0
        for course_data in courses_data:
            course, _ = Course.objects.get_or_create(
                code=course_data['code'],
                defaults={
                    'title': course_data['title'],
                    'department': course_data['department'],
                    'credit_units': course_data['credit_units'],
                    'course_type': course_data['course_type'],
                    'level': course_data['level'],
                    'semester': course_data['semester'],
                    'description': '',
                    'max_students': 200,
                }
            )
            course.programme.set(course_data['programmes'])
            created += 1

        self.stdout.write(self.style.SUCCESS(f'Created or updated {created} courses'))
