from django.urls import path
from .views import UserTasksList, TaskUpdateView, TaskReportView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # JWT auth
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Task endpoints
    path('tasks/', UserTasksList.as_view(), name='user_tasks'),
    path('tasks/<int:pk>/', TaskUpdateView.as_view(), name='task_update'),
    path('tasks/<int:pk>/report/', TaskReportView.as_view(), name='task_report'),
]
