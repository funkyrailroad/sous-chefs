from rest_framework import serializers
import api.models as m


class UserTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = m.UserTask
        fields = "__all__"
