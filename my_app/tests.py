from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from my_app.models import Recipe, Task, UserTask
from my_app.data import test_recipe
import my_app.utils as u

User = get_user_model()


def create_test_recipe() -> Recipe:
    tasks = test_recipe["tasks"]
    recipe_name = test_recipe["name"]
    obj = Recipe.objects.create(name=recipe_name)
    recipe_id = obj.id
    task_objs = [Task(description=task, recipe_id=recipe_id) for task in tasks]
    Task.objects.bulk_create(task_objs)
    return obj


def create_regular_test_users(n_users: int) -> list[User]:
    users = []
    for i in range(1, n_users + 1):
        username = f"regular_user_{i}"
        user = User.objects.create(
            username=username,
            email=f"{username}@example.com",
        )
        users.append(user)
    return users


def create_admin_test_users(n_users: int) -> list[User]:
    users = []
    for i in range(1, n_users + 1):
        username = f"admin_user_{i}"
        user = User.objects.create(
            username=username,
            email=f"{username}@example.com",
            is_staff=True,
        )
        users.append(user)
    return users


class SousChefsBaseTestCase(APITestCase):
    def list_user_tasks(self, user):
        self.client.force_authenticate(user=user)
        resp = self.client.get(reverse("my_app:my-task-list"))
        self.assertEqual(resp.status_code, 200)
        return resp.json()


def create_test_cooking_group(name: str | None = "Test cooking group") -> Group:
    group = Group.objects.create(name=name)
    return group


class UserTaskTests(APITestCase):
    @classmethod
    def setUp(cls):
        recipe = create_test_recipe()
        cls.recipe_id = recipe.id
        cls.admin_user = create_admin_test_users(1)[0]
        cls.cooking_group = create_test_cooking_group()

    def test_list_recipes(self):
        self.client.force_authenticate(user=self.admin_user)
        resp = self.client.get(reverse("my_app:recipe-list"))
        self.assertEqual(resp.status_code, 200)

    def test_detail_recipe(self):
        self.client.force_authenticate(user=self.admin_user)
        recipe = Recipe.objects.first()
        resp = self.client.get(
            reverse(
                "my_app:recipe-detail",
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
                "my_app:recipe-tasks-list",
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
                UserTask(
                    task=task,
                    status=UserTask.TaskStatus.UPCOMING,
                    group=self.cooking_group,
                )
            )
        UserTask.objects.bulk_create(user_task_objs)
        self.client.force_authenticate(user=self.admin_user)
        resp = self.client.get(reverse("my_app:user-task-list"))
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
        cls.cooking_group = create_test_cooking_group()

        cls.user_task_objs = u.initialize_user_tasks(cls.recipe_id, cls.cooking_group.id)

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
            resp = self.client.get(reverse("my_app:my-task-list"))
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertGreater(len(data), 0, data)
            self.assertEqual(data[0]["status"], UserTask.TaskStatus.ACTIVE)

    def test_see_all_tasks(self):
        self.client.force_authenticate(user=self.admin_user)
        resp = self.client.get(reverse("my_app:user-task-list"))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), len(self.user_task_objs))

    def test_user_1_gets_my_task_detail(self):
        self.client.force_authenticate(user=self.user_1)
        resp = self.client.get(
            reverse(
                "my_app:my-task-detail",
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
                "my_app:my-task-detail",
                kwargs=dict(
                    pk=self.user_1_task_id,
                ),
            ),
            data={"status": "CO"},
        )
        self.assertEqual(resp.status_code, 200)

        data = resp.data
        self.assertEqual(data["status"], UserTask.TaskStatus.COMPLETED)

        # get user_1's tasks again, there should be a new one
        tasks = self.list_user_tasks(self.user_1)
        self.assertEqual(len(tasks), 2)

    def test_user_2_marks_user_1_task_as_complete(self):
        self.client.force_authenticate(user=self.user_2)
        resp = self.client.patch(
            reverse(
                "my_app:my-task-detail",
                kwargs=dict(
                    pk=self.user_1_task_id,
                ),
            ),
            data={"status": "CO"},
        )
        self.assertEqual(resp.status_code, 404)


class AssignNextTaskTests(SousChefsBaseTestCase):
    @classmethod
    def setUp(cls):
        recipe = create_test_recipe()
        cls.recipe_id = recipe.id
        cls.user = create_regular_test_users(1)[0]
        cls.user_id = cls.user.id
        cls.admin_user = create_admin_test_users(1)[0]
        cls.cooking_group = create_test_cooking_group()

        cls.user_task_objs = u.initialize_user_tasks(cls.recipe_id, cls.cooking_group.id)

    def test_with_previously_assigned_task_completed(self):
        # verify no assigned tasks
        tasks = self.list_user_tasks(self.user)
        self.assertEqual(len(tasks), 0)

        # assign task and mark it as completed
        first_unassigned_task = u.get_first_unassigned_task(self.recipe_id, self.cooking_group.id)
        first_unassigned_task.user = self.user
        first_unassigned_task.status = UserTask.TaskStatus.COMPLETED
        first_unassigned_task.save()

        # run function
        task = u.get_next_task_for_user(self.user_id, self.recipe_id, self.cooking_group.id)
        self.assertEqual(task.user, self.user)
        self.assertEqual(task.status, UserTask.TaskStatus.ACTIVE)

        # should return the next available task
        tasks = self.list_user_tasks(self.user)
        self.assertEqual(len(tasks), 2)

    def test_without_previously_assigned_task(self):
        u.get_next_task_for_user(self.user.id, self.recipe_id, self.cooking_group.id)
        tasks = self.list_user_tasks(self.user)
        self.assertEqual(len(tasks), 1)
        task = tasks[0]
        self.assertEqual(task["status"], UserTask.TaskStatus.ACTIVE)

    def test_with_previously_assigned_task_still_active(self):
        # should return the currently assigned and still active task
        # or raise an error

        # verify no assigned tasks
        tasks = self.list_user_tasks(self.user)
        self.assertEqual(len(tasks), 0)

        # assign task and mark it as active
        first_unassigned_task = u.get_first_unassigned_task(self.recipe_id, self.cooking_group.id)
        first_unassigned_task.user = self.user
        first_unassigned_task.status = UserTask.TaskStatus.ACTIVE
        first_unassigned_task.save()

        # run function
        task = u.get_next_task_for_user(self.user_id, self.recipe_id, self.cooking_group.id)
        self.assertEqual(task.user, self.user)
        self.assertEqual(task.status, UserTask.TaskStatus.ACTIVE)

        # should not have assigned a new task
        tasks = self.list_user_tasks(self.user)
        self.assertEqual(len(tasks), 1)


class CookingSessionTests(SousChefsBaseTestCase):
    """
    - Create a cooking session with admin user
    - add a non admin user to the cooking session
    - initialize tasks
    - iterate through all tasks


    - create two different recipes
        - (recipe_1, recipe_2)
    - create two admin users
        - (admin_1, admin_2)
    - create two cooking sessions with the two admin users for the two recipes
        - (cooking_session_1, cooking_session_2)
    - add two non admin users to each cooking group (4 nonadmin users total)
        - regular_user_1a
        - regular_user_1b
        - regular_user_2a
        - regular_user_2b
    - initialize tasks
    - make initial task assignments
    - iterate through all the tasks in group_1
    - see that all tasks for group 1 are completed
    - see that no tasks for group 2 are completed


    - make sure steps from recipe_1 only appear for users in cooking_session_1
    - make sure steps from recipe_2 only appear for users in cooking_session_2

    """

    @classmethod
    def setUpTestData(cls):
        admin_users = create_admin_test_users(2)
        regular_users = create_regular_test_users(4)

        cls.admin_user_1 = admin_users[0]
        cls.admin_user_2 = admin_users[1]

        cls.regular_user_1a = regular_users[0]
        cls.regular_user_1b = regular_users[1]

        cls.regular_user_2a = regular_users[2]
        cls.regular_user_2b = regular_users[3]

        group_name_1 = f"{cls.admin_user_1.username}'s Cooking Session"
        cls.cooking_group_1 = Group.objects.create(name=group_name_1)

        group_name_2 = f"{cls.admin_user_2.username}'s Cooking Session"
        cls.cooking_group_2 = Group.objects.create(name=group_name_2)

        u.add_user_to_group(cls.admin_user_1.id, cls.cooking_group_1.id)
        u.add_user_to_group(cls.admin_user_2.id, cls.cooking_group_2.id)
        u.add_user_to_group(cls.regular_user_1a.id, cls.cooking_group_1.id)
        u.add_user_to_group(cls.regular_user_1b.id, cls.cooking_group_1.id)
        u.add_user_to_group(cls.regular_user_2a.id, cls.cooking_group_2.id)
        u.add_user_to_group(cls.regular_user_2b.id, cls.cooking_group_2.id)

        group_1_users = cls.cooking_group_1.user_set.all()
        group_2_users = cls.cooking_group_2.user_set.all()

        cls.recipe = create_test_recipe()

        group_1_user_task_objs = u.initialize_user_tasks(cls.recipe.id, cls.cooking_group_1.id)
        u.assign_initial_tasks_to_users(group_1_users, group_1_user_task_objs)

        group_2_user_task_objs = u.initialize_user_tasks(cls.recipe.id, cls.cooking_group_2.id)
        u.assign_initial_tasks_to_users(group_2_users, group_2_user_task_objs)

    def test_create_cooking_session(self):
        admin1 = self.admin_user_1
        user_1a = self.regular_user_1a
        user_1b = self.regular_user_1b
        ut_1 = u.get_next_task_for_user(admin1.id, self.recipe.id, self.cooking_group_1.id)
        ut_2 = u.get_next_task_for_user(user_1a.id, self.recipe.id, self.cooking_group_1.id)
        ut_3 = u.get_next_task_for_user(user_1b.id, self.recipe.id, self.cooking_group_1.id)

        u.mark_task_complete(ut_1)
        self.assertEqual(ut_1.status, UserTask.TaskStatus.COMPLETED)

        next_task = u.get_next_task_for_user(user_1a.id, self.recipe.id, self.cooking_group_1.id)
        task_count = 3
        while next_task:
            u.mark_task_complete(next_task)
            try:
                next_task = u.get_next_task_for_user(user_1a.id, self.recipe.id, self.cooking_group_1.id)
                task_count += 1
            except u.AllUserTasksAssigned:
                break

        self.assertEqual(task_count, len(self.recipe.task_set.all()))
