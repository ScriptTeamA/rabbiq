from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from .models import Employee,Task,TimeEntry,PerformanceAppraisal,Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = 'Employee'
    autocomplete_fields = ['department']


class CustomUserAdmin(UserAdmin):
    inlines = (EmployeeInline, )
    
    # Customizing the change form
    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_search_field'] = True  # Adding the search field flag
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    # Adding the search field to the change form
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj and 'show_search_field' in request.GET:
            fieldsets += (
                (_('Search'), {'fields': ('search_field',)}),
            )
        return fieldsets



@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    autocomplete_fields = ['assign_to']

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        user = request.user
        if not user.is_superuser:
            employee = Employee.objects.get(user=user)
            department = employee.department
            form.base_fields['assign_to'].queryset = User.objects.filter(employee__department=department, employee__is_manager=True)
        return form

@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'task', 'start_time', 'end_time', 'approved')
    list_filter = ('approved',)
    search_fields = ('user__username', 'task__name')
    date_hierarchy = 'start_time'
    autocomplete_fields = ['task']
    fieldsets = (
        (None, {
            'fields': ('user', 'task')
        }),
        ('Time Information', {
            'fields': ('start_time', 'end_time')
        }),
        ('Additional Notes', {
            'fields': ('notes',)
        }),
        ('Approvals', {
            'fields': ('approved',)
        }),
    )
    readonly_fields = ['approved', 'user']

    def get_readonly_fields(self, request, obj=None):
        if not request.user.has_perm('rabbiq_api.change_timeentry'):
            return self.readonly_fields + ['approved']
        return self.readonly_fields
    
    def get_exclude(self, request, obj=None):
        # Exclude the 'user' field from the change form
        if obj is not None:
            return ['user']
        return []

@admin.register(PerformanceAppraisal)
class PerformanceAppraisalAdmin(admin.ModelAdmin):
    pass




admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


