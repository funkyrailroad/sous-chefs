x by default all endpoints must be admin
. keep thinking of these user scenarios:
/ define the user scenarios for the minimum prototype
    - I'm the host and I want to distribute tasks between two other users
        - log in
        - pick a recipe
        - create a cooking group (automatically)
        - invite two other users to join the recipe
        - distribute tasks to everybody
    - I'm the host and I want to set up a recipe for people to cook
    - I'm a user and I want to join a session to help cook
    - I'm a user and I want to see which tasks I have to complete
    - I'm the host and I want to see who is responsible for each task
    - I'm a user and I want to see how I can complete my current task
    - I'm a user and I want to mark my task as complete
. create a recipe detail page where you can see all the steps
. click on a recipe and see the steps
. do the simplest prototype (relate each task to a scenario)
    . populate test data with initial state of a recipe ready to start cooking
        - I'm a user and I want to see which tasks I have to complete
    . add a screen for a user to see their assigned tasks
        - I'm a user and I want to see which tasks I have to complete
        . go through the flow
    . define the whole workflow:
        - I'm an admin, and I want to select a recipe to make
        - I'm an admin, I want to invite people to cook with me
            - show them a QR code
        - I'm an anonymous user, I want to join a cooking group from a QR code
          an admin sent me
    . define the requirements for actually testing it out
        . the users are all defined in the database
        . users can look at the whole recipe
        . users can view their assigned tasks and their previously completed
          tasks
        . users can mark their task as completed
    x allow a user to mark a task as completed
    x assign next task to user when they mark their task as complete
        x be able to assign the next task to a user
        x look into "perform_update" for MyTaskViewSet
        x how to test this?
            - have a recipe
            - have a single user
            - initialize user tasks
            - list their steps
            - mark it as complete
            - see that the next unfinished task is assigned to that new user
            - get_next_task_for_user()
    . create a cooking group
        - a "cooking group" is the group of people that are making the same
          recipe at the same time
        - add group field to UserTasks (maybe rename to GroupTasks or
          UserGroupTasks)
        - each group has a full list of tasks in that table
        - only one person within each group can be assigned one task
        - the same user can be assigned that task as part of different tasks
        - one user can be part of multiple cooking groups
        - each cooking group needs an id
        - cooking group may be the wrong term, it could also be
    . accept payments
        - https://django-payments.readthedocs.io/en/latest/
    . be able to add/remove users from a cooking group
    . ensure if a user is removed from a cooking group, their task(s) are able
      to be reassigned to other active users
    . list users in a cooking group
    . choose a recipe as a cooking group
    . see which tasks each user has completed
    . view ingredients list for a recipe
    . view an equipment list for a recipe
    . allow users to create an account
x keep going with tasks
    ~ make a custom user model
    x be able to see all the tasks associated with a recipe
    x create user_tasks table
    x assign tasks to users
. model recipes as DAGs (topological sort)
    - https://philuvarov.io/python-top-sort/
