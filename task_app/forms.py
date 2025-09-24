from django import forms
from .models import Task, CustomUser
from django.contrib.auth.forms import UserCreationForm

class TaskAssignForm(forms.ModelForm):
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )
    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'due_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'assigned_to': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class TaskCompleteForm(forms.Form):
    completion_report = forms.CharField(widget=forms.Textarea, required=True)
    worked_hours = forms.DecimalField(max_digits=6, decimal_places=2, required=True)


# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class SignUpForm(UserCreationForm):
    # Only allow USER and ADMIN for public signup (SUPERADMIN should be created manually)
    ROLE_CHOICES = [
        (CustomUser.ROLE_USER, 'User'),
        (CustomUser.ROLE_ADMIN, 'Admin')
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'password1', 'password2')
