from my_app.models import Task, UserTask, Recipe


def get_recipe(recipe_id):
    return Recipe.objects.get(id=recipe_id)


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


def get_first_unassigned_task(recipe_id: int) -> UserTask:
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
