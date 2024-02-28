from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Employee,PerformanceAppraisal
from django.contrib.auth.models import User

@receiver(post_save, sender=User)
def create_performance_appraisal(sender, instance, created, **kwargs):
    if created:
        PerformanceAppraisal.objects.create(user=instance)


# Connect the signal handler function to the post_save signal of the User model
post_save.connect(create_performance_appraisal, sender=User)