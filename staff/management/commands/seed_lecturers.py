import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from academics.models import Department, StudySemester, Course, CourseAllocation
from staff.models import StaffProfile

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed lecturer user accounts, staff profiles, and course allocations.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding lecturers and course assignments...')

        departments = {dept.code: dept for dept in Department.objects.all()}
        semester1 = StudySemester.objects.filter(number=1).first()
        semester2 = StudySemester.objects.filter(number=2).first()

        if not departments:
            self.stdout.write(self.style.ERROR('No departments found. Run academic seed data first.'))
            return

        if not semester1 or not semester2:
            self.stdout.write(self.style.ERROR('Study semesters missing. Run academic seed data first.'))
            return

        lecturer_data = [
            {
                'first_name': 'Alice',
                'last_name': 'Mwangi',
                'email': 'alice.mwangi@ums.edu',
                'username': 'alice.mwangi',
                'staff_id': 'LEC001',
                'department_code': 'CS',
                'rank': 'senior_lecturer',
                'qualification': 'PhD Computer Science',
                'specialization': 'Software Engineering',
            },
            {
                'first_name': 'Benjamin',
                'last_name': 'Otieno',
                'email': 'benjamin.otieno@ums.edu',
                'username': 'benjamin.otieno',
                'staff_id': 'LEC002',
                'department_code': 'IT',
                'rank': 'lecturer_i',
                'qualification': 'MSc Information Technology',
                'specialization': 'Networks and Security',
            },
            {
                'first_name': 'Charles',
                'last_name': 'Nsubuga',
                'email': 'charles.nsubuga@ums.edu',
                'username': 'charles.nsubuga',
                'staff_id': 'LEC003',
                'department_code': 'ENG',
                'rank': 'professor',
                'qualification': 'PhD Mechanical Engineering',
                'specialization': 'Thermodynamics',
            },
            {
                'first_name': 'Diana',
                'last_name': 'Kato',
                'email': 'diana.kato@ums.edu',
                'username': 'diana.kato',
                'staff_id': 'LEC004',
                'department_code': 'BUS',
                'rank': 'senior_lecturer',
                'qualification': 'MBA',
                'specialization': 'Strategic Management',
            },
            {
                'first_name': 'Edward',
                'last_name': 'Ssemanda',
                'email': 'edward.ssemanda@ums.edu',
                'username': 'edward.ssemanda',
                'staff_id': 'LEC005',
                'department_code': 'CS',
                'rank': 'assistant_lecturer',
                'qualification': 'MSc Computer Science',
                'specialization': 'Data Structures',
            },
            {
                'first_name': 'Faith',
                'last_name': 'Lule',
                'email': 'faith.lule@ums.edu',
                'username': 'faith.lule',
                'staff_id': 'LEC006',
                'department_code': 'IT',
                'rank': 'lecturer_ii',
                'qualification': 'PhD Information Systems',
                'specialization': 'Web Development',
            },
            {
                'first_name': 'George',
                'last_name': 'Kyeyune',
                'email': 'george.kyeyune@ums.edu',
                'username': 'george.kyeyune',
                'staff_id': 'LEC007',
                'department_code': 'ENG',
                'rank': 'lecturer_i',
                'qualification': 'MSc Civil Engineering',
                'specialization': 'Structural Analysis',
            },
            {
                'first_name': 'Hannah',
                'last_name': 'Kaggwa',
                'email': 'hannah.kaggwa@ums.edu',
                'username': 'hannah.kaggwa',
                'staff_id': 'LEC008',
                'department_code': 'BUS',
                'rank': 'assistant_lecturer',
                'qualification': 'MBA',
                'specialization': 'Accounting',
            },
            {
                'first_name': 'Ibrahim',
                'last_name': 'Mutebi',
                'email': 'ibrahim.mutebi@ums.edu',
                'username': 'ibrahim.mutebi',
                'staff_id': 'LEC009',
                'department_code': 'CS',
                'rank': 'lecturer_ii',
                'qualification': 'PhD Artificial Intelligence',
                'specialization': 'Machine Learning',
            },
            {
                'first_name': 'Joyce',
                'last_name': 'Nansubuga',
                'email': 'joyce.nansubuga@ums.edu',
                'username': 'joyce.nansubuga',
                'staff_id': 'LEC010',
                'department_code': 'BUS',
                'rank': 'senior_lecturer',
                'qualification': 'PhD Finance',
                'specialization': 'Financial Accounting',
            },
        ]

        created_lecturers = 0
        created_allocations = 0

        for lecturer in lecturer_data:
            department = departments.get(lecturer['department_code'])
            if not department:
                self.stdout.write(self.style.WARNING(
                    f"Skipped lecturer {lecturer['first_name']} {lecturer['last_name']} because department {lecturer['department_code']} was not found."
                ))
                continue

            user, user_created = User.objects.get_or_create(
                email=lecturer['email'],
                defaults={
                    'username': lecturer['username'],
                    'first_name': lecturer['first_name'],
                    'last_name': lecturer['last_name'],
                    'is_active': True,
                    'role': User.Role.LECTURER if hasattr(User, 'Role') else 'lecturer',
                }
            )

            if user_created:
                user.set_password('Password123!')
                user.save()

            profile, profile_created = StaffProfile.objects.get_or_create(
                user=user,
                defaults={
                    'staff_id': lecturer['staff_id'],
                    'department': department,
                    'staff_type': StaffProfile.StaffType.ACADEMIC,
                    'rank': lecturer['rank'],
                    'qualification': lecturer['qualification'],
                    'specialization': lecturer['specialization'],
                }
            )

            if user_created or profile_created:
                created_lecturers += 1

            department_courses = Course.objects.filter(department=department, is_active=True).order_by('code')
            allocation_count = 0
            for course in department_courses[:3]:
                semester = course.semester or semester1
                allocation, allocation_created = CourseAllocation.objects.get_or_create(
                    course=course,
                    lecturer=profile,
                    semester=semester,
                )
                if allocation_created:
                    created_allocations += 1
                allocation_count += 1

            if allocation_count == 0:
                self.stdout.write(self.style.WARNING(
                    f"Lecturer {user.get_full_name()} has no department courses available to allocate."
                ))

        self.stdout.write(self.style.SUCCESS(
            f'Created or updated {created_lecturers} lecturer users and profiles.'
        ))
        self.stdout.write(self.style.SUCCESS(
            f'Created {created_allocations} course allocations for lecturers.'
        ))
        self.stdout.write(self.style.SUCCESS('Lecturer seeding complete.'))
