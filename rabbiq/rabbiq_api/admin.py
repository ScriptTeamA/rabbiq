from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm
from .models import User,UserProfile,Task,TimeEntry,PerformanceAppraisal

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        # Exclude the user_permissions field from the form
        exclude = ['user_permissions']

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    form = CustomUserChangeForm
    list_display = ("last_name","first_name","email","occupation", "performance")

    def performance(self, obj):
        result = PerformanceAppraisal.objects.get(user=obj)
        return result.average_performance
    
    def occupation(self, obj):
        result = UserProfile.objects.get(user=obj)
        return result.occupation


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    pass

@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    readonly_fields = ['approved','user']

    def get_readonly_fields(self, request, obj=None):
        if not request.user.has_perm('rabbiq_api.change_timeentry'):
            return self.readonly_fields + ['approved']
        return self.readonly_fields

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['user'].initial = request.user
        return form
    

@admin.register(PerformanceAppraisal)
class PerformanceAppraisalAdmin(admin.ModelAdmin):
    pass





