from django.contrib.auth.models import User
from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=255,unique=True)

    def __str__(self):
        return self.name

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    contact_number = models.CharField(max_length=50)
    national_ID = models.CharField(unique=True, max_length=50)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    position = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    date_of_birth = models.DateField()
    joined_date = models.DateField()
    salary = models.DecimalField(max_digits=10, decimal_places=2 ,default=0.0)
    is_manager = models.BooleanField(default=False)
    medical_conditions = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_number = models.CharField(max_length=50, blank=True)

    
    
    class Meta:
        verbose_name = 'Employee Profile'
    
    def __str__(self):
        return self.user.username


class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    wage_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    tax_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    assign_to = models.ManyToManyField(User, related_name='tasks_assigned')
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class TimeEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    approved = models.BooleanField(default=False)
    notes = models.TextField()

    class Meta:
        verbose_name = "timesheet"

    def __str__(self):
        return self.user.username
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.task.status:
            entry_times_count = TimeEntry.objects.filter(task=self.task, user__in=self.task.assign_to.all()).count()

            if entry_times_count > 0:
                self.task.status = True
                self.task.save()


class PerformanceAppraisal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    average_performance = models.FloatField(default=0.0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2 ,default=0.0)
    comments = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.user.username
    
    class Meta:
        verbose_name = "KPI"
