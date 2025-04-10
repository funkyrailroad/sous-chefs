from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _


class Recipe(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.id} - {self.name}"


# might rename this to RecipeStep or something, and then UserTask to Task
class Task(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
        return f"{self.id} - {self.description[:50]}..."


class UserTask(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    class TaskStatus(models.TextChoices):
        UPCOMING = "UP", _("Upcoming")
        BLOCKED = "BL", _("Blocked")
        ACTIVE = "AC", _("Active")
        COMPLETED = "CO", _("Completed")

    status = models.CharField(choices=TaskStatus.choices, max_length=5)

    def __str__(self):
        return f"{self.user} - {self.task}..."

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["task", "group"], name="unique user tasks")
        ]
