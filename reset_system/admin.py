from django.contrib import admin
from .models import Department, UserProfile, PasswordResetRequest

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'is_deputy_director')
    list_filter = ('is_deputy_director', 'department')
    search_fields = ('user__username', 'user__email')

@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = (
        'requestor', 'system', 'reason', 'status', 'created_at', 'updated_at',
        'approver', 'ict_personnel'
    )
    list_filter = ('status', 'system', 'department')
    search_fields = ('requestor__username', 'reason', 'department__name')
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ("Request Details", {
            'fields': ('requestor', 'system', 'reason', 'department', 'status')
        }),
        ("Approvals", {
            'fields': ('approver', 'deputy_director_comments', 'cto_comments')
        }),
        ("ICT Section", {
            'fields': ('ict_personnel', 'completed_at')
        }),
        ("Timestamps", {
            'fields': ('created_at', 'updated_at')
        }),
    )
