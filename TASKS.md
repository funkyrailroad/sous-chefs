. notes on first alpha session:
    - polish the product to avoid 80% of the criticisms people might have from
      first using it (or keep some in to be able to gauge if people are
      willing to critique even that)
    - make it as easy as possible to log in
    - make the opportunities to try it out with friends as easy as possible
      (minimal sign in)
        - email not necessary for starting
        - possibly just a name
        - default to the register page instead of sign in page
    - add some context in the beginning
        - explaining the purpose of the app
        - what the recipe will be
        - have some other
    - improve the formatting of the my tasks page
        - make tasks more obvious on first login (fred didn't realize it was a
          task)
        - increase spacing between tasks
        - make tasks bullet points (avoid it becoming a wall of text for long
          tasks)
    - as admin, be able to more easily see that overall task view
        - be able to navigate to it from the dropdown menu
        - be able to navigate to it from the my tasks page
        - be able to navigate to the my tasks page from the cooking session
          page
    - have a task detail page
        - see relevant ingredients and amounts for each task
        - be able to mark status as completed, blocked
    - be able to undo a "mark task as complete"
    - possible change the current task view to the "list my tasks" or "my task
      history" view
    - figure out what to do for blocking tasks (e.g. make a task unavailable
      for n minutes)
        - don't pass out tasks that may be blocked by something else
        - clustering tasks into lines to deal with dependencies
        - allow a user to mark a task as blocked and to specify which user's
          task is blocking it
            - my task is blocked!
            - which task is blocking it?
                - show the active tasks, and they can click the task that's
                  blocking it
                    - better than specifying a name, because people may have
                      switched phones (e.g. Fred and Anusha)
        -
x by default all endpoints must be admin
. usage notes:
    - get drinks/water
    - better distribute long running tasks
    - physical activity warning
    -
. keep thinking of these user scenarios:
    . turn these user scenarios into cucumber/gherkin
. connect the render instance to the postgres
    - be able to use sqlite locally and postgres in prod
. switch this over to use cookiecutter
/ define the user scenarios for the minimum prototype
    / I'm a user and I haven't chosen a recipe yet. I want to see a list of
      ingredients and amounts for each recipe
    . I'm a user and I'm working on a task. I want to know how much of each
      ingredient I should add
    . I'm a user and I can't complete my current task because it's blocked
        - e.g. I'm supposed to clean something, but it's not done being used
        . be able to skip a task,
            . possibly also identify who's task is blocking it
    - I'm a user and I want to update my user info
        . be able to update your user info (email, first_name, last_name,
          password)
    . I'm a user and I'm assigned a task, but I want to take a break and stop
      getting tasks assigned to me
    . I'm a user and I accidentally marked a task as complete, but I didn't
      actually finish it
        - could have an "Undo" button next to the "Mark as complete" button
            - unassigns the current task
            - deletes the current task from the user's my-task-view
                - (!might happen automatically)
            - reactivates the user's most recent task
            - remove strikethrough formatting from the user's my-task-view for that most
              recent task
                - (!might happen automatically)
    . I'm the host/admin and I want to change the status of a task
    x I'm the host and I want to see who is responsible for each task
    x I'm the host and I want to navigate to an existing cooking group I
      created
        - see my group in login page
        - My group
    x I'm a user and I want to see how I can complete my current task
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
    x Require opt in for every task assignment
    x I'm a user, I just completed a task. I should be prompted about if I
      want another task.
        ! could break up the logic in complete_user_task, complete is separate
        from assign.
        - in the template, if there are no active tasks, the user is prompted
          with "Click for your next task."
            - this button can call the get_new_task endpoint,

/ I'm a user and I haven't chosen a recipe yet. I want to see a list of
  ingredients and amounts for each recipe
    . create a separate table for ingredients
        - this can have the basic food items (name, maybe even some macro
          stuff)
    . create a separate table for recipe_ingredients
        - this can have a link to the ingredients table
        - it can also have some extra columns, e.g. the amount and unit (e.g.
          2 oz)
            - amount: float
            - unit: choice_field
. I'm a user and I'm working on a task. I want to know how much of each
  ingredient I should add
    - user_tasks might need a detail view
    - user_tasks could also have another column that references
      recipe_ingredient
    ! somewhere needs to be the servings multiplier
        - could be in the create a session
. fix bug where user clicks my cooking session without being in a group
    - options:
        - hide it from homepage
        - link to my-cooking-sessions
            - be able to select individual
. be able to skip a step if it's not ready yet
    - (e.g. can't start cooking pasta if the water isn't boiling yet)
. be able to undo a task that was marked as complete
    . release currently assigned task
    . go back to most recently completed task
    . probably have to adjust the ui too,
        - delete the current task
        -
. create a test for the whole qr-scan/register/my-tasks workflow
    - create a group
    - create an admin
    - as an unlogged in user, go to the join url
x figure out the flow of having an unlogged in user with an account scan a qr
  code, log in, and get redirected to the my tasks page
. the the user who's just been assigned a task know who the user was that had
  the previous task (in case they're related)
. only allow paying customers to create cooking sessions
    .
. fix bug when user clicks my tasks without having been assigned a group or
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
x figure out that flow to have a user without an account to scan a qr code,
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
x handle user registration bugs (create tests)
    x log user in and redirect to home after account is created
    x be able to create multiple new users
    x see when an email or username is already taken
x be able to show users a qr code to join a cooking group
    - create qr code from
    - cache this view
x change the flow to get to my-cooking-sessions
    x Add front page link to My cooking sessions
    x create list endpoint: my-cooking-sessions
        x all sessions that current user is a part of
    x create list-my-cooking-sessions.html
    x link to each individual cooking session page
    x detail endpoint my-cooking-sessions/<id>/
        x use the create-cooking-session template and name it
          my-cooking-session.html
    x the create_cooking_session_view should return the detail template
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
. host the project on my local network:
    - https://chatgpt.com/c/67f7d6d9-7194-8010-872f-86f0d544d607
    - find my local IP address with ifconfig
    - Look for something like inet 192.168.x.x under your active network
      adapter (often en0 or wlan0).
    - 192.168.178.94
