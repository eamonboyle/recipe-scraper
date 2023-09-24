import psycopg2
from slugify import slugify

import postgresconfig

connection = psycopg2.connect(
    database=postgresconfig.database,
    user=postgresconfig.user,
    password=postgresconfig.password,
    host=postgresconfig.host,
    port=postgresconfig.port,
)
cursor = connection.cursor()
print("Connected to the database!")

# get all recipes
cursor.execute(
    "SELECT ID, recipe_name, description FROM recipes WHERE slug IS NULL ORDER BY id;"
)
recipes = cursor.fetchall()

# create a list of dictionaries
recipe_list = []
for recipe in recipes:
    recipe_dict = {"id": recipe[0], "name": recipe[1], "description": recipe[2]}
    recipe_list.append(recipe_dict)

# get all categories
cursor.execute("SELECT id, category FROM recipe_categories WHERE slug IS NULL;")

categories = cursor.fetchall()

# create a list of dictionaries
category_list = []
for category in categories:
    category_dict = {"id": str(category[0]), "name": category[1]}
    category_list.append(category_dict)

print("Recipes and categories fetched from the database!")

for category in category_list:
    print(slugify(category["name"]))

    # update the database with the slug
    cursor.execute(
        "UPDATE recipe_categories SET slug = %s WHERE id = %s;",
        (slugify(category["name"]), category["id"]),
    )

    connection.commit()

for recipe in recipe_list:
    print(slugify(recipe["name"]))

    # update the database with the slug
    cursor.execute(
        "UPDATE recipes SET slug = %s WHERE id = %s;",
        (slugify(recipe["name"]), recipe["id"]),
    )

    connection.commit()
