"""Academic signals — prerequisite enforcement and result auto-calculation."""
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError


@receiver(pre_save, sender='students.Enrollment')
def enforce_prerequisites(sender, instance, **kwargs):
    """Prevent enrollment in a course if student hasn't passed prerequisites."""
    if not instance.pk:  # only on creation
        course = instance.course
        student = instance.student
        prerequisites = course.prerequisites.all()
        if not prerequisites.exists():
            return
        from academics.models import StudentResult
        passed_courses = set(
            StudentResult.objects.filter(
                student=student,
                is_published=True,
                grade_point__gte=1.0,
            ).values_list('course_allocation__course_id', flat=True)
        )
        missing = [p.code for p in prerequisites if p.pk not in passed_courses]
        if missing:
            raise ValidationError(
                f"Cannot enroll in {course.code}: prerequisite(s) not met — {', '.join(missing)}"
            )


@receiver(pre_save, sender='academics.StudentResult')
def auto_calculate_grade(sender, instance, **kwargs):
    """Auto-calculate total_score, grade and grade_point before save."""
    from academics.models import GradeScale
    instance.total_score = instance.ca_score + instance.exam_score
    try:
        scale = GradeScale.objects.get(
            min_score__lte=instance.total_score,
            max_score__gte=instance.total_score,
        )
        instance.grade = scale.grade
        instance.grade_point = scale.grade_point
    except GradeScale.DoesNotExist:
        instance.grade = 'F'
        instance.grade_point = 0


@receiver(pre_save, sender='academics.StudentResult')
def sync_published_flag(sender, instance, **kwargs):
    """Keep is_published in sync with approval_status."""
    from academics.models import StudentResult
    if instance.approval_status == StudentResult.ApprovalStatus.PUBLISHED:
        instance.is_published = True
        if not instance.published_at:
            from django.utils import timezone
            instance.published_at = timezone.now()
    else:
        instance.is_published = False
