from django.urls import path

from . import views

user_task_list = views.UserTaskViewSet.as_view(
    {
        "get": "list",
    }
)

user_task_detail = views.UserTaskViewSet.as_view(
    {
        "get": "retrieve",
    }
)

urlpatterns = [
    path("", views.index, name="index"),
    path("user-tasks/", user_task_list, name="user-task-list"),
    path("user-tasks/<int:pk>/", user_task_detail, name="user-task-detail"),
]
