from django.db import models


class Recipe(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.id} - {self.name}"


class Task(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    description = models.TextField()

    def __str__(self):
        return f"{self.description[:50]}..."
