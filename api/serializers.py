from rest_framework import serializers
import api.models as m


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.Recipe
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.Task
        fields = "__all__"


class UserTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.UserTask
        fields = "__all__"
