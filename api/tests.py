from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from api.models import Recipe, Task, UserTask
from api.data import test_recipe

UserModel = get_user_model()


def create_test_recipe() -> Recipe:
    tasks = test_recipe["tasks"]
    recipe_name = test_recipe["name"]
    obj = Recipe.objects.create(name=recipe_name)
    recipe_id = obj.id
    task_objs = [Task(description=task, recipe_id=recipe_id) for task in tasks]
    Task.objects.bulk_create(task_objs)
    return obj


def create_regular_test_users(n_users: int) -> list[get_user_model()]:
    users = []
    User = get_user_model()
    for i in range(1, n_users + 1):
        user = User.objects.create(username=f"regular_user_{i}")
        users.append(user)
    return users


def create_admin_test_users(n_users: int) -> list[get_user_model()]:
    users = []
    User = get_user_model()
    for i in range(1, n_users + 1):
        user = User.objects.create(username=f"admin_user_{i}", is_staff=True)
        users.append(user)
    return users


def initialize_user_tasks(recipe_id: int) -> list[UserTask]:
    tasks = Task.objects.filter(recipe_id=recipe_id).order_by("id")
    user_task_objs = []
    for task in tasks:
        user_task_objs.append(UserTask(task=task, status=UserTask.TaskStatus.UPCOMING))
    UserTask.objects.bulk_create(user_task_objs)
    return user_task_objs


class SousChefsBaseTestCase(APITestCase):
    def list_user_tasks(self):
        self.client.force_authenticate(user=self.user)
        resp = self.client.get(reverse("my-task-list"))
        self.assertEqual(resp.status_code, 200)
        return resp.json()


class UserTaskTests(APITestCase):
    @classmethod
    def setUp(cls):
        recipe = create_test_recipe()
        cls.recipe_id = recipe.id
        cls.admin_user = create_admin_test_users(1)[0]

    def test_list_recipes(self):
        self.client.force_authenticate(user=self.admin_user)
        resp = self.client.get(reverse("recipe-list"))
        self.assertEqual(resp.status_code, 200)

    def test_detail_recipe(self):
        self.client.force_authenticate(user=self.admin_user)
        recipe = Recipe.objects.first()
        resp = self.client.get(
            reverse(
                "recipe-detail",
                kwargs=dict(
                    pk=recipe.id,
                ),
            )
        )
        self.assertEqual(resp.status_code, 200)

    def test_list_recipe_tasks(self):
        self.client.force_authenticate(user=self.admin_user)
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
        self.client.force_authenticate(user=self.admin_user)
        resp = self.client.get(reverse("user-task-list"))
        self.assertEqual(resp.status_code, 200)


class AssignTaskTests(SousChefsBaseTestCase):
    @classmethod
    def setUp(cls):
        recipe = create_test_recipe()
        cls.recipe_id = recipe.id
        cls.users = create_regular_test_users(3)
        cls.user_1 = cls.users[0]
        cls.user_2 = cls.users[1]
        cls.user_3 = cls.users[2]
        cls.admin_user = create_admin_test_users(1)[0]

        cls.user_task_objs = initialize_user_tasks(cls.recipe_id)

        for ind, user in enumerate(cls.users):
            user_task = cls.user_task_objs[ind]
            user_task.user = user
            user_task.status = UserTask.TaskStatus.ACTIVE
            user_task.save()

        user_1_tasks = UserTask.objects.filter(user=cls.user_1)
        cls.user_1_task_id = user_1_tasks.first().id

    def test_all_users_see_an_active_task(self):
        for user in self.users:
            self.client.force_authenticate(user=user)
            resp = self.client.get(reverse("my-task-list"))
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertGreater(len(data), 0, data)
            self.assertEqual(data[0]["status"], UserTask.TaskStatus.ACTIVE)

    def test_see_all_tasks(self):
        self.client.force_authenticate(user=self.admin_user)
        resp = self.client.get(reverse("user-task-list"))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), len(self.user_task_objs))

    def test_user_1_gets_my_task_detail(self):
        self.client.force_authenticate(user=self.user_1)
        resp = self.client.get(
            reverse(
                "my-task-detail",
                kwargs=dict(
                    pk=self.user_1_task_id,
                ),
            )
        )
        self.assertEqual(resp.status_code, 200)

    def test_user_1_marks_user_1_task_as_complete(self):
        self.client.force_authenticate(user=self.user_1)
        resp = self.client.patch(
            reverse(
                "my-task-detail",
                kwargs=dict(
                    pk=self.user_1_task_id,
                ),
            ),
            data={"status": "CO"},
        )
        self.assertEqual(resp.status_code, 200)

    def test_user_2_marks_user_1_task_as_complete(self):
        self.client.force_authenticate(user=self.user_2)
        resp = self.client.patch(
            reverse(
                "my-task-detail",
                kwargs=dict(
                    pk=self.user_1_task_id,
                ),
            ),
            data={"status": "CO"},
        )
        self.assertEqual(resp.status_code, 404)


def get_next_task_for_user(user_id: int, recipe_id: int) -> Task:
    try:
        return get_currently_assigned_task(user_id, recipe_id)
    except UserTask.DoesNotExist:
        pass

    task = get_first_unassigned_task(recipe_id)
    task.user_id = user_id
    task.status = UserTask.TaskStatus.ACTIVE
    task.save()
    return task


def get_first_unassigned_task(recipe_id: int) -> Task:
    first_unassigned_task = (
        UserTask.objects.filter(user=None, task__recipe=recipe_id)
        .order_by("task_id")
        .first()
    )
    return first_unassigned_task


def get_currently_assigned_task(user_id: int, recipe_id: int) -> Task:
    task = UserTask.objects.get(
        user_id=user_id, task__recipe=recipe_id, status=UserTask.TaskStatus.ACTIVE
    )
    return task


class AssignNextTaskTests(SousChefsBaseTestCase):
    @classmethod
    def setUp(cls):
        recipe = create_test_recipe()
        cls.recipe_id = recipe.id
        cls.user = create_regular_test_users(1)[0]
        cls.user_id = cls.user.id
        cls.admin_user = create_admin_test_users(1)[0]

        cls.user_task_objs = initialize_user_tasks(cls.recipe_id)

    def test_with_previously_assigned_task_completed(self):
        # verify no assigned tasks
        tasks = self.list_user_tasks()
        self.assertEqual(len(tasks), 0)

        # assign task and mark it as completed
        first_unassigned_task = get_first_unassigned_task(self.recipe_id)
        first_unassigned_task.user = self.user
        first_unassigned_task.status = UserTask.TaskStatus.COMPLETED
        first_unassigned_task.save()

        # run function
        task = get_next_task_for_user(self.user_id, self.recipe_id)
        self.assertEqual(task.user, self.user)
        self.assertEqual(task.status, UserTask.TaskStatus.ACTIVE)

        # should return the next available task
        tasks = self.list_user_tasks()
        self.assertEqual(len(tasks), 2)

    def test_without_previously_assigned_task(self):
        get_next_task_for_user(self.user.id, self.recipe_id)
        tasks = self.list_user_tasks()
        self.assertEqual(len(tasks), 1)
        task = tasks[0]
        self.assertEqual(task["status"], UserTask.TaskStatus.ACTIVE)

    def test_with_previously_assigned_task_still_active(self):
        # should return the currently assigned and still active task
        # or raise an error

        # verify no assigned tasks
        tasks = self.list_user_tasks()
        self.assertEqual(len(tasks), 0)

        # assign task and mark it as active
        first_unassigned_task = get_first_unassigned_task(self.recipe_id)
        first_unassigned_task.user = self.user
        first_unassigned_task.status = UserTask.TaskStatus.ACTIVE
        first_unassigned_task.save()

        # run function
        task = get_next_task_for_user(self.user_id, self.recipe_id)
        self.assertEqual(task.user, self.user)
        self.assertEqual(task.status, UserTask.TaskStatus.ACTIVE)

        # should not have assigned a new task
        tasks = self.list_user_tasks()
        self.assertEqual(len(tasks), 1)
