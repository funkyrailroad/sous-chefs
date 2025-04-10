from django.contrib.auth import get_user_model
from my_app.tests import create_test_recipe

User = get_user_model()

# Admin user
user = User.objects.create_superuser(
    username="myadmin",
    email="admin@example.com",
    password="mypassword",
)
user.save()

# Non-admin user
user = User.objects.create_user(
    username="myuser",
    email="user@example.com",
    password="mypassword",
)
user.save()


create_test_recipe()
