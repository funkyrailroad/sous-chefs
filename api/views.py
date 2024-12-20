from rest_framework import viewsets
import api.models as m
import api.serializers as s

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
    serializer_class = s.UserTaskSerializer

    def get_queryset(self):
        return m.UserTask.objects.filter(user=self.request.user)
