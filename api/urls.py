from django.urls import path

from . import views

recipe_list = views.RecipeViewSet.as_view(
    {
        "get": "list",
    }
)

recipe_detail = views.RecipeViewSet.as_view(
    {
        "get": "retrieve",
    }
)

recipe_tasks_list = views.RecipeTaskViewSet.as_view(
    {
        "get": "list",
    }
)

my_task_list = views.MyTaskViewSet.as_view(
    {
        "get": "list",
    }
)

my_task_detail = views.MyTaskViewSet.as_view(
    {
        "get": "retrieve",
        "patch": "partial_update",
    }
)

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
    path("recipes/", recipe_list, name="recipe-list"),
    path("recipes/<int:pk>/", recipe_detail, name="recipe-detail"),
    path("recipes/<int:pk>/tasks/", recipe_tasks_list, name="recipe-tasks-list"),
    path("user-tasks/", user_task_list, name="user-task-list"),
    path("user-tasks/<int:pk>/", user_task_detail, name="user-task-detail"),
    path("my-tasks/", my_task_list, name="my-task-list"),
    path("my-tasks/<int:pk>/", my_task_detail, name="my-task-detail"),
]
