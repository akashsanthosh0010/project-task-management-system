from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Task, CustomUser
from .forms import TaskAssignForm, TaskCompleteForm
from django.contrib import messages
from django.urls import reverse

def role_required(roles):
    def decorator(view_func):
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.role not in roles:
                return render(request, 'task_app/base.html', {'error': 'Permission denied'})
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator

@login_required
@role_required(['SUPERADMIN'])
def superadmin_dashboard(request):
    users = CustomUser.objects.all()
    admins = CustomUser.objects.filter(role=CustomUser.ROLE_ADMIN)
    tasks = Task.objects.all().order_by('-created_at')
    return render(request, 'task_app/superadmin_dashboard.html', {'users':users,'admins':admins,'tasks':tasks})

@login_required
@role_required(['ADMIN', 'SUPERADMIN'])
def admin_dashboard(request):
    tasks = Task.objects.all()  # or filter by assigned_to
    from .forms import TaskAssignForm
    form = TaskAssignForm()
    # Limit users depending on role
    if request.user.is_admin():
        form.fields['assigned_to'].queryset = CustomUser.objects.filter(assigned_admin=request.user)
    elif request.user.is_superadmin():
        form.fields['assigned_to'].queryset = CustomUser.objects.filter(role=CustomUser.ROLE_USER)
    return render(request, 'task_app/admin_dashboard.html', {'tasks': tasks, 'form': form})


@login_required
@role_required(['SUPERADMIN'])
def users_list(request):
    users = CustomUser.objects.filter(role=CustomUser.ROLE_USER)
    admins = CustomUser.objects.filter(role=CustomUser.ROLE_ADMIN)
    return render(request, 'task_app/users_list.html', {'users': users, 'admins': admins})

@login_required
@role_required(['ADMIN','SUPERADMIN', 'USER'])
def tasks_list(request):
    if request.user.is_superadmin():
        tasks = Task.objects.all().order_by('-created_at')
    elif request.user.is_admin():
        # Tasks assigned to users managed by this admin
        tasks = Task.objects.filter(assigned_to__assigned_admin=request.user).order_by('-created_at')
    else:
        # Tasks assigned to the logged-in user
        tasks = Task.objects.filter(assigned_to=request.user).order_by('-created_at')

    return render(request, 'task_app/tasks_list.html', {'tasks': tasks})




@login_required
@role_required(['ADMIN','SUPERADMIN', 'USER'])
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        # Admin can assign/update task fields
        form = TaskAssignForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated')
            return redirect(reverse('tasks_list'))
    else:
        form = TaskAssignForm(instance=task)
    return render(request, 'task_app/task_detail.html', {'task':task,'form':form})

@login_required
def task_complete_by_user(request, pk):
    # This view allows a user to mark their own task completed (admin-panel style).
    task = get_object_or_404(Task, pk=pk)
    if task.assigned_to != request.user:
        messages.error(request, 'You can only update your own tasks.')
        return redirect('admin_dashboard')
    if request.method == 'POST':
        form = TaskCompleteForm(request.POST)
        if form.is_valid():
            report = form.cleaned_data['completion_report']
            hours = form.cleaned_data['worked_hours']
            task.completion_report = report
            task.worked_hours = hours
            task.status = Task.STATUS_COMPLETED
            task.save()
            messages.success(request, 'Task marked as completed.')
            return redirect('admin_dashboard')
    else:
        form = TaskCompleteForm()
    return render(request, 'task_app/task_report.html', {'task':task,'form':form})

@login_required
@role_required(['ADMIN','SUPERADMIN'])
def task_report_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    # Only for completed tasks
    if task.status != Task.STATUS_COMPLETED:
        messages.error(request, 'Report available only for completed tasks.')
        return redirect('tasks_list')
    return render(request, 'task_app/task_report.html', {'task':task})

@role_required(['SUPERADMIN'])
def assign_admin(request, user_id):
    if request.method == 'POST' and request.user.is_superadmin():
        user = get_object_or_404(CustomUser, id=user_id)
        admin_id = request.POST.get('assigned_admin')
        if admin_id:
            admin = get_object_or_404(CustomUser, id=admin_id, role=CustomUser.ROLE_ADMIN)
            user.assigned_admin = admin
            user.save()
            messages.success(request, f"{user.username} is now assigned to {admin.username}.")
    return redirect('users_list')


@login_required
@role_required(['ADMIN', 'SUPERADMIN'])
def assign_task(request):
    # Create form first
    if request.user.is_admin():
        qs = CustomUser.objects.filter(assigned_admin=request.user)
    elif request.user.is_superadmin():
        qs = CustomUser.objects.filter(role=CustomUser.ROLE_USER)
    else:
        qs = CustomUser.objects.none()

    if request.method == 'POST':
        form = TaskAssignForm(request.POST)
        form.fields['assigned_to'].queryset = qs  # <-- Set before validation
        if form.is_valid():
            form.save()
            messages.success(request, "Task assigned successfully!")
            return redirect('admin_dashboard')
        else:
            messages.error(request, f"Error: {form.errors}")  # Show exact errors
    else:
        form = TaskAssignForm()
        form.fields['assigned_to'].queryset = qs  # <-- Set queryset for GET form

    tasks = Task.objects.all()
    return render(request, 'task_app/admin_dashboard.html', {'form': form, 'tasks': tasks})


