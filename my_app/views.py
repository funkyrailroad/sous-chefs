import io
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseForbidden
from rest_framework import viewsets
from rest_framework.response import Response
import my_app.models as m
import my_app.serializers as s
import my_app.utils as u
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins
import pyqrcode

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.template.response import TemplateResponse
from rest_framework.exceptions import ValidationError


def index(request):
    return TemplateResponse(request, "my_app/index.html", {})


def home(request):
    return TemplateResponse(request, "my_app/home.html", {})


def get_tasks_for_user(user_id: int) -> m.UserTask:
    usertasks = m.UserTask.objects.filter(user=user_id)
    return usertasks


@login_required
def my_tasks_view(request):
    my_tasks = get_tasks_for_user(request.user.id)
    my_tasks = my_tasks.order_by("-task__id")
    my_active_tasks = my_tasks.filter(status=m.UserTask.TaskStatus.ACTIVE)
    my_completed_tasks = my_tasks.filter(status=m.UserTask.TaskStatus.COMPLETED)
    group_id = my_tasks.first().group.id
    context = {
        "group_id": group_id,
        "my_active_tasks": my_active_tasks,
        "my_completed_tasks": my_completed_tasks,
    }
    return TemplateResponse(request, "my_app/my-tasks-view.html", context)


@login_required
def complete_user_task(request, usertask_id):
    if request.method == "POST":
        user_task = m.UserTask.objects.get(id=usertask_id)
        user_task.status = m.UserTask.TaskStatus.COMPLETED
        user_task.save()
        cooking_group = user_task.group
        recipe = u.get_recipe_from_user_task(user_task)
        try:
            u.get_next_task_for_user(request.user.id, recipe.id, cooking_group.id)
        except u.AllUserTasksAssigned:
            # potentially could return something saying you've completed the
            # recipe!
            pass
        return redirect("my_app:my-tasks-view")
    return HttpResponseForbidden()


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
    u.get_next_task_for_user(request.user.id, recipe_id, cooking_group.id)

    # return a url (eventually QR code) that other people can go to to join
    join_group_url = u.create_cooking_session_join_url(request, cooking_group.id)

    # return current users in group
    context = {
        "recipe": recipe,
        "group": cooking_group,
        "users": cooking_group.user_set.all(),
        "join_group_url": join_group_url,
    }
    # breakpoint()
    return TemplateResponse(request, "my_app/create-cooking-session.html", context)


@login_required
def join_cooking_session_view(request, group_id):
    group = u.get_group(group_id)
    recipe = u.get_recipe_from_group(group)
    u.add_user_to_group(request.user.id, group.id)
    u.get_next_task_for_user(request.user.id, recipe.id, group.id)
    return redirect("my_app:my-tasks-view")


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


# probably want to cache this at some point
# most performant option is to have the qr code generated on the frontend
# https://chatgpt.com/c/67f94481-a37c-8010-aea4-6788d6a2b28c
# @login_required
def get_cooking_session_qr_code(request, cooking_session_id):
    # logged in user needs to be a member of the cooking session!
    group = u.get_group(cooking_session_id)
    if request.user not in group.user_set.all():
        return HttpResponseForbidden()

    endpoint = u.create_cooking_session_join_url(request, cooking_session_id)
    qr_code = pyqrcode.create(endpoint)
    buffer = io.BytesIO()
    qr_code.svg(buffer, scale=12)
    svg_data = buffer.getvalue()
    buffer.close()
    return HttpResponse(svg_data, content_type="image/svg+xml")
