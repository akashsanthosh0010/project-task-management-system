from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Task

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username','email','role','assigned_admin','is_staff','is_superuser')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('role','assigned_admin')}),
    )

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title','assigned_to','status','due_date','worked_hours')
    list_filter = ('status','due_date')

