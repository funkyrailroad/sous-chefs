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


class UserTaskQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status=UserTask.TaskStatus.ACTIVE)

    def completed(self):
        return self.filter(status=UserTask.TaskStatus.COMPLETED)

    def blocked(self):
        return self.filter(status=UserTask.TaskStatus.BLOCKED)

    def upcoming(self):
        return self.filter(status=UserTask.TaskStatus.UPCOMING)


class UserTask(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    blocked_by = models.ForeignKey("self", on_delete=models.DO_NOTHING, null=True, blank=True, related_name="blocked_tasks")
    reported_blocked_by = models.ForeignKey(get_user_model(), on_delete=models.DO_NOTHING, null=True, blank=True, related_name="reported_blocked_tasks")

    class TaskStatus(models.TextChoices):
        UPCOMING = "UP", _("Upcoming")
        BLOCKED = "BL", _("Blocked")
        ACTIVE = "AC", _("Active")
        COMPLETED = "CO", _("Completed")

    status = models.CharField(choices=TaskStatus.choices, max_length=5)
    objects = UserTaskQuerySet.as_manager()

    def __str__(self):
        return f"{self.user} - {self.task}..."

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["task", "group"], name="unique user tasks")
        ]

    def mark_as_completed(self):
        # if this task blocks any others, unblock those tasks
        self.status = UserTask.TaskStatus.COMPLETED
        self.save()

    def mark_blocked_tasks_as_upcoming(self):
        self.blocked_tasks.update(status=UserTask.TaskStatus.UPCOMING)

    def mark_as_blocked_by(self, blocking_task: "UserTask"):
        self.status = UserTask.TaskStatus.BLOCKED
        self.blocked_by = blocking_task
        self.reported_blocked_by = self.user
        self.user = None  # Unassign the user from this task
        self.save()

    def mark_as_blocked(self):
        self.status = UserTask.TaskStatus.BLOCKED
        self.save()

    def mark_as_active(self):
        self.status = UserTask.TaskStatus.ACTIVE
        self.save()

    def mark_as_upcoming(self):
        self.status = UserTask.TaskStatus.UPCOMING
        self.save()
