from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from .models import StaffProfile, StaffPerformance
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .forms import StaffCreateForm
from django.template.loader import render_to_string

User = get_user_model()


@login_required
@role_required(['admin', 'registrar'])
def staff_list(request):
    staff = StaffProfile.objects.select_related('user', 'department').all()
    if request.user.is_department_head:
        from academics.models import Department
        dept = Department.objects.filter(head_of_department=request.user).first()
        staff = staff.filter(department=dept) if dept else staff.none()
    dept_filter = request.GET.get('department')
    type_filter = request.GET.get('staff_type')
    if dept_filter:
        staff = staff.filter(department_id=dept_filter)
    if type_filter:
        staff = staff.filter(staff_type=type_filter)
    from academics.models import Department
    departments = Department.objects.all()
    return render(request, 'staff/staff_list.html', {
        'staff_members': staff,
        'departments': departments,
        'staff_types': StaffProfile.StaffType.choices,
    })


@login_required
def staff_detail(request, pk):
    staff_member = get_object_or_404(StaffProfile.objects.select_related('user', 'department'), pk=pk)
    if request.user.is_department_head:
        from academics.models import Department
        dept = Department.objects.filter(head_of_department=request.user).first()
        if not dept or staff_member.department != dept:
            messages.error(request, 'You do not have permission to view this staff member.')
            return redirect('accounts:dashboard')
    from academics.models import CourseAllocation
    allocations = CourseAllocation.objects.filter(
        lecturer=staff_member
    ).select_related('course', 'semester')[:10]
    performances = StaffPerformance.objects.filter(staff=staff_member)[:5]
    return render(request, 'staff/staff_detail.html', {
        'staff_member': staff_member,
        'allocations': allocations,
        'performances': performances,
    })


@login_required
def my_courses(request):
    """Lecturer's allocated courses."""
    try:
        staff = StaffProfile.objects.get(user=request.user)
        from academics.models import CourseAllocation
        allocations = CourseAllocation.objects.filter(
            lecturer=staff, is_active=True
        ).select_related('course', 'semester')
        current_allocations = allocations
    except StaffProfile.DoesNotExist:
        staff = None
        allocations = []
        current_allocations = []

    return render(request, 'staff/my_courses.html', {
        'staff': staff,
        'allocations': allocations,
        'current_allocations': current_allocations,
    })


@login_required
@role_required(['admin'])
def workload_overview(request):
    """Overview of staff workload distribution."""
    staff_members = StaffProfile.objects.filter(
        staff_type='academic', is_active=True
    ).select_related('user', 'department')
    return render(request, 'staff/workload_overview.html', {
        'staff_members': staff_members,
    })


@login_required
@role_required(['admin', 'registrar'])
def staff_create_ajax(request):
    if request.method == 'POST':
        form = StaffCreateForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # create user with unusable password
            user = User.objects.create(
                username=data['username'],
                email=data.get('email') or '',
                first_name=data['first_name'],
                last_name=data['last_name'],
                role='lecturer'
            )
            user.set_unusable_password()
            user.save()

            staff = StaffProfile.objects.create(
                user=user,
                staff_id=data['staff_id'],
                department=data.get('department'),
                staff_type=data.get('staff_type', 'academic')
            )

            return JsonResponse({'success': True, 'staff_id': staff.pk, 'display': str(staff)})
        return JsonResponse({'success': False, 'errors': form.errors})

    # GET - return fragment
    form = StaffCreateForm()
    html = render_to_string('staff/staff_create_fragment.html', {'form': form}, request=request)
    return JsonResponse({'success': True, 'html': html})
