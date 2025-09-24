from rest_framework import serializers
from .models import Task, CustomUser
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email','first_name','last_name','role','assigned_admin']

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True, required=False)

    class Meta:
        model = Task
        fields = ['id','title','description','assigned_to','due_date','status','completion_report','worked_hours','created_at','updated_at']
        read_only_fields = ['created_at','updated_at']

    def validate(self, data):
        # If status set to Completed ensure completion_report and worked_hours present
        status = data.get('status', getattr(self.instance, 'status', None))
        if status == Task.STATUS_COMPLETED:
            # If updating via partial update, check either in data or existing instance fields
            report = data.get('completion_report', getattr(self.instance, 'completion_report', None))
            hours = data.get('worked_hours', getattr(self.instance, 'worked_hours', None))
            if not report:
                raise serializers.ValidationError({"completion_report": "Completion report is required when marking task as Completed."})
            if hours is None:
                raise serializers.ValidationError({"worked_hours": "Worked hours is required when marking task as Completed."})
        return data
