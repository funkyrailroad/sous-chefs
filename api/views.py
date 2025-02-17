from rest_framework import viewsets
import api.models as m
import api.serializers as s
from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins

from django.http import HttpResponse


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
