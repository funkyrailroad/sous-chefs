from django.contrib.auth import get_user_model
from my_app.tests import create_test_recipe

User = get_user_model()

# Admin user
user = User.objects.create_superuser(
    first_name="Admin",
    last_name="User",
    email="admin@example.com",
    password="mypassword",
)
user.save()

# Non-admin user
user = User.objects.create_user(
    first_name="Regular",
    last_name="User",
    email="user@example.com",
    password="mypassword",
)
user.save()


create_test_recipe()
