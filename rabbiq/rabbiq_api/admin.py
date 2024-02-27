from django.contrib import admin
from .models import User,UserProfile,Task,TimeEntry,PerformanceAppraisal

# Register your models here.

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "performance")

    def performance(self, obj):
        result = PerformanceAppraisal.objects.get(user=obj)
        return result.average_performance


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass

@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    pass

@admin.register(PerformanceAppraisal)
class PerformanceAppraisalAdmin(admin.ModelAdmin):
    pass





