import sqlite3
# Connect to the database
connection = sqlite3.connect('recipes.db')
recipe = connection.cursor()
# Retrieve all recipes from the table
recipe.execute('SELECT * FROM recipes')
recipes = recipe.fetchall()

# Print the recipes
for i in recipes:
    print(f'Title: {i[1]}')
    print(f'Ingredients: {i[2]}')
    print(f'Instructions: {i[3]}')
    print('---')

# Close the connection
connection.close()
