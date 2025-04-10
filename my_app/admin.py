from django.contrib import admin
from my_app.models import Recipe, Task, UserTask

# Register your models here.
admin.site.register(Recipe)
admin.site.register(Task)
admin.site.register(UserTask)
