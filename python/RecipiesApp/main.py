import sqlite3
from recipie import Recipe

t = Recipe(connection=sqlite3.connect('recipes.db'))
user_input = input("What would you like to do? ").lower()
if user_input == "read":
    t.read_recipes()
if user_input == "remove":
    t.remove_recipe("Pasta Carbonara")
if user_input == "add":
    title = 'Pasta Carbonara' 
    meal_type = 'Lunch'
    ingredients = 'Spaghetti, Eggs, Guanciale , Parmesan Cheese'
    instructions = 'Cook spaghetti; Combine everything'
    t.add_recipe(title, meal_type, ingredients, instructions)
if user_input == "modify":
    recipe_title_to_modify = "Pasta Carbonara"
    new_ingredients = "Spaghetti, Eggs, Pancetta, Parmesan Cheese"
    new_instructions = "Cook spaghetti; Mix eggs, cheese, and pancetta; Combine everything"
    t.modify_recipe(recipe_title_to_modify,new_ingredients,new_instructions)
t.close_connection()
