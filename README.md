x by default all endpoints must be admin
. keep thinking of these user scenarios:
/ define the user scenarios for the minimum prototype
    - I'm the host and I want to navigate to an existing cooking group I
      created
        - see my group
    - I'm the host and I want to see who is responsible for each task
    - I'm a user and I want to see how I can complete my current task
    - I'm a user and I want to update my user info
        . be able to update your user info (email, first_name, last_name,
          password)
    x I'm the host and I want to see who is in my cooking group
        - cooking group detail view
    x I'm the host and I want to set up a recipe for people to cook
    x I'm a user and I want to see which tasks I have to complete
    x I'm a user and I want to mark my task as complete
    x I'm a user and I want to join a session to help cook
        x scan a qr code
            - join-cooking-group
        x create an endpoint that automatically creates a user, logs them in,
          and joins the group
            - user needs to enter email address and first name
        x slightly different flow for if the user is already logged in
        x get your first task
        x join the group immediately
    x I'm the host and I want to distribute tasks between two other users
        x log in
        x pick a recipe
        x create a cooking group (automatically)
        x invite two other users to join the recipe
        x distribute tasks to everybody
/ figure out that flow to have a user without an account to scan a qr code,
  create an account, and get redirected to the my tasks page
    x as admin, create cooking session
    x scan a qr code as a non-logged in user
    x get prompted to login
    x click register
        x I don't jump to the join cooking session page, that must have gotten
          lost while going from the login page to the registration page
    x see my tasks
        x might have to use the "next" query parameter to redirect if it's
          provided
    . plan a test for this
        - create a group
        - create an admin
        - as an unlogged in user, go to the join url
x figure out the flow of having an unlogged in user with an account scan a qr
  code, log in, and get redirected to the my tasks page
. only allow paying customers to create cooking sessions
    .
. fix bug when use clicks my tasks without having been assigned a group or
  task
. don't error when a newly created user logs in and clicks my tasks
    - options:
        - only show the "my-tasks" link if user has tasks
. be able to show another potential user a qr code from the my tasks list
. be able to show another potential user a qr code from the cooking session
  homepage
. cook a whole recipe that I want to make myself
    ? tacos
    ? teriyaki chicken thighs and fried rice
    ? a big stew
. be able to quickly get back to my latest cooking group from the homepage
. add "My cooking groups" to the home page
. handle if someone has been stuck on a task for a while
    - could prompt users to "Check in on {user}" if they need help with their
      task
. be able to join a cooking group from the frontend if not already logged in
    - if not logged in:
        - provide minimal information to create an account
        - email, password
. let someone leave a cooking session
. allow anybody to allow anybody else to join the session with a qr code that
  they can navigate to from their tasks screen
.
. accept payments
    - https://django-payments.readthedocs.io/en/latest/
. be able to add/remove users from a cooking group
. ensure if a user is removed from a cooking group, their task(s) are able
  to be reassigned to other active users
. list users in a cooking group
. choose a recipe as a cooking group
. see which tasks each user has completed
. view ingredients list for a recipe
. standardize naming convention between group, session, cooking_session,
  cooking_group
    - I like session because a group can persist over more than a session
. allow users to create an account
. view an equipment list for a recipe
. use nginx and gunicorn for local hosting on a .local domain name
    - https://chatgpt.com/c/67f7d6d9-7194-8010-872f-86f0d544d607
! task will need another column other than id
    ! add a second recipe to the test database to start seeing this issue
    - task_no
    - for the absolute ordering of the recipe (and not relying on the ids for
      each task to have been created in the proper order of the steps in the
      recipe)
    ! will need to change how some things are ordered
! might want to create a different group for cooking groups, so I can
  associate a recipe or user_tasks with a group
    - I could do a many-to-one relationships between groups and recipes
        - One group has exactly one recipe
        - One recipe can be assigned to many groups
    - I could do a one-to-many relationship between groups and user_tasks
        - One group can have many user_tasks
        - One user_task has exactly one group
x handle user registration bugs (create tests)
    x log user in and redirect to home after account is created
    x be able to create multiple new users
    x see when an email or username is already taken
x be able to show users a qr code to join a cooking group
    - create qr code from
    - cache this view
x fix bug when user creates session, but all the user tasks have been
  completed
x joining a session when all the tasks have been assigned and/or completed
x figure out that flow to have a user with an account to scan a qr code, log
  in, and get redirected to the my tasks page
    - they will go to join page
    - they will be redirect to login
    - might want to set LOGIN_URL in settings to a custom view
        - then I can intercept it
        - and customize login page template
x be able to register a new user
    x create a view
    x create a template
        - email         (mandatory)
        - username      (optional)
        - first name    (mandatory)
        - last name     (optional)
x let someone mark their task as complete and get the next one
    ? would you like another task or to take a break? (requiring opting in
      will prevent the flow from being bogged down)
x be able to join a cooking group from the frontend if already logged in
    ? do they need to be already logged in or not?
        - yes
    x plan the frontend for right after having clicked creating a session
        - important data:
            - all users in the group
            - group name
            - the recipe
            - list the current user's current task
            - a link to show the join url or qr code
            ? a way to delete the group
    x ?does the user appear in the admin's group view right after the user
      clicks the link without having logged in and then logs in?
        . log in as admin
        . create session
        . look at users in session
        . go to join link in incognito tab
        . log in as regular user
        . refresh admin view
        . see if regular user is in the group
        ! no!
    x be able to see each person's tasks
    x redirect from joining a session to go right to the person's tasks
    x plan a test for this flow:
        x setup:
            x have an admin
            x have a user
            x have a recipe
            x the admin calls the endpoint to create a session for the recipe
            x the admin gets the group back
            x the admin gets the join url
            x the admin is in the group
            x the user is not in the group
            x the user goes to the join url
            x the user is in the group
            x the admin has their first task
            - the user has their first task
    - the url has the group id and eventually ideally some confirmation code
    - if logged in:
        - get the user id from the request
            - join-cooking-group/<group_id>/
        - get the group id from the join url
        - join the group automatically
        - assign the user their first task
        - show the user their task screen
x create second nonadmin user to test in browser
x get recipe from group_id for join_cooking_session_view
    -
x include tests about the view
x create a cooking group from the frontend
    x make sure duplicate usertasks aren't created duplicate
        - unique_together (user, group, task_id)
x create a cooking session/group
    - a "cooking group" is the group of people that are making the same
      recipe at the same time
    x add group field to UserTasks (maybe rename to GroupTasks or
      UserGroupTasks)
    - each group has a full list of tasks in that table
    - only one person within each group can be assigned one task
    - the same user can be assigned that task as part of different recipes
    - one user can be part of multiple cooking groups
    - each cooking group needs an id
    - cooking group may be the wrong term, it could also be
x create a recipe detail page where you can see all the steps
x expose the app on a local network
    . run `ifconfig`
        - look for 192.168.... in eth0 or wlan0
    . python manage.py runserver 0.0.0.0:8000
    . possibly add the IP found from `ifconfig` to ALLOWED_HOSTS in
      settings.py
x click on a recipe and see the steps
. do the simplest prototype (relate each task to a scenario)
    x populate test data with initial state of a recipe ready to start cooking
        - I'm a user and I want to see which tasks I have to complete
    x add a screen for a user to see their assigned tasks
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
x keep going with tasks
    ~ make a custom user model
    x be able to see all the tasks associated with a recipe
    x create user_tasks table
    x assign tasks to users
. model recipes as DAGs (topological sort)
    - https://philuvarov.io/python-top-sort/
