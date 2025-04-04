from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from my_app.models import Task, UserTask, Recipe

User = get_user_model()


def assign_initial_tasks_to_users(
    users: list[User],
    user_task_objs: list[UserTask],
) -> list[UserTask]:
    initially_assigned_tasks = []
    for ind, user in enumerate(users):
        user_task_obj = user_task_objs[ind]
        user_task_obj.user = user
        user_task_obj.status = UserTask.TaskStatus.ACTIVE
        # user_task_obj.save()
        initially_assigned_tasks.append(user_task_obj)
    UserTask.objects.bulk_update(initially_assigned_tasks, ["user", "status"])
    return initially_assigned_tasks


def get_recipe(recipe_id: int) -> Recipe:
    return Recipe.objects.get(id=recipe_id)


def get_user(user_id: int) -> User:
    return User.objects.get(id=user_id)


def get_group(group_id: int) -> Group:
    return Group.objects.get(id=group_id)


def add_user_to_group(user_id: int, group_id: int) -> None:
    user = get_user(user_id)
    group = get_group(group_id)
    user.groups.add(group)


def initialize_user_tasks(recipe_id: int) -> list[UserTask]:
    tasks = Task.objects.filter(recipe_id=recipe_id).order_by("id")
    user_task_objs = []
    for task in tasks:
        user_task_objs.append(UserTask(task=task, status=UserTask.TaskStatus.UPCOMING))
    UserTask.objects.bulk_create(user_task_objs)
    return user_task_objs


def get_next_task_for_user(user_id: int, recipe_id: int) -> UserTask:
    try:
        return get_currently_assigned_task(user_id, recipe_id)
    except UserTask.DoesNotExist:
        pass

    task = get_first_unassigned_task(recipe_id)
    task.user_id = user_id
    task.status = UserTask.TaskStatus.ACTIVE
    task.save()
    return task


class AllUserTasksAssigned(Exception):
    def __init__(self):
        super().__init__("All tasks have been assigned.")


def get_first_unassigned_task(recipe_id: int) -> UserTask:
    first_unassigned_task = (
        UserTask.objects.filter(user=None, task__recipe=recipe_id)
        .order_by("task_id")
        .first()
    )
    if first_unassigned_task is None:
        raise AllUserTasksAssigned()
    return first_unassigned_task


def get_currently_assigned_task(user_id: int, recipe_id: int) -> Task:
    task = UserTask.objects.get(
        user_id=user_id, task__recipe=recipe_id, status=UserTask.TaskStatus.ACTIVE
    )
    return task


def mark_task_complete(usertask: UserTask) -> None:
    usertask.status = UserTask.TaskStatus.COMPLETED
    usertask.save()
