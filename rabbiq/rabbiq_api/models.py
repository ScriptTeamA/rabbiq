from django.db import models
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin, Group
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission

class UserManager(BaseUserManager):
    def create_user(self, email, phone_number, national_ID, first_name='', last_name='', password=None):
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            phone_number=phone_number,
            national_ID=national_ID,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, phone_number, national_ID, first_name='', last_name='', password=None):
        user = self.create_user(
            email=email,
            phone_number=phone_number,
            national_ID=national_ID,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save(using=self._db)
        
        # Assign all available permissions to the superuser
        permissions = Permission.objects.all()
        user.user_permissions.set(permissions)
        
        return user
    
    def add_user_to_group(self, user, group_name):
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=254)
    phone_number = models.CharField(max_length=50)
    national_ID = models.CharField(unique=True, max_length=50)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [
        'phone_number',
        'national_ID',
    ]

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        if not self.pk:
            # New instance, set_password will hash the password
            self.set_password(self.password)
        return super().save(*args, **kwargs)
    class Meta:
        verbose_name = 'Employee'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/')
    occupation = models.CharField(max_length=50, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    DECAY_FACTOR = 0.95

    def calculate_performance_rating(self):
        total_hours = 0
        total_rating = 0

        time_entries = TimeEntry.objects.filter(user=self.user).order_by('-end_time')
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

    def calculate_performance_comments(self):
        average_performance = self.calculate_performance_rating()
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


class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    wage_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    tax_per_hour = models.DecimalField(max_digits=10, decimal_places=2)

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


class PerformanceAppraisal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    average_performance = models.FloatField(default=0.0)
    comments = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.user.email
