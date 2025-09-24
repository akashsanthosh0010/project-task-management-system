from django.urls import path
from . import admin_view
from . import auth_view
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='task_app/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),  # <-- use this
    path('signup/', auth_view.signup, name='signup'),
    path('superadmin/', admin_view.superadmin_dashboard, name='superadmin_dashboard'),
    path('admin-dashboard/', admin_view.admin_dashboard, name='admin_dashboard'),
    path('users/', admin_view.users_list, name='users_list'),
    path('tasks/', admin_view.tasks_list, name='tasks_list'),
    path('tasks/<int:pk>/', admin_view.task_detail, name='task_detail'),
    path('tasks/<int:pk>/complete/', admin_view.task_complete_by_user, name='task_complete'),
    path('tasks/<int:pk>/report/', admin_view.task_report_view, name='task_report_view'),
    path('users/<int:user_id>/assign-admin/', admin_view.assign_admin, name='assign_admin'),
    path('assign-task/', admin_view.assign_task, name='assign_task'),
]

