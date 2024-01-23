MEAL_TYPES = ["Breakfast","Lunch","Dinner"]

class Recipe:
    def __init__(self, connection): 
        self.connection = connection
        
    
    def close_connection(self):
        self.connection.close()

    def read_recipes(self):
        recipe = self.connection.cursor()
        for i in MEAL_TYPES:       
            recipe.execute(f'SELECT * FROM recipes WHERE type == "{i}"')
            recipes = {} 
            recipes[i] = recipe.fetchall()
        for i in recipes:
            print(f'Title: {i[0]}')
            print(f'Ingredients: {i[3]}')
            print(f'Instructions: {i[4]}')
            print('---')
    
    def add_recipe(self):
        title = input("Title: ")
        meal_type = input("Meal Type: ")
        ingredients = input("Ingredients: ")
        instructions = input("Instructions: ")
        recipe = self.connection.cursor()
        recipe.execute('''
            INSERT INTO recipes (title, type, ingredients, instructions)
            VALUES (?, ?, ?, ?)
        ''', (title, meal_type, ingredients, instructions))
        self.connection.commit()
        print(f"Recipe for {title} have been added to database.")

    def remove_recipe(self, recipe_title):
        recipe = self.connection.cursor()
        recipe.execute('SELECT id FROM recipes WHERE title = ?', (recipe_title,))
        recipe_id = recipe.fetchone()
        if recipe_id:
            # If the recipe exists, delete it
            recipe.execute('DELETE FROM recipes WHERE id = ?', (recipe_id[0],))
            print(f'Recipe "{recipe_title}" removed successfully.')
            self.connection.commit()
        else:
            print(f'Recipe "{recipe_title}" not found.')

    def modify_recipe(self, recipe_title, new_ingredients, new_instructions):
        recipe = self.connection.cursor()
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
            self.connection.commit()
        else:
            print(f'Recipe "{recipe_title}" not found.')


