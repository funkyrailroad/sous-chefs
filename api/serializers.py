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
    task_description = serializers.SerializerMethodField("get_task_description")

    def get_task_description(self, obj):
        return obj.task.description

    class Meta:
        model = m.UserTask
        fields = ["user", "task", "status", "task_description"]
