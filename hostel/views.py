from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from accounts.decorators import role_required
from .models import Hostel, Room, RoomAllocation, MaintenanceRequest


@login_required
@role_required(['admin', 'hostel_manager'])
def hostel_dashboard(request):
    hostels = Hostel.objects.filter(is_active=True)
    total_capacity = sum(h.total_capacity for h in hostels)
    total_occupied = sum(h.occupied_beds for h in hostels)
    pending_maintenance = MaintenanceRequest.objects.filter(status='pending').count()
    return render(request, 'hostel/dashboard.html', {
        'hostels': hostels,
        'total_capacity': total_capacity,
        'total_occupied': total_occupied,
        'occupancy_rate': round((total_occupied / total_capacity * 100), 1) if total_capacity > 0 else 0,
        'pending_maintenance': pending_maintenance,
    })


@login_required
@role_required(['admin', 'hostel_manager'])
def hostel_detail(request, pk):
    hostel = get_object_or_404(Hostel, pk=pk)
    rooms = Room.objects.filter(hostel=hostel)
    allocations = RoomAllocation.objects.filter(room__hostel=hostel, is_active=True)
    return render(request, 'hostel/hostel_detail.html', {
        'hostel': hostel,
        'rooms': rooms,
        'allocations': allocations,
    })


@login_required
@role_required(['admin', 'hostel_manager'])
def room_list(request):
    rooms = Room.objects.select_related('hostel').all()
    hostel_filter = request.GET.get('hostel')
    available_only = request.GET.get('available')
    if hostel_filter:
        rooms = rooms.filter(hostel_id=hostel_filter)
    if available_only:
        rooms = rooms.filter(is_available=True, current_occupancy__lt=models.F('capacity'))
    return render(request, 'hostel/room_list.html', {
        'rooms': rooms,
        'hostels': Hostel.objects.all(),
    })


@login_required
@role_required(['admin', 'hostel_manager'])
def allocate_room(request):
    from django.http import JsonResponse
    if request.method == 'POST':
        from students.models import Student
        from academics.models import AcademicSession
        student_id = request.POST.get('student')
        room_id = request.POST.get('room')
        student = get_object_or_404(Student, pk=student_id)
        room = get_object_or_404(Room, pk=room_id)
        session = AcademicSession.objects.filter(is_current=True).first()

        if room.is_full:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Room is at full capacity.'})
            messages.error(request, 'Room is at full capacity.')
            return redirect('hostel:room_list')

        RoomAllocation.objects.create(
            student=student,
            room=room,
            session=session,
            allocated_by=request.user,
        )
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': f'Room {room} allocated to {student}.',
                'redirect': '/hostel/'
            })
        messages.success(request, f'Room {room} allocated to {student}.')
        return redirect('hostel:dashboard')

    from students.models import Student
    students = Student.objects.filter(status='active')
    rooms = Room.objects.filter(is_available=True)

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'hostel/allocate_room_fragment.html', {
            'students': students,
            'rooms': rooms,
        })

    return render(request, 'hostel/allocate_room.html', {
        'students': students,
        'rooms': rooms,
    })


@login_required
@role_required(['admin', 'hostel_manager'])
def maintenance_list(request):
    requests_list = MaintenanceRequest.objects.select_related('room__hostel', 'reported_by').all()
    return render(request, 'hostel/maintenance_list.html', {'requests': requests_list})
