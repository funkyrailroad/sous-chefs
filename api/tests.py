from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from api.models import Recipe, Task, UserTask
from api.data import test_recipe


def create_test_recipe() -> Recipe:
    tasks = test_recipe["tasks"]
    recipe_name = test_recipe["name"]
    obj = Recipe.objects.create(name=recipe_name)
    recipe_id = obj.id
    task_objs = [Task(description=task, recipe_id=recipe_id) for task in tasks]
    Task.objects.bulk_create(task_objs)
    return obj


def create_test_users(n_users: int) -> list[get_user_model()]:
    users = []
    User = get_user_model()
    for i in range(n_users):
        user = User.objects.create(username=f"user_{i}")
        users.append(user)
    return users


def initialize_user_tasks(recipe_id: int) -> list[UserTask]:
    tasks = Task.objects.filter(recipe_id=recipe_id).order_by("id")
    user_task_objs = []
    for task in tasks:
        user_task_objs.append(UserTask(task=task, status=UserTask.TaskStatus.UPCOMING))
    UserTask.objects.bulk_create(user_task_objs)
    return user_task_objs


class UserTaskTests(APITestCase):
    @classmethod
    def setUp(cls):
        recipe = create_test_recipe()
        cls.recipe_id = recipe.id
        cls.users = create_test_users(3)

    def test_list_recipes(self):
        self.client.force_authenticate(user=self.users[0])
        resp = self.client.get(reverse("recipe-list"))
        self.assertEqual(resp.status_code, 200)

    def test_detail_recipe(self):
        self.client.force_authenticate(user=self.users[0])
        recipe = Recipe.objects.first()
        resp = self.client.get(
            reverse(
                "recipe-detail",
                kwargs=dict(
                    pk=recipe.id,
                ),
            )
        )

    def test_list_recipe_tasks(self):
        self.client.force_authenticate(user=self.users[0])
        recipe = Recipe.objects.first()
        resp = self.client.get(
            reverse(
                "recipe-tasks-list",
                kwargs=dict(
                    pk=recipe.id,
                ),
            )
        )
        self.assertEqual(resp.status_code, 200)

    def test_assign_initialize_all_user_tasks_for_a_recipe(self):
        tasks = Task.objects.filter(recipe_id=self.recipe_id).order_by("id")
        user_task_objs = []
        for task in tasks:
            user_task_objs.append(
                UserTask(task=task, status=UserTask.TaskStatus.UPCOMING)
            )
        UserTask.objects.bulk_create(user_task_objs)
        self.client.force_authenticate(user=self.users[0])
        resp = self.client.get(reverse("user-task-list"))


class AssignTaskTests(APITestCase):
    @classmethod
    def setUp(cls):
        recipe = create_test_recipe()
        cls.recipe_id = recipe.id
        cls.users = create_test_users(3)
        cls.user_task_objs = initialize_user_tasks(cls.recipe_id)

        for ind, user in enumerate(cls.users):
            user_task = cls.user_task_objs[ind]
            user_task.user = user
            user_task.save()

    def test_all_users_see_a_task(self):
        for user in self.users:
            self.client.force_authenticate(user=user)
            resp = self.client.get(reverse("my-task-list"))
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertGreater(len(data), 0, data)

    def test_see_all_tasks(self):
        self.client.force_authenticate(user=self.users[0])
        resp = self.client.get(reverse("user-task-list"))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), len(self.user_task_objs))
