from django.urls import path

from . import views

app_name = "my_app"
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
    path("home", views.home, name="home"),
    path("recipes-list-view", views.recipes_list_view, name="recipes-list-view"),
    path("recipe-detail-view/<int:recipe_id>/", views.recipes_detail_view, name="recipe-detail-view"),
    path("my-tasks-view", views.my_tasks_view, name="my-tasks-view"),
    path("usertasks/<int:usertask_id>/complete", views.complete_user_task, name="complete-user-task"),
    path("create-cooking-session/<int:recipe_id>/", views.create_cooking_session_view, name="create-cooking-session"),
    path("join-cooking-session/<int:group_id>/", views.join_cooking_session_view, name="join-cooking-session"),
    path("cooking-session/<int:cooking_session_id>/join-qr-code", views.get_cooking_session_qr_code, name="join-cooking-session-qr-code"),

    # restful api views
    path("api/recipes/", recipe_list, name="recipe-list"),
    path("api/recipes/<int:pk>/", recipe_detail, name="recipe-detail"),
    path("api/recipes/<int:pk>/tasks/", recipe_tasks_list, name="recipe-tasks-list"),
    path("api/user-tasks/", user_task_list, name="user-task-list"),
    path("api/user-tasks/<int:pk>/", user_task_detail, name="user-task-detail"),
    path("api/my-tasks/", my_task_list, name="my-task-list"),
    path("api/my-tasks/<int:pk>/", my_task_detail, name="my-task-detail"),
]
