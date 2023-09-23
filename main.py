import json
from recipe_scrapers import scrape_me
import psycopg2
import requests
from bs4 import BeautifulSoup

import postgresconfig


class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect_to_database(self):
        try:
            self.connection = psycopg2.connect(
                database=postgresconfig.database,
                user=postgresconfig.user,
                password=postgresconfig.password,
                host=postgresconfig.host,
                port=postgresconfig.port,
            )
            self.cursor = self.connection.cursor()
            print("Connected to the database!")
        except psycopg2.Error as e:
            print("Error: Unable to connect to the database")
            print(e)

    def close_database_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Connection closed.")


class BBCGoodFoodScraper(DatabaseConnection):
    def __init__(self):
        super().__init__()

    def insert_category_links(self, categories):
        for category in categories:
            try:
                self.cursor.execute(
                    "INSERT INTO bbc_good_food_category_links (url) VALUES (%s)",
                    (category,),
                )
                self.connection.commit()
                print("Inserted category link:" + category)
            except Exception as e:
                self.connection.rollback()
                print(f"Error: {e}")

    def get_category_links(self, scraped=False):
        scraped_str = "true" if scraped else "false"
        self.cursor.execute(
            "SELECT id, url FROM bbc_good_food_category_links WHERE scraped = "
            + scraped_str
        )
        rows = self.cursor.fetchall()
        return rows

    def get_bbc_recipe_links_from_categories(self):
        category_links = self.get_category_links(True)

        if len(category_links) == 0:
            print("No category links found")
            return

        for id, category_url in category_links:
            page = 1
            hasLoadMoreButton = True

            while hasLoadMoreButton:
                response = requests.get(category_url + "?page=" + str(page))

                if response.status_code == 200:
                    html = response.text
                    soup = BeautifulSoup(html, "html.parser")

                    # find the load more button with data-gtm-class="list-page-see-more-button"
                    load_more_button = soup.find(
                        "a", {"data-gtm-class": "list-page-next"}
                    )

                    # find all the recipe list items as divs with class card__section card__media
                    recipe_list_items = soup.find_all(
                        "div", class_="card__section card__media"
                    )

                    for recipe_list_item in recipe_list_items:
                        recipe_link = (
                            "https://www.bbcgoodfood.com"
                            + recipe_list_item.find("a")["href"]
                        )
                        if "recipe" not in recipe_link:
                            continue

                        if "premium" in recipe_link:
                            continue

                        print(recipe_link)

                        try:
                            self.cursor.execute(
                                "INSERT INTO bbc_good_food_recipe_links (url) VALUES (%s)",
                                (recipe_link,),
                            )
                            self.connection.commit()
                        except Exception as e:
                            self.connection.rollback()
                            print(f"Error: {e}")

                    if load_more_button is None:
                        print("Error: Unable to find load more button", category_url)
                        hasLoadMoreButton = False
                        page = 1
                    else:
                        page += 1

                    # finish scraping this category set scraped to true
                    try:
                        self.cursor.execute(
                            "UPDATE bbc_good_food_category_links SET scraped = true WHERE id = %s",
                            (id,),
                        )
                        self.connection.commit()
                    except Exception as e:
                        self.connection.rollback()
                        print(f"Error: {e}")

                else:
                    print("Error: Unable to retrieve HTML", category_url)

    def get_bbc_full_recipes(self):
        self.cursor.execute(
            "SELECT id, url FROM bbc_good_food_recipe_links WHERE scraped = false"
        )
        rows = self.cursor.fetchall()

        if len(rows) == 0:
            print("No recipe links found")
            return

        for id, recipe_url in rows:
            # check if it already exists in the database
            self.cursor.execute(
                "SELECT id FROM recipes WHERE recipe_url = %s", (recipe_url,)
            )
            recipe_exists = self.cursor.fetchone()

            if recipe_exists:
                print("Recipe already exists in the database")
                continue

            scraper = scrape_me(recipe_url)

            # Initialize variables with default values
            recipe_name = "Unknown Recipe Name"
            recipe_image = "Image URL Not Available"
            recipe_ingredients = []
            recipe_instructions = "Instructions not found"
            recipe_total_time = "Total time not specified"
            recipe_servings = "Servings not specified"
            recipe_author = "Author not specified"
            recipe_description = "No Description Available"
            recipe_url = "URL not available"
            recipe_host = "Host not available"
            recipe_language = "Language not specified"
            recipe_nutrients = {}

            try:
                # get the recipe name
                recipe_name = scraper.title()

            except Exception as e:
                print(f"Error getting recipe name: {e}")

            try:
                # get the recipe image
                recipe_image = scraper.image()

            except Exception as e:
                print(f"Error getting recipe image: {e}")

            try:
                # get the recipe ingredients
                recipe_ingredients = (
                    scraper.ingredients() if scraper.ingredients() else []
                )

            except Exception as e:
                print(f"Error getting recipe ingredients: {e}")

            # Wrap the remaining data retrieval operations in similar try...except blocks

            # get the recipe instructions
            try:
                recipe_instructions = (
                    scraper.instructions()
                    if scraper.instructions()
                    else "Instructions not found"
                )
            except Exception as e:
                print(f"Error getting recipe instructions: {e}")

            # get the recipe total time
            try:
                recipe_total_time = (
                    scraper.total_time()
                    if scraper.total_time()
                    else "Total time not specified"
                )
            except Exception as e:
                print(f"Error getting total time: {e}")

            # get the recipe servings
            try:
                recipe_servings = (
                    scraper.yields() if scraper.yields() else "Servings not specified"
                )
            except Exception as e:
                print(f"Error getting servings: {e}")

            # get the recipe author
            try:
                recipe_author = (
                    scraper.author() if scraper.author() else "Author not specified"
                )
            except Exception as e:
                print(f"Error getting author: {e}")

            # get the recipe description
            try:
                recipe_description = (
                    scraper.description()
                    if scraper.description()
                    else "No Description Available"
                )
            except Exception as e:
                print(f"Error getting description: {e}")

            # get the recipe url
            try:
                recipe_url = scraper.url if scraper.url else "URL not available"
            except Exception as e:
                print(f"Error getting URL: {e}")

            # get the recipe host
            try:
                recipe_host = scraper.host() if scraper.host() else "Host not available"
            except Exception as e:
                print(f"Error getting host: {e}")

            # get the recipe language
            try:
                recipe_language = (
                    scraper.language()
                    if scraper.language()
                    else "Language not specified"
                )
            except Exception as e:
                print(f"Error getting language: {e}")

            # get the recipe nutrients
            try:
                recipe_nutrients = scraper.nutrients() if scraper.nutrients() else {}
            except Exception as e:
                print(f"Error getting nutrients: {e}")

            # At this point, all variables are populated with the data obtained or contain default values in case of errors

            try:
                insert_query = """
                INSERT INTO recipes (
                    recipe_name,
                    description,
                    ingredients,
                    instructions,
                    total_time,
                    servings,
                    author,
                    host,
                    recipe_language,
                    nutrition_data,
                    recipe_url,
                    image_url
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """

                # convert the nutrition / ingredients data to a JSONB string
                ingredients_data_json = json.dumps(recipe_ingredients)
                nutrition_data_json = json.dumps(recipe_nutrients)

                self.cursor.execute(
                    insert_query,
                    (
                        recipe_name,
                        recipe_description,
                        ingredients_data_json,
                        recipe_instructions,
                        recipe_total_time,
                        recipe_servings,
                        recipe_author,
                        recipe_host,
                        recipe_language,
                        nutrition_data_json,
                        recipe_url,
                        recipe_image,
                    ),
                )
                self.connection.commit()
                print("Inserted recipe: " + recipe_name)
            except Exception as e:
                self.connection.rollback()
                print(f"Error: {e}")

    def get_random_recipe(self):
        try:
            self.cursor.execute("SELECT * FROM recipes ORDER BY RANDOM() LIMIT 1")
            rows = self.cursor.fetchall()
            return rows
        except Exception as e:
            print(f"Error: {e}")

    def categories_recipes(self):
        self.cursor.execute(
            "SELECT id, recipe_name, description FROM recipes ORDER BY id ASC LIMIT 10 OFFSET 60"
        )
        rows = self.cursor.fetchall()

        if len(rows) == 0:
            print("No recipe links found")
            return

        for id, recipe_name, description in rows:
            print(
                "ID: "
                + str(id)
                + " Name: "
                + recipe_name
                + " Description: "
                + description
            )


if __name__ == "__main__":
    scraper = BBCGoodFoodScraper()
    scraper.connect_to_database()
    # scraper.get_bbc_recipe_links_from_categories()
    # scraper.get_bbc_full_recipes()
    # print(scraper.get_random_recipe())

    scraper.categories_recipes()

    scraper.close_database_connection()
