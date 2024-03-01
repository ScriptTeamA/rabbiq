from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.http import HttpRequest
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Employee,Task,TimeEntry,PerformanceAppraisal,Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    search_fields = ('name',)


class EmployeeInline(admin.StackedInline):
    model = Employee
    #can_delete = False
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
    list_display = ('name', 'description', 'start_date', 'end_date','task_status')
    search_fields = ('name',)
    autocomplete_fields = ['assign_to']
    readonly_fields = ['status']
    ordering = ['end_date']

    def get_fieldsets(self, request, obj=None):
        try:
            user = Employee.objects.get(user=request.user)
            if user.is_manager == False:
                return (
                    (None, {'fields': ('name', 'description','start_date', 'end_date')}),
                )
            return super().get_fieldsets(request, obj)
        except:
            return super().get_fieldsets(request, obj)


    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        user = request.user
        if not user.is_superuser:
            employee = Employee.objects.get(user=user)
            department = employee.department
            if employee.is_manager:
                form.base_fields['assign_to'].queryset = User.objects.filter(employee__department=department, employee__is_manager=True)
        return form
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        if request.user.is_superuser:
            return queryset

        return queryset.filter(assign_to=request.user)
    
    def task_status(self, obj):
        if obj.status:
            return mark_safe('<p class="bg-success">completed</p>')
        else:
            return mark_safe('<p class="bg-warning">pending</p>')

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
    readonly_fields = ['user']

    def get_readonly_fields(self, request, obj=None):
        if not request.user.has_perm('rabbiq_api.change_timeentry'):
            return self.readonly_fields + ['approved']
        elif request.user.has_perm('rabbiq_api.change_timeentry'):
            return self.readonly_fields + ['user', 'task', 'start_time', 'end_time','notes']
    
    def save_model(self, request, obj, form, change):
        # Set the 'user' field to the current user
        obj.user = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Filter the queryset to show only tasks assigned to the current user
        if not request.user.is_superuser:
            qs = qs.filter(user=request.user)
        return qs
    
    def has_delete_permission(self, request, obj=None):
        # Disable the ability to delete existing entries
        return False
    


@admin.register(PerformanceAppraisal)
class PerformanceAppraisalAdmin(admin.ModelAdmin):
    list_display = ('user', 'average_performance','insight','comments')
    ordering = ['average_performance']
    search_fields = ('user__username',)

    def insight(self, obj):
        progress_percentage = round(obj.average_performance, 2)
        return format_html(
            '<progress value="{}" max="100"></progress> {}%'.format(progress_percentage, progress_percentage)
        )
    
    def has_change_permission(self, request, obj=None):
        # Disable the ability to change existing entries
        return False

    def has_delete_permission(self, request, obj=None):
        # Disable the ability to delete existing entries
        return False

    def has_add_permission(self, request, obj = None):
        # Disable the ability to add existing entries
        return False



admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


