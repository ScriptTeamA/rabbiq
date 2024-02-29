from django.utils import timezone
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

    DECAY_FACTOR = 0.95

    def calculate_performance_rating(self,user):
        total_hours = 0
        total_rating = 0

        time_entries = TimeEntry.objects.filter(user=user).order_by('-end_time')
        if time_entries.exists():
            last_activity_time = time_entries.first().end_time
            days_since_last_activity = (timezone.now() - last_activity_time).days
        else:
            days_since_last_activity = None

        for entry in time_entries:
            hours_worked = (entry.end_time - entry.start_time).total_seconds() / 3600
            total_hours += hours_worked
            total_rating += float(entry.task.wage_per_hour) * hours_worked

        if total_hours > 0:
            average_performance = total_rating / total_hours
        else:
            average_performance = 0

        # Apply time decay to the rating based on days since last activity
        if days_since_last_activity is not None:
            decay_factor = self.DECAY_FACTOR ** days_since_last_activity
            average_performance *= decay_factor

        # Limit the rating to a maximum of 100
        average_performance = min(average_performance, 100)

        return average_performance

    def calculate_performance_comments(self,user):
        average_performance = self.calculate_performance_rating(user)
        comments = ''

        if average_performance >= 80:
            comments = 'Great job! You are performing excellently.'
        elif average_performance >= 60:
            comments = 'Good job! Keep up the good work.'
        else:
            comments = 'You can improve your performance.'

        return comments
    
    class Meta:
        verbose_name = 'Employee Profile'
    
    def __str__(self):
        return self.user.first_name + '-' + self.user.last_name


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
    comments = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.user.username
    
    class Meta:
        verbose_name = "KPI"
