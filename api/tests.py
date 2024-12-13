from django.test import TestCase
from django.urls import reverse

from .models import Recipe, Task


"""
Tasks:
========
"get out all ingredients",
"get out cutting board and knife",
"get out pot",
"get out measuring cups and spoons",
"put pot on stove and turn heat to medium/low",
"chop onions",
"put oil in pot",
"put onions in oiled pot",
"stir onions & sautee for ~10 mninutes until golden",
"get out a bowl for the spices",
"measure out all the spices, put into a bowl",
"add spices to pot with sauteed onions and mix",
"dice/plane garlic",
"stir garlic into onions and sautee for ~2 minutes",
"measure out 2 cups vegetable broth (or make it from boullion)",
"get out can opener",
"open can of crushed tomatoes",
"add broth to pot",
"add water to pot",
"add tomatoes to pot",
"chop carrots",
"add carrots to pot",
"bring pot to a boil",
"reduce pot heat and keep at a simmer",
"add one cup of uncooked lentils to pot",
"open can of chickpeas and add to pot",
"get out wooden spoon",
"give pot a deep stir, scraping everything off the bottom with a wooden spoon",
"squeeze lemon juice onto stew",
"turn off heat",
"get out bowls",
"get out ladle for serving stew",
"get out yogurt and spoon",
"serve stew into bowls",
"distribute leftovers evenly into everybody's takehome containers",
"eat",
"everybody should bring all dirty dishes to near the sink",
"wash dishes for 5 minutes",
"dry dishes and put them away",


Ingredients:
============
"""


class IndexViewTests(TestCase):
    def setUp(self):
        self.tasks = [
            "get out all ingredients",
            "get out cutting board and knife",
            "get out pot",
            "get out measuring cups and spoons",
            "put pot on stove and turn heat to medium/low",
            "chop onions",
            "put oil in pot",
            "put onions in oiled pot",
            "stir onions & sautee for ~10 mninutes until golden",
            "get out a bowl for the spices",
            "measure out all the spices, put into a bowl",
            "add spices to pot with sauteed onions and mix",
            "dice/plane garlic",
            "stir garlic into onions and sautee for ~2 minutes",
            "measure out 2 cups vegetable broth (or make it from boullion)",
            "get out can opener",
            "open can of crushed tomatoes",
            "add broth to pot",
            "add water to pot",
            "add tomatoes to pot",
            "chop carrots",
            "add carrots to pot",
            "bring pot to a boil",
            "reduce pot heat and keep at a simmer",
            "add one cup of uncooked lentils to pot",
            "open can of chickpeas and add to pot",
            "get out wooden spoon",
            "give pot a deep stir, scraping everything off the bottom with a wooden spoon",
            "squeeze lemon juice onto stew",
            "turn off heat",
            "get out bowls",
            "get out ladle for serving stew",
            "get out yogurt and spoon",
            "serve stew into bowls",
            "distribute leftovers evenly into everybody's takehome containers",
            "eat",
            "everybody should bring all dirty dishes to near the sink",
            "wash dishes for 5 minutes",
            "dry dishes and put them away",
        ]

    def test_index_view(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello, world. You're at the polls index.")

    def test_create_recipe(self):
        obj = Recipe.objects.create(name="Lentil stew")
        recipe_id = obj.id

        task_objs = [Task(description=task, recipe_id=recipe_id) for task in self.tasks]
        Task.objects.bulk_create(task_objs)
        breakpoint()
