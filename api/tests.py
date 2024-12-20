from django.test import TestCase
from django.urls import reverse

from .data import test_recipe


class IndexViewTests(TestCase):
    def setUp(self):
        self.tasks = test_recipe["tasks"]
        self.recipe_name = test_recipe["name"]

    def test_index_view(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello, world. You're at the polls index.")

    def test_create_recipe(self):
        obj = Recipe.objects.create(name=self.recipe_name)
        recipe_id = obj.id

        task_objs = [Task(description=task, recipe_id=recipe_id) for task in self.tasks]
        Task.objects.bulk_create(task_objs)
        breakpoint()
