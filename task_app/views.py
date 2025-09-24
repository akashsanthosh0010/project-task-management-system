from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from .serializers import TaskSerializer
from .models import Task
from django.shortcuts import get_object_or_404
from .permissions import IsAssignedUser, IsSuperAdmin, IsAdmin
from rest_framework.views import APIView

class UserTasksList(generics.ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Task.objects.filter(assigned_to=user).order_by('-created_at')

class TaskUpdateView(generics.UpdateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsAssignedUser]
    queryset = Task.objects.all()
    lookup_url_kwarg = 'pk'

    def update(self, request, *args, **kwargs):
        partial = False  # full update expected per task
        instance = self.get_object()
        # Ensure user is assigned to this task (IsAssignedUser permission will check)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class TaskReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        task = get_object_or_404(Task, pk=pk)
        # Admin or SuperAdmin only
        if not (request.user.is_admin() or request.user.is_superadmin()):
            return Response({"detail": "You do not have permission to view reports."}, status=status.HTTP_403_FORBIDDEN)
        if task.status != Task.STATUS_COMPLETED:
            return Response({"detail": "Report available only for completed tasks."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TaskSerializer(task)
        # Return only report and worked_hours along with basic info
        return Response({
            "task_id": task.id,
            "title": task.title,
            "assigned_to": task.assigned_to.id if task.assigned_to else None,
            "completion_report": task.completion_report,
            "worked_hours": str(task.worked_hours),
            "completed_at": task.updated_at
        })

