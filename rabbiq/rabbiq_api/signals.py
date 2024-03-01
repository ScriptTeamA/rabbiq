from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PerformanceAppraisal,TimeEntry,Employee
from django.contrib.auth.models import User
from .utilis import KPI

@receiver(post_save, sender=User)
def create_performance_appraisal(sender, instance, created, **kwargs):
    if created:
        PerformanceAppraisal.objects.create(user=instance)

@receiver(post_save, sender=TimeEntry)
def update_employee_performance(sender, instance, created, **kwargs):
    if instance.approved:
        try:
            kpi = KPI()
            performance_rating = kpi.calculate_performance_rating(user=instance.user)
            performance_comments = kpi.calculate_performance_comments(user=instance.user)

            # Update the employee's performance appraisal
            performance_appraisal, _ = PerformanceAppraisal.objects.get_or_create(user=instance.user)
            performance_appraisal.average_performance = performance_rating
            performance_appraisal.comments = performance_comments
            performance_appraisal.save()
        except:
            aprroved = instance
            aprroved.approved = False
            aprroved.save()

        