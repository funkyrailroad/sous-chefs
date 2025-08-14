from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

import my_app.utils as u
from my_app.data import test_recipe
from my_app.models import Group, Recipe, Task, UserTask

User = get_user_model()


def create_recipe(recipe_dict) -> Recipe:
    tasks = recipe_dict["tasks"]
    recipe_name = recipe_dict["name"]
    obj = Recipe.objects.create(name=recipe_name)
    recipe_id = obj.id
    task_objs = [Task(description=task, recipe_id=recipe_id) for task in tasks]
    Task.objects.bulk_create(task_objs)
    return obj


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
        first_name = f"Regular {i}"
        last_name = f"User {i}"
        email_prefix = f"{first_name.lower()}_{last_name.lower()}"
        user = User.objects.create(
            email=f"{email_prefix}@example.com",
            first_name=first_name,
            last_name=last_name,
        )
        users.append(user)
    return users


def create_admin_test_users(n_users: int) -> list[User]:
    users = []
    for i in range(1, n_users + 1):
        first_name = f"Admin {i}"
        last_name = f"User {i}"
        email_prefix = f"{first_name.lower()}_{last_name.lower()}"
        user = User.objects.create(
            email=f"{email_prefix}@example.com",
            first_name=first_name,
            last_name=last_name,
            is_staff=True,
        )
        users.append(user)
    return users


def create_admin_and_regular_users(
    n_admin_users: int, n_regular_users: int
) -> tuple[list[User], list[User]]:
    admin_users = create_admin_test_users(n_admin_users)
    regular_users = create_regular_test_users(n_regular_users)
    return admin_users, regular_users


class SousChefsTestCase(TestCase):
    api_client = APIClient()

    def list_user_tasks(self, user):
        self.api_client.force_authenticate(user=user)
        resp = self.api_client.get(reverse("my_app:my-task-list"))
        self.assertEqual(resp.status_code, 200)
        return resp.json()


def create_test_cooking_group() -> Group:
    group = u.create_cooking_group("Test cooking group")
    return group


class UserTaskTests(SousChefsTestCase):
    @classmethod
    def setUp(cls):
        recipe = create_test_recipe()
        cls.recipe_id = recipe.id
        cls.admin_user = create_admin_test_users(1)[0]
        cls.cooking_group = create_test_cooking_group()

    def test_list_recipes(self):
        self.api_client.force_authenticate(user=self.admin_user)
        resp = self.api_client.get(reverse("my_app:recipe-list"))
        self.assertEqual(resp.status_code, 200)

    def test_detail_recipe(self):
        self.api_client.force_authenticate(user=self.admin_user)
        recipe = Recipe.objects.first()
        resp = self.api_client.get(
            reverse(
                "my_app:recipe-detail",
                kwargs=dict(
                    pk=recipe.id,
                ),
            )
        )
        self.assertEqual(resp.status_code, 200)

    def test_list_recipe_tasks(self):
        self.api_client.force_authenticate(user=self.admin_user)
        recipe = Recipe.objects.first()
        resp = self.api_client.get(
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
        self.api_client.force_authenticate(user=self.admin_user)
        resp = self.api_client.get(reverse("my_app:user-task-list"))
        self.assertEqual(resp.status_code, 200)


class AssignTaskTests(SousChefsTestCase):
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

        cls.user_task_objs = u.initialize_user_tasks(
            cls.recipe_id, cls.cooking_group.id
        )

        for ind, user in enumerate(cls.users):
            user_task = cls.user_task_objs[ind]
            user_task.user = user
            user_task.status = UserTask.TaskStatus.ACTIVE
            user_task.save()

        user_1_tasks = UserTask.objects.filter(user=cls.user_1)
        cls.user_1_task_id = user_1_tasks.first().id

    def test_all_users_see_an_active_task(self):
        for user in self.users:
            self.api_client.force_authenticate(user=user)
            resp = self.api_client.get(reverse("my_app:my-task-list"))
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            self.assertGreater(len(data), 0, data)
            self.assertEqual(data[0]["status"], UserTask.TaskStatus.ACTIVE)

    def test_see_all_tasks(self):
        self.api_client.force_authenticate(user=self.admin_user)
        resp = self.api_client.get(reverse("my_app:user-task-list"))
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), len(self.user_task_objs))

    def test_user_1_gets_my_task_detail(self):
        self.api_client.force_authenticate(user=self.user_1)
        resp = self.api_client.get(
            reverse(
                "my_app:my-task-detail",
                kwargs=dict(
                    pk=self.user_1_task_id,
                ),
            )
        )
        self.assertEqual(resp.status_code, 200)

    def test_user_1_marks_user_1_task_as_complete(self):
        self.api_client.force_authenticate(user=self.user_1)
        resp = self.api_client.patch(
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
        self.api_client.force_authenticate(user=self.user_2)
        resp = self.api_client.patch(
            reverse(
                "my_app:my-task-detail",
                kwargs=dict(
                    pk=self.user_1_task_id,
                ),
            ),
            data={"status": "CO"},
        )
        self.assertEqual(resp.status_code, 404)


class AssignNextTaskTests(SousChefsTestCase):
    @classmethod
    def setUp(cls):
        recipe = create_test_recipe()
        cls.recipe_id = recipe.id
        cls.user = create_regular_test_users(1)[0]
        cls.user_id = cls.user.id
        cls.admin_user = create_admin_test_users(1)[0]
        cls.cooking_group = create_test_cooking_group()

        cls.user_task_objs = u.initialize_user_tasks(
            cls.recipe_id, cls.cooking_group.id
        )

    def test_with_previously_assigned_task_completed(self):
        # verify no assigned tasks
        tasks = self.list_user_tasks(self.user)
        self.assertEqual(len(tasks), 0)

        # assign task and mark it as completed
        first_unassigned_task = u.get_first_upcoming_task(
            self.recipe_id, self.cooking_group.id
        )
        first_unassigned_task.user = self.user
        first_unassigned_task.status = UserTask.TaskStatus.COMPLETED
        first_unassigned_task.save()

        # run function
        task = u.get_next_task_for_user(
            self.user_id, self.recipe_id, self.cooking_group.id
        )
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
        first_unassigned_task = u.get_first_upcoming_task(
            self.recipe_id, self.cooking_group.id
        )
        first_unassigned_task.user = self.user
        first_unassigned_task.status = UserTask.TaskStatus.ACTIVE
        first_unassigned_task.save()

        # run function
        task = u.get_next_task_for_user(
            self.user_id, self.recipe_id, self.cooking_group.id
        )
        self.assertEqual(task.user, self.user)
        self.assertEqual(task.status, UserTask.TaskStatus.ACTIVE)

        # should not have assigned a new task
        tasks = self.list_user_tasks(self.user)
        self.assertEqual(len(tasks), 1)


class CreateCookingSessionViewTests(SousChefsTestCase):
    @classmethod
    def setUp(cls):
        cls.recipe = create_test_recipe()
        cls.recipe_id = cls.recipe.id
        cls.admin_user = create_admin_test_users(1)[0]
        cls.regular_user = create_regular_test_users(1)[0]

    def test_get_create_cooking_session_view(self):
        self.client.force_login(user=self.admin_user)
        resp = self.client.get(
            reverse(
                "my_app:create-cooking-session",
                kwargs=dict(
                    recipe_id=self.recipe_id,
                ),
            ),
            follow=True,
        )
        self.assertEqual(resp.status_code, 200)
        context = resp.context
        group = context["group"]
        self.assertIn(self.admin_user, group.user_set.all())
        self.assertNotIn(self.regular_user, group.user_set.all())

        # Check name of group
        self.assertEqual(
            group.name, f"Cook {self.recipe.name} with {self.admin_user.first_name}"
        )

        # admin has a task
        self.assertTrue(
            u.get_currently_assigned_task(self.admin_user, self.recipe_id, group.id)
        )

        # regular user does not have a task
        with self.assertRaises(UserTask.DoesNotExist):
            (
                u.get_currently_assigned_task(
                    self.regular_user, self.recipe_id, group.id
                ),
            )

        join_group_url = context["join_group_url"]

        self.client.force_login(user=self.regular_user)
        resp = self.client.get(join_group_url)
        group.refresh_from_db()
        self.assertIn(self.admin_user, group.user_set.all())
        self.assertIn(self.regular_user, group.user_set.all())

        admin_task = u.get_currently_assigned_task(
            self.admin_user, self.recipe_id, group.id
        )
        self.assertIsNotNone(admin_task)
        reg_task = u.get_currently_assigned_task(
            self.regular_user, self.recipe_id, group.id
        )
        self.assertIsNotNone(reg_task)
        self.assertNotEqual(admin_task, reg_task)


class CookingSessionTests(SousChefsTestCase):
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

        group_name_1 = f"{cls.admin_user_1.first_name}'s Cooking Session"
        cls.cooking_group_1 = Group.objects.create(name=group_name_1)

        group_name_2 = f"{cls.admin_user_2.first_name}'s Cooking Session"
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

        group_1_user_task_objs = u.initialize_user_tasks(
            cls.recipe.id, cls.cooking_group_1.id
        )
        u.assign_initial_tasks_to_users(group_1_users, group_1_user_task_objs)

        group_2_user_task_objs = u.initialize_user_tasks(
            cls.recipe.id, cls.cooking_group_2.id
        )
        u.assign_initial_tasks_to_users(group_2_users, group_2_user_task_objs)

    def test_create_cooking_session(self):
        admin1 = self.admin_user_1
        user_1a = self.regular_user_1a
        user_1b = self.regular_user_1b
        ut_1 = u.get_next_task_for_user(
            admin1.id, self.recipe.id, self.cooking_group_1.id
        )
        ut_2 = u.get_next_task_for_user(
            user_1a.id, self.recipe.id, self.cooking_group_1.id
        )
        ut_3 = u.get_next_task_for_user(
            user_1b.id, self.recipe.id, self.cooking_group_1.id
        )

        u.mark_task_complete(ut_1)
        self.assertEqual(ut_1.status, UserTask.TaskStatus.COMPLETED)

        next_task = u.get_next_task_for_user(
            user_1a.id, self.recipe.id, self.cooking_group_1.id
        )
        task_count = 3
        while next_task:
            u.mark_task_complete(next_task)
            try:
                next_task = u.get_next_task_for_user(
                    user_1a.id, self.recipe.id, self.cooking_group_1.id
                )
                task_count += 1
            except u.AllUserTasksAssigned:
                break

        self.assertEqual(task_count, len(self.recipe.task_set.all()))

    def test_initialize_cooking_session_doubly(self):
        """Ensure there's no error."""
        cooking_group_name = (
            f"Cook {self.recipe.name} with {self.admin_user_1.first_name}"
        )

        u.get_or_initialize_cooking_session(cooking_group_name, self.recipe.id)

        u.get_or_initialize_cooking_session(cooking_group_name, self.recipe.id)

    def test_2(self):
        # Additional testing ideas:
        # start to see if the tasks from the second group are still available.
        # make sure all assigned tasks are assigned in order that the recipe gives
        # make sure the number of assigned tasks equuals the number of tasks in the recipe
        pass

    def test_get_my_cooking_session_view(self):
        self.client.force_login(user=self.regular_user_1a)
        resp = self.client.get(
            reverse("my_app:my-cooking-session", args=(self.cooking_group_1.id,))
        )
        self.assertEqual(resp.status_code, 200)


class MyTasksTests(SousChefsTestCase):
    @classmethod
    def setUpTestData(cls):
        # be a user
        cls.user = create_regular_test_users(1)[0]

        # have a task assigned to me
        recipe = Recipe.objects.create(name="Test recipe")
        task_1 = Task.objects.create(
            recipe_id=recipe.id,
            description="Test task 1",
        )
        task_2 = Task.objects.create(
            recipe_id=recipe.id,
            description="Test task 2",
        )
        group = Group.objects.create(name="Test group")
        u.add_user_to_group(cls.user.id, group.id)
        usertask1 = UserTask.objects.create(
            user=cls.user,
            task=task_1,
            group=group,
            status=UserTask.TaskStatus.ACTIVE,
        )
        usertask2 = UserTask.objects.create(
            # user=cls.user,
            task=task_2,
            group=group,
            status=UserTask.TaskStatus.UPCOMING,
        )

    def test_mark_task_complete(self):
        # call my tasks endpoint, see it
        self.client.force_login(user=self.user)
        resp = self.client.get(reverse("my_app:my-tasks-view"))
        my_active_tasks = resp.context["my_active_tasks"]
        self.assertEqual(len(my_active_tasks), 1)
        my_active_task = my_active_tasks[0]

        # it's assigned, but unfinished
        self.assertEqual(my_active_task.status, UserTask.TaskStatus.ACTIVE)
        self.assertEqual(my_active_task.user, self.user)

        # call complete_task endpoint
        resp = self.client.post(
            reverse(
                "my_app:complete-user-task", kwargs={"usertask_id": my_active_task.id}
            ),
            follow=True,
        )
        context = resp.context
        my_completed_tasks = context["my_completed_tasks"]
        # get response, see I have another task
        self.assertEqual(len(my_completed_tasks), 1)
        my_completed_task = my_completed_tasks[0]
        self.assertEqual(my_completed_task.status, UserTask.TaskStatus.COMPLETED)


class JoinCookingSessionQRCodeViewTests(SousChefsTestCase):
    @classmethod
    def setUp(cls):
        # have a valid cooking session
        cls.cooking_session = Group.objects.create(name="Test cooking session")
        cls.admin = create_admin_test_users(1)[0]
        cls.user = create_regular_test_users(1)[0]

        # have admin in that group
        u.add_user_to_group(cls.admin.id, cls.cooking_session.id)

    def test_with_user_in_session(self):
        self.client.force_login(self.admin)
        resp = self.client.get(
            reverse(
                "my_app:join-cooking-session-qr-code",
                kwargs={"cooking_session_id": self.cooking_session.id},
            ),
        )
        self.assertEqual(resp.status_code, 200)

    def test_anon_user(self):
        resp = self.client.get(
            reverse(
                "my_app:join-cooking-session-qr-code",
                kwargs={"cooking_session_id": self.cooking_session.id},
            ),
        )
        self.assertEqual(resp.status_code, 403)

    def test_with_user_not_in_session(self):
        self.client.force_login(self.user)
        resp = self.client.get(
            reverse(
                "my_app:join-cooking-session-qr-code",
                kwargs={"cooking_session_id": self.cooking_session.id},
            ),
        )
        self.assertEqual(resp.status_code, 403)


class SeeGroupTasksTests(SousChefsTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.recipe = create_test_recipe()
        cls.recipe_id = cls.recipe.id

        # create users
        cls.admin_user = create_admin_test_users(1)[0]
        cls.regular_user = create_regular_test_users(1)[0]

        # initialize cooking session
        group_name = f"{cls.admin_user.first_name}'s Cooking Session"
        cls.cooking_group = Group.objects.create(name=group_name)

        # add users to cooking session
        u.add_user_to_group(cls.admin_user.id, cls.cooking_group.id)
        u.add_user_to_group(cls.regular_user.id, cls.cooking_group.id)

        # users all have their tasks
        group_users = cls.cooking_group.user_set.all()
        group_user_task_objs = u.initialize_user_tasks(
            cls.recipe.id, cls.cooking_group.id
        )
        u.assign_initial_tasks_to_users(group_users, group_user_task_objs)

        # call the endpoint for an admin to see all the tasks

    def test_1(self):
        resp = self.client.get(
            reverse("my_app:usertasks-in-group", args=(self.cooking_group.id,))
        )


class BlockingTasksTests(SousChefsTestCase):
    @classmethod
    def setUpTestData(cls):
        recipe_dict = {
            "name": "Bratwurst with pesto pasta, greek salad and fruit",
            "tasks": [
                "get out pot for cooking pasta, fill it with water, and start boiling the water",  # 1a takes time
                "fry bratwurst in a pan on medium heat until golden brown",  # 2a takes time
                "start playing some music, ask everybody for one or two songs to add to the queue, and add them",  # fun-a
                "Add pasta to boiling water for proper duration and strain it when done",  # 1b takes time
                "Get out a serving bowl for the salad and tell others this is the salad bowl",  # 3a
                "get bell peppers, rinse, remove seeds, slice into squares and put into salad bowl",  # 3b
                "Get cucumbers, rinse, slice into bite-size pieces and put into salad bowl",  # 3c
                "Get tomatoes, rinse, slice into bite-size pieces and put into salad bowl",  # 3d
                "Get red onion, rinse, slice into thin rings and put into salad bowl",  # 3e
            ],
        }
        cls.recipe = create_recipe(recipe_dict)
        # create all user tasks for the recipe
        cls.cooking_session = u.get_or_initialize_cooking_session(
            "Test cooking session", cls.recipe.id
        )
        admin_users, regular_users = create_admin_and_regular_users(1, 3)
        cls.admin_user = admin_users[0]
        cls.regular_user_1 = regular_users[0]
        cls.regular_user_2 = regular_users[1]
        cls.regular_user_3 = regular_users[2]

        all_users = [*admin_users, *regular_users]
        all_user_ids = [user.id for user in all_users]
        # add the three users to the cooking group
        u.add_users_to_group(all_user_ids, cls.cooking_session.id)

        usertasks = u.get_all_usertasks_in_group(cls.cooking_session.id)
        cls.initial_tasks = u.assign_initial_tasks_to_users(all_users, usertasks)

    def test_blocked_task_not_distributed_until_freed(self):
        blocked_usertask: UserTask = self.regular_user_3.usertask_set.active().get()
        blocking_usertask: UserTask = self.admin_user.usertask_set.active().get()

        # reg_user_3 marks task as blocked by first task
        blocked_usertask.mark_as_blocked_by(blocking_usertask)
        u.get_next_task_for_user(
            self.regular_user_3.id, self.recipe.id, self.cooking_session.id
        )
        # check that regular_user_3 has an active task
        self.assertEqual(self.regular_user_3.usertask_set.active().count(), 1)

        # Assign and complete all remaining tasks
        while True:
            try:
                usertask = u.get_next_task_for_user(
                    self.regular_user_3.id, self.recipe.id, self.cooking_session.id
                )
                usertask.mark_as_completed()
            except u.AllUserTasksAssigned:
                break

        self.assertEqual(self.regular_user_3.usertask_set.active().count(), 0)

        # complete the blocking task
        blocking_usertask.mark_as_completed()
        blocking_usertask.mark_blocked_tasks_as_upcoming()

        # assign another task to the user
        usertask = u.get_next_task_for_user(self.regular_user_3.id, self.recipe.id, self.cooking_session.id)
        # verify the task that is assigned is the task that was blocked
        self.assertEqual(usertask, blocked_usertask)

        # verify no more available upcoming tasks
        with self.assertRaises(u.AllUserTasksAssigned):
            u.get_first_upcoming_task(self.recipe.id, self.cooking_session.id)
