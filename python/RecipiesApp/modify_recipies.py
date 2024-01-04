import sqlite3

def modify_recipe(recipe_title, new_ingredients, new_instructions):
    # Connect to the SQLite database
    connection = sqlite3.connect('recipes.db')
    recipe = connection.cursor()

    # Check if the recipe exists
    recipe.execute('SELECT id FROM recipes WHERE title = ?', (recipe_title,))
    recipe_id = recipe.fetchone()

    if recipe_id:
        # If the recipe exists, update it
        recipe.execute('''
            UPDATE recipes
            SET ingredients = ?, instructions = ?
            WHERE id = ?
        ''', (new_ingredients, new_instructions, recipe_id[0]))

        print(f'Recipe "{recipe_title}" modified successfully.')
        connection.commit()
    else:
        print(f'Recipe "{recipe_title}" not found.')

    # Close the connection
    connection.close()

# Example usage:
recipe_title_to_modify = "Pasta Carbonara"
new_ingredients = "Spaghetti, Eggs, Pancetta, Parmesan Cheese"
new_instructions = "Cook spaghetti; Mix eggs, cheese, and pancetta; Combine everything"
modify_recipe(recipe_title_to_modify, new_ingredients, new_instructions)
