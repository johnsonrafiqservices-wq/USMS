from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.utils import timezone
from accounts.decorators import role_required
from .models import Announcement, Message, Notification


@login_required
def announcements(request):
    user = request.user
    announcements_qs = Announcement.objects.filter(is_published=True)

    if user.is_student:
        announcements_qs = announcements_qs.filter(
            target_audience__in=['all', 'students']
        )
    elif user.is_lecturer:
        announcements_qs = announcements_qs.filter(
            target_audience__in=['all', 'staff', 'lecturers']
        )
    else:
        pass  # Admin/staff see all

    return render(request, 'communications/announcements.html', {
        'announcements': announcements_qs,
    })


@login_required
@role_required(['admin', 'registrar', 'lecturer'])
def create_announcement(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        target = request.POST.get('target_audience', 'all')
        priority = request.POST.get('priority', 'normal')

        Announcement.objects.create(
            title=title,
            content=content,
            author=request.user,
            target_audience=target,
            priority=priority,
        )
        django_messages.success(request, 'Announcement published successfully.')
        return redirect('communications:announcements')

    return render(request, 'communications/create_announcement.html')


@login_required
def inbox(request):
    received = Message.objects.filter(recipient=request.user).select_related('sender')
    unread_count = received.filter(is_read=False).count()
    return render(request, 'communications/inbox.html', {
        'messages_list': received,
        'unread_count': unread_count,
    })


@login_required
def sent_messages(request):
    sent = Message.objects.filter(sender=request.user).select_related('recipient')
    return render(request, 'communications/sent.html', {'messages_list': sent})


@login_required
def compose_message(request):
    if request.method == 'POST':
        from accounts.models import User
        recipient_id = request.POST.get('recipient')
        subject = request.POST.get('subject')
        body = request.POST.get('body')

        recipient = get_object_or_404(User, pk=recipient_id)
        Message.objects.create(
            sender=request.user,
            recipient=recipient,
            subject=subject,
            body=body,
        )
        Notification.objects.create(
            user=recipient,
            title='New Message',
            message=f'You have a new message from {request.user.get_full_name()}',
            link='/communications/inbox/',
        )
        django_messages.success(request, 'Message sent successfully.')
        return redirect('communications:inbox')

    from accounts.models import User
    users = User.objects.filter(is_active=True).exclude(id=request.user.id)
    return render(request, 'communications/compose.html', {'users': users})


@login_required
def read_message(request, pk):
    message = get_object_or_404(Message, pk=pk)
    if message.recipient == request.user and not message.is_read:
        message.is_read = True
        message.read_at = timezone.now()
        message.save()
    return render(request, 'communications/read_message.html', {'message': message})


@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(user=request.user)
    unread = notifications.filter(is_read=False)
    if request.method == 'POST':
        unread.update(is_read=True)
        django_messages.success(request, 'All notifications marked as read.')
        return redirect('communications:notifications')
    return render(request, 'communications/notifications.html', {
        'notifications': notifications[:50],
        'unread_count': unread.count(),
    })
