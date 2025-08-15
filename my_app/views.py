import io

import pyqrcode
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import UpdateView
from rest_framework import mixins, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

import my_app.forms as f
import my_app.models as m
import my_app.serializers as s
import my_app.utils as u


class UserTaskUpdateView(UpdateView):
    model = m.UserTask
    fields = ["user", "task", "status"]

    def get_success_url(self, **kwargs) -> str:
        return reverse_lazy("my_app:usertask-detail", kwargs={"pk": self.object.pk})



class UserTaskDetailView(DetailView):
    model = m.UserTask


class UserTaskPotentialBlockersView(ListView):
    model = m.UserTask
    template_name_suffix = "_list_potential_blockers"

    def get_queryset(self):
        pk = self.kwargs["pk"]
        session = m.UserTask.objects.get(pk=pk).group
        qs = session.usertask_set.active().exclude(pk=pk)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pk"] = self.kwargs["pk"]
        return context


class UserTaskBlockView(UpdateView):
    model = m.UserTask
    form_class = f.UserTaskBlockForm
    template_name_suffix = "_block"
    success_url = reverse_lazy("my_app:my-tasks-view")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        usertask = self.get_object()
        # get all active tasks in the cooking session
        qs = u.get_all_usertasks_in_group(usertask.group.id)
        kwargs["potential_blocking_tasks"] = qs.active().exclude(pk=usertask.pk)
        return kwargs


def index(request):
    return TemplateResponse(request, "my_app/index.html", {})


def home(request):
    return TemplateResponse(request, "my_app/home.html", {})


# @login_required
# def my_tasks_view(request):
#     my_tasks = u.get_tasks_for_user(request.user.id)
#     my_tasks = my_tasks.order_by("-task__id")
#     context = {}
#     if my_tasks.count() != 0:
#         my_active_tasks = my_tasks.filter(status=m.UserTask.TaskStatus.ACTIVE)
#         my_completed_tasks = my_tasks.filter(status=m.UserTask.TaskStatus.COMPLETED)
#         group_id = my_tasks.first().group.id
#         context = {
#             "group_id": group_id,
#             "my_active_tasks": my_active_tasks,
#             "my_completed_tasks": my_completed_tasks,
#         }
#     return TemplateResponse(request, "my_app/my-tasks-view.html", context)


@login_required
def my_tasks_view(request):
    my_tasks = u.get_tasks_for_user(request.user.id)
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
    """Mark user task as completed."""
    if request.method == "POST":
        user_task = m.UserTask.objects.get(id=usertask_id)
        user_task.mark_as_completed()
        return redirect("my_app:my-tasks-view")
    return HttpResponseForbidden()


@login_required
def get_next_user_task(request, cooking_session_id):
    if request.method == "GET":
        group = u.get_group(cooking_session_id)
        recipe = u.get_recipe_from_group(group)
        try:
            u.get_next_task_for_user(request.user.id, recipe.id, cooking_session_id)
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
# This should probably be a POST, and redirect to the detail view
def create_cooking_session_view(request, recipe_id):
    recipe = u.get_recipe(recipe_id)

    cooking_group_name = f"Cook {recipe.name} with {request.user.first_name}"
    cooking_group = u.get_or_initialize_cooking_session(cooking_group_name, recipe.id)
    u.add_user_to_group(request.user.id, cooking_group.id)
    try:
        u.get_next_task_for_user(request.user.id, recipe_id, cooking_group.id)
    except u.AllUserTasksAssigned:
        pass
    return redirect("my_app:my-cooking-session", cooking_group.id)


def list_my_cooking_sessions(request):
    user = request.user
    cooking_sessions = user.groups.all()
    context = dict(cooking_sessions=cooking_sessions)
    return TemplateResponse(request, "my_app/list-my-cooking-sessions.html", context)


def usertasks_in_group(request, cooking_session_id):
    session = m.Group.objects.get(id=cooking_session_id)
    usertasks = session.usertask_set.all()
    context = dict(usertasks=usertasks)
    return TemplateResponse(
        request, "my_app/list-user-tasks-in-cooking-sessions.html", context
    )


def my_cooking_session_view(request, cooking_session_id):
    cooking_group = m.Group.objects.get(id=cooking_session_id)

    recipe = u.get_recipe_from_group(cooking_group)
    join_group_url = u.create_cooking_session_join_url(request, cooking_group.id)

    # return current users in group
    context = {
        "recipe": recipe,
        "group": cooking_group,
        "users": cooking_group.user_set.all(),
        "join_group_url": join_group_url,
    }
    return TemplateResponse(request, "my_app/my-cooking-session.html", context)


@login_required
def join_cooking_session_view(request, group_id):
    group = u.get_group(group_id)
    recipe = u.get_recipe_from_group(group)
    u.add_user_to_group(request.user.id, group.id)
    try:
        u.get_next_task_for_user(request.user.id, recipe.id, group.id)
    except u.AllUserTasksAssigned:
        pass
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
