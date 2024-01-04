import sqlite3

def remove_recipe(recipe_title):
    # Connect to the SQLite database
    connection = sqlite3.connect('recipes.db')
    recipe = connection.cursor()

    # Check if the recipe exists
    recipe.execute('SELECT id FROM recipes WHERE title = ?', (recipe_title,))
    recipe_id = recipe.fetchone()

    if recipe_id:
        # If the recipe exists, delete it
        recipe.execute('DELETE FROM recipes WHERE id = ?', (recipe_id[0],))
        print(f'Recipe "{recipe_title}" removed successfully.')
        connection.commit()
    else:
        print(f'Recipe "{recipe_title}" not found.')

    # Close the connection
    connection.close()

# Example usage:
recipe_title_to_remove = "Pasta Carbonara"
remove_recipe(recipe_title_to_remove)