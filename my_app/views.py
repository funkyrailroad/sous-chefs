from django.urls import reverse
from rest_framework import viewsets
from rest_framework.response import Response
import my_app.models as m
import my_app.serializers as s
import my_app.utils as u
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.template.response import TemplateResponse
from rest_framework.exceptions import ValidationError


def index(request):
    return TemplateResponse(request, "my_app/index.html", {})


def home(request):
    return TemplateResponse(request, "my_app/home.html", {})


def get_tasks_for_user(user_id):
    tasks = m.UserTask.objects.filter(user=user_id)
    return tasks


def my_tasks_view(request):
    my_tasks = get_tasks_for_user(request.user.id)
    context = {"my_tasks": my_tasks}
    return TemplateResponse(request, "my_app/my-tasks-view.html", context)


def recipes_list_view(request):
    recipes = m.Recipe.objects.all()
    context = {"recipes": recipes}
    return TemplateResponse(request, "my_app/recipes-list-view.html", context)


def recipes_detail_view(request, recipe_id):
    recipe = u.get_recipe(recipe_id)
    tasks = recipe.task_set.all()
    context = {"recipe": recipe, "tasks": tasks}
    return TemplateResponse(request, "my_app/recipe-detail-view.html", context)


@login_required
# Could make sense if this is for admins only
def create_cooking_session_view(request, recipe_id):
    recipe = u.get_recipe(recipe_id)

    cooking_group_name = f"Cook {recipe.name} with {request.user.username}"
    cooking_group = u.initialize_cooking_session(cooking_group_name, recipe.id)
    u.add_user_to_group(request.user.id, cooking_group.id)

    # return a url (eventually QR code) that other people can go to to join
    # cooking_group_endpoint = request.build_absolute_uri()

    # return current users in group
    context = {
        "recipe": recipe,
        "group": cooking_group,
        # "cooking_group_endpoint": cooking_group_endpoint,
    }
    return TemplateResponse(request, "my_app/create-cooking-session.html", context)


class RecipeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = s.RecipeSerializer
    queryset = m.Recipe.objects.all()


class RecipeTaskViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = s.TaskSerializer

    def get_queryset(self):
        recipe_id = self.kwargs["pk"]
        return m.Task.objects.filter(recipe=recipe_id).order_by("id")


class UserTaskViewSet(viewsets.ReadOnlyModelViewSet):
    """General endpoints for all user tasks. Probably best for an admin."""

    serializer_class = s.UserTaskSerializer
    queryset = m.UserTask.objects.all()


class UpdateListRetrieveViewSet(
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """
    A viewset that provides `retrieve`, `update`, and `list` actions.

    To use it, override the class and set the `.queryset` and
    `.serializer_class` attributes.
    """

    pass


class MyTaskViewSet(UpdateListRetrieveViewSet):
    """Specific endpoint for the authenticated user's tasks."""

    serializer_class = s.UserTaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return m.UserTask.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        # Perform the update and additional operations in a single transaction
        with transaction.atomic():
            partial = kwargs.pop("partial", False)
            instance = self.get_object()
            serializer = self.get_serializer(
                instance, data=request.data, partial=partial
            )
            serializer.is_valid(raise_exception=True)

            # Perform the update
            self.perform_update(serializer)

            # Check if the task was marked as completed
            if serializer.instance.status == m.UserTask.TaskStatus.COMPLETED:
                # Assign a new task to the user
                try:
                    u.get_next_task_for_user(
                        request.user.id,
                        serializer.instance.task.recipe_id,
                        instance.group.id,
                    )
                except Exception as e:
                    # If anything goes wrong while assigning a new task, raise an error
                    raise ValidationError(f"Failed to assign a new task: {str(e)}")

        # Return the updated instance as the response
        return Response(serializer.data)
