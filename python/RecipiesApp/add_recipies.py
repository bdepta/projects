import sqlite3

# Connect to or create a SQLite database file (e.g., recipes.db)
connection = sqlite3.connect('recipes.db')

# Create a cursor object to execute SQL queries
recipe = connection.cursor()

# Create a table to store recipes
recipe.execute('''
    CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        ingredients TEXT NOT NULL,
        instructions TEXT NOT NULL
    )
''')

# Insert a sample recipe into the table
recipe.execute('''
    INSERT INTO recipes (title, ingredients, instructions)
    VALUES (?, ?, ?)
''', ('Pasta Carbonara', 'Spaghetti, Eggs, Guanciale, Pecorino Cheese', 'Cook spaghetti; Mix eggs, cheese, and guanciale; Combine everything'))

# Commit the changes and close the connection
connection.commit()
connection.close()