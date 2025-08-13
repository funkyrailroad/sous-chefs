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

test_recipe = {
    "name": "Lentil stew",
    "tasks": [
        "get out all ingredients",
        "get out cutting board and knife",
        "get out pot",
        "get out measuring cups and spoons",
        "put pot on stove and turn heat to medium/low",
        "chop onions",
        "put oil in pot",
        "put onions in oiled pot",
        "stir onions & sautee for ~10 minutes until golden",
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
        "get out bowls to eat from",
        "get out ladle for serving stew",
        "get out yogurt and spoon",
        "serve stew into bowls with ladle",
        "distribute leftovers evenly into everybody's takehome containers",
        "eat",
        "everybody should bring all dirty dishes to near the sink",
        "wash dishes for 5 minutes",
        "dry dishes and put them away",
    ],
}

test_recipe_2 = {
    "name": "Bratwurst with pesto pasta, greek salad and fruit",
    "tasks": [
        "get out pot for cooking pasta, fill it with water, and start boiling the water",                       # 1a takes time
        "fry bratwurst in a pan on medium heat until golden brown",                                             # 2a takes time
        "start playing some music, ask everybody for one or two songs to add to the queue, and add them",       # fun-a
        "Get out a serving bowl for the salad and tell others this is the salad bowl",                          # 3a
        "get bell peppers, rinse, remove seeds, slice into squares and put into salad bowl",                    # 3b
        "Get cucumbers, rinse, slice into bite-size pieces and put into salad bowl",                            # 3c
        "Get tomatoes, rinse, slice into bite-size pieces and put into salad bowl",                             # 3d
        "Get red onion, rinse, slice into thin rings and put into salad bowl",                                  # 3e
        "Add pasta to boiling water for proper duration and strain it when done",                               # 1b takes time
        "Slice fried bratwurst and continue frying until the ends are also browned, then turn off the heat",    # 2b takes time
        "Get out a serving bowl for the pasta, add the cooked pasta and mix in the pesto",                      # 1c
        "Add the fried bratwurst slices to the mixed pesto pasta and mix well",                                 # 2c
        "wash the pan that was used to cook the bratwurst",                                                     # 2d
        "Coursely chop olives and put into salad bowl",                                                         # 3f
        "Crumble feta cheese and put into salad bowl",                                                          # 3g
        "Get garlic and dice it for the salad dressing, put near the salad bowl",                               # 3h
        "Ask everybody for one or two songs to add to the music queue, and add them all to the queue",          # fun-b
        "Make the salad dressing in a small bowl, whisk together olive oil, lemon juice, oregano, salt, pepper and garlic to taste.",  # 3i
        "Get out a serving bowl/platter for the fruits",                                                        # 4a
        "wash the pot that was used to cook the pasta",                                                         # 1d
        "do 10 pushups",                                                                                        # fun-c
        "do 10 pushups",                                                                                        # fun-c
        "Cut up the first of the fruits into bite-sized pieces and put into serving bowl",                      # 4b
        "do 10 pushups",                                                                                        # fun-c
        "do 10 pushups",                                                                                        # fun-c
        "Cut up the second of the fruits into bite-sized pieces and put into serving bowl",                     # 4c
        "Have everybody taste the salad dressing to see how it can be improved, and make the improvements",     # 3j
        "do 10 pushups",                                                                                        # fun-c
        "do 10 pushups",                                                                                        # fun-c
        "Add the finished salad dressing to the salad bowl and mix well",                                       # 3k
        "Cut up the third of the fruits into bite-sized pieces and put into serving bowl",                      # 4d
        "Put the bowl/platter of cut fruit into the fridge to keep cool",                                       # 4e
        "set the table with plates",                                                                            # 5a
        "set the table with forks and knives",                                                                  # 5b
        "set the table with glasses",                                                                           # 5c
        "Put the finished pesto pasta w/ bratwurst serving bowl/platter on the table",                          # 5d
        "Put the finished salad bowl on the table",                                                             # 5e
        "go sit at the table (don't mark this task as complete)",
        "go sit at the table (don't mark this task as complete)",
        "go sit at the table (don't mark this task as complete)",
        "go sit at the table (don't mark this task as complete)",
        "go sit at the table (don't mark this task as complete)",
        "go sit at the table (don't mark this task as complete)",
        "go sit at the table (don't mark this task as complete)",
        "go sit at the table (don't mark this task as complete)",
        "go sit at the table (don't mark this task as complete)",
        "go sit at the table (don't mark this task as complete)",
    ],
}

"""
Bratwurst with pesto pasta, greek salad and fruit

- get out pot for cooking pasta, fill it with water, and start boiling the
  water
- boil and strain pasta
- start playing some music and add some songs to the queue
- fry bratwurst in a pan on medium heat until golden brown
- slice fried bratwurst and continue frying until the ends are also browned,
  then turn off the heat
- get out ingredients for salad
- wash the pan that was used to cook the bratwurst
- get out a bowl for the salad
- rinse vegetables for salad
- ask everybody for at least one song to add to the queue, and add them all to
  the queue
- get bell peppers, remove seeds, slice into squares and put into salad bowl
- slice cucumbers into bite-size and put into salad bowl
- slice tomatoes into bite-size and put into salad bowl
- slice red onion into thin rings and put into salad bowl
- coursely chop olives and put into salad bowl
- crumble feta cheese and put into salad bowl
- Make the dressing in a small bowl, whisk together olive oil, lemon juice,
  oregano, salt, and pepper to taste.
- add the dressing to the salad bowl and mix well
- get out a serving bowl/platter for the fruits
- cut up the first of the fruits into bite-size pieces and put into serving
  bowl
- cut up the second of the fruits into bite-size pieces and put into serving
  bowl
- cut up the third of the fruits into bite-size pieces and put into serving
  bowl
- put the bowl/platter of fruit into the fridge to keep cool
- set the table with plates, cutlery, and glasses




Ingredients:
===================
- entree
    - penne pasta
    - bratwurst
    - green pesto
- greek salad
    - cucumber
    - tomato
    - bell peppers
    - red onion
    - olives
    - feta cheese
- greek salad dressing
    - olive oil
    - lemon juice
    - oregano
    - salt
    - pepper
    - garlic
- dessert
    - three different fruits
    - apples
    - oranges
    - peaches
"""
