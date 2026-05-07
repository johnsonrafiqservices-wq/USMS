from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import role_required
from .models import StaffProfile, StaffPerformance


@login_required
@role_required(['admin', 'registrar'])
def staff_list(request):
    staff = StaffProfile.objects.select_related('user', 'department').all()
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
