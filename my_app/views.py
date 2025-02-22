from rest_framework import viewsets
from rest_framework.response import Response
import api.models as m
import api.serializers as s
import api.utils as u
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins

from django.db import transaction
from django.http import HttpResponse
from rest_framework.exceptions import ValidationError


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


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
                        request.user.id, serializer.instance.task.recipe_id
                    )
                except Exception as e:
                    # If anything goes wrong while assigning a new task, raise an error
                    raise ValidationError(f"Failed to assign a new task: {str(e)}")

        # Return the updated instance as the response
        return Response(serializer.data)
