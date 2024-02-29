from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PerformanceAppraisal,TimeEntry
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def create_performance_appraisal(sender, instance, created, **kwargs):
    if created:
        PerformanceAppraisal.objects.create(user=instance)

@receiver(post_save, sender=TimeEntry)
def update_employee_performance(sender, instance, created, **kwargs):
    if instance.approved and instance.user.employee.is_manager:
        employee = instance.user.employee
        performance_rating = employee.calculate_performance_rating()
        performance_comments = employee.calculate_performance_comments()

        # Update the employee's performance appraisal
        performance_appraisal, _ = PerformanceAppraisal.objects.get_or_create(user=employee.user)
        performance_appraisal.average_performance = performance_rating
        performance_appraisal.comments = performance_comments
        performance_appraisal.save()