import sqlite3
import math
import os

class DatabaseCreation:
    def __init__(self):
        self.db_path = "stock-up.db"

    def _connect_to_db(self):
        return sqlite3.connect(self.db_path)
    
    def initialize_db(self, recipe_txt_data):
        self._create_db_tables()
        print("INFO: Tables created.")

        self.recipe_txt_data = recipe_txt_data
        print("INFO: Text file parsed into variable.")

        self._populate_tables()
        print("INFO: Tables populated.")

        print("SUCCESS: Database has been fully initialized.")
        
    
    def _create_db_tables(self):
        with self._connect_to_db() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS ingredients (
                           ingredient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                           name TEXT NOT NULL UNIQUE,
                           inventory_quantity REAL NOT NULL,
                           inventory_unit TEXT,
                           price_per_unit REAL NOT NULL
                           )""")
            
            cursor.execute("""
                           CREATE TABLE IF NOT EXISTS recipes (
                           entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
                           meal_name TEXT NOT NULL,
                           portion_size INTEGER NOT NULL,
                           ingredient_quantity REAL NOT NULL,
                           ingredient_unit TEXT NOT NULL,
                           ingredient_id INTEGER,
                           FOREIGN KEY (ingredient_id) REFERENCES ingredients (ingredient_id)
                           )""")
        
    def _populate_tables(self):
        with self._connect_to_db() as connection:
            cursor = connection.cursor()

            '''
            Iterates over the recipe dictionary, inserting all listed
            ingredients without duplicates. Also maps the assigned ids
            of the ingredients to a mapping for the later recipe insertion
            loop.
            '''
            for meal_name, (portion_size, ingredient_list) in self.recipe_txt_data.items():
                for quantity, unit, ingredient_name in ingredient_list:
                    cursor.execute("""
                                   INSERT OR IGNORE INTO ingredients (name, inventory_quantity, inventory_unit, price_per_unit)
                                   VALUES (?, ?, ?, ?)
                                   """, (ingredient_name, 0, unit, 0))

                    cursor.execute("SELECT ingredient_id FROM ingredients WHERE name = ?", (ingredient_name,))

                    ingredient_id = cursor.fetchone()[0]

                    ingredient_id_mapping = {name: ingredient_id for name, ingredient_id in cursor.execute("SELECT name, ingredient_id FROM ingredients")}

            '''
            Checks if recipe is already in table, if not, the list of
            ingredients in each recipe is iterated over and inserted
            into a the recipe table, one entry = one ingredient.
            '''
            for meal_name, (portion_size, ingredient_list) in self.recipe_txt_data.items():
                cursor.execute("SELECT 1 FROM recipes WHERE meal_name = ?", (meal_name,))

                if cursor.fetchone():
                    continue

                for quantity, unit, ingredient_name in ingredient_list:
                    ingredient_id = ingredient_id_mapping[ingredient_name]
                    cursor.execute("""
                                   INSERT INTO recipes (meal_name, portion_size, ingredient_quantity, ingredient_unit, ingredient_id)
                                   VALUES (?, ?, ?, ?, ?)
                                   """, (meal_name, int(portion_size[0]), quantity, unit, ingredient_id))
                    

class DatabaseManipulation:
    def __init__(self):
        self.db_path = "stock-up.db"

    def _connect_to_db(self):
        return sqlite3.connect(self.db_path)

    # Fetches all ingredients in stock.
    def fetch_all_inventory_ingredients(self):
        with self._connect_to_db() as connection:
            cursor = connection.cursor()

            cursor.execute('SELECT name, inventory_quantity, inventory_unit FROM ingredients')
            
            inventory = [ingredient for ingredient in cursor.fetchall() if ingredient[1] != 0.0]

            return inventory
    
    # Fetches all ingredients in ingredients table.
    def fetch_all_ingredients(self):
        with self._connect_to_db() as connection:
            cursor = connection.cursor()

            cursor.execute('SELECT name, inventory_quantity, inventory_unit FROM ingredients')
            
            inventory = [ingredient for ingredient in cursor.fetchall()]

            return inventory

    def fetch_all_ingredients_for_meal_list(self, meal_list):
        ingredient_data = []
        ingredient_names = []
        ingredient_summary = {}

        with self._connect_to_db() as connection:
            cursor = connection.cursor()

            '''
            Fetches all ingredients used in the meals within the specified
            list of meals, using two sql queries. The first query gets all
            ingredient details and the second query gets the default portions
            per meal.
            '''
            for meal_details in meal_list:
                cursor.execute("""
                               SELECT recipes.ingredient_quantity, recipes.ingredient_unit, ingredients.name
                               FROM ingredients, recipes
                               WHERE recipes.meal_name = ? AND recipes.ingredient_id = ingredients.ingredient_id
                               """, (meal_details[0],))
                
                ingredient_list = cursor.fetchall()

                cursor.execute("""
                               SELECT portion_size
                               FROM recipes
                               WHERE recipes.meal_name = ?
                               """, (meal_details[0],))
                
                '''
                Iterates over the data fetched in the first query. Each iteration
                appends data to two lists which are later combined into a concise
                dictionary.
                '''
                for ingredient in ingredient_list:
                    ingredient_names.append(ingredient[2])
                    ingredient_data.append([ingredient[2], ingredient[0] * (meal_details[1] / cursor.fetchone()[0]), ingredient[1]])

            ingredient_names = list(set(ingredient_names))

            for name in ingredient_names:
                total_quantity = 0
                for record in ingredient_data:
                    if record[0] == name:
                        total_quantity += record[1]
                        unit = record[2]
                ingredient_summary[name] = [total_quantity, unit]

            ''' Dictionary of ingredients, keys are names and values are lists of quantity and unit'''
            return ingredient_summary

    def fetch_additional_ingredients_for_meal_list(self, meal_list):
        ingredient_summary = self.fetch_all_ingredients_for_meal_list(meal_list)

        inventory_ingredients = self.fetch_all_inventory_ingredients()

        ingredients_to_ignore = []

        '''
        Using a nested for loop, each index of the lists above are compared
        and when they match, the inventory quantities saved to the ingredient
        table are subtracted.
        '''
        for ingredient in ingredient_summary.items():
            for item in inventory_ingredients:
                if ingredient[0] == item[0]:
                    '''
                    If the required quantity of ingredients are already within the
                    inventory, the ingredient is removed from the dictionary
                    before it is returned.
                    '''
                    if (ingredient[1][0] - item[1]) > 0:
                        ingredient_summary[ingredient[0]] = [ingredient[1][0] - item[1], ingredient[1][1]]

                    else:
                        ingredients_to_ignore.append(ingredient[0])

        for key in ingredients_to_ignore:
            del ingredient_summary[key]

        return ingredient_summary

    def edit_ingredient_inventory_stock_level(self, ingredient, operator, quantity_change):
        with self._connect_to_db() as connection:
            cursor = connection.cursor()

            '''
            Fetches the quantity of the specified ingredient saved
            within the ingredients table.
            '''
            cursor.execute("""
                           SELECT inventory_quantity
                           FROM ingredients
                           WHERE name = ?
                           """, (ingredient,))
            
            ingredient_original_quantity = cursor.fetchall()[0][0]

            '''
            Depending on the declared operator during the function call,
            the stored inventory_quantity is increased or deducted by
            the specified amount.
            '''
            match operator:
                case '+':
                    cursor.execute("""
                                   UPDATE ingredients
                                   SET inventory_quantity = ?
                                   WHERE name = ?;
                                   """, ((ingredient_original_quantity + quantity_change), ingredient,))
                    
                    print(f"INFO: The {ingredient} stock level has been altered to {ingredient_original_quantity + quantity_change}.")

                case '-':
                    if (ingredient_original_quantity - quantity_change) >= 0:
                        cursor.execute("""
                                       UPDATE ingredients
                                       SET inventory_quantity = ?
                                       WHERE name = ?;
                                       """, ((ingredient_original_quantity - quantity_change), ingredient,))
                        
                        if ingredient_original_quantity - quantity_change == 0:
                            print(f"INFO: The {ingredient} stock level has been altered to {ingredient_original_quantity - quantity_change}. Consider restocking!")

                        else:
                            print(f"INFO: The {ingredient} stock level has been altered to {ingredient_original_quantity - quantity_change}")

                    else:
                        cursor.execute("""
                                       UPDATE ingredients
                                       SET inventory_quantity = ?
                                       WHERE name = ?;
                                       """, (0, ingredient,))
                        
                        print(f"INFO: You have attempted to remove stock that doesn't exist, however, the {ingredient} stock level has been altered to 0. Consider restocking!")

    
    def edit_ingredient_inventory_stock_level_per_recipe(self, operator, recipe_name, portions):

        '''
        By calling the 'fetch_all_ingredients_for_meal_list', the
        required ingredients are looped through and added to the
        stock by the 'edit_ingredient_inventory_stock_level' function.
        '''
        for ingredient, quantity in self.fetch_all_ingredients_for_meal_list([[recipe_name, portions]]).items():
            self.edit_ingredient_inventory_stock_level(ingredient, operator, quantity[0])

        if operator == '+':
            print(f"INFO: Ingredients for {recipe_name} have been added to inventory.")

        else:
            print(f"INFO: Ingredients for {recipe_name} have been subtracted from inventory.")

    def edit_ingredient_inventory_stock_level_per_weekly_shop(self, operator, dict):
        
        '''
        Simply iterates over the dictionary parameter to call the
        'edit_ingredient_inventory_stock_level' function for each
        ingredient.
        '''
        for ingredient, quantity in dict.items():
            self.edit_ingredient_inventory_stock_level(ingredient, operator, math.ceil(quantity[0]))

        if operator == '+':
            print(f"INFO: Weekly shop has been added to inventory.")

        else:
            print(f"INFO: Weekly shop has been subtracted from inventory.")

    def edit_ingredient_inventory_cost_per_unit(self, ingredient, cost):
        with self._connect_to_db() as connection:
            cursor = connection.cursor()
            cursor.execute("""
                           UPDATE ingredients
                           SET price_per_unit = ?
                           WHERE name = ?;
                           """, (cost, ingredient.lower().strip(),))
            
    def fetch_recipe_cost(self, recipe, recipe_txt_data):
        recipe = recipe.lower()

        ingredients_total_price = 0.0

        with self._connect_to_db() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                           SELECT portion_size
                           FROM recipes
                           WHERE meal_name = ?;
                           """, (recipe,))
            
            portions = cursor.fetchone()[0]

            for ingredient in recipe_txt_data[recipe][1]:
                    with self._connect_to_db() as connection:
                        cursor = connection.cursor()
                        cursor.execute("""
                                       SELECT price_per_unit
                                       FROM ingredients
                                       WHERE name = ?;
                                       """, (ingredient[2],))
                
                        PPU = cursor.fetchall()[0][0]

                    ingredients_total_price += ((ingredient[0] * PPU) / portions)
        
        return ingredients_total_price
    
    def delete_recipe(self, recipe):
        recipe = recipe.lower()

        with self._connect_to_db() as connection:
            cursor = connection.cursor()

            cursor.execute("""
                           DELETE FROM recipes
                           WHERE meal_name = ?
                           """, (recipe,))

    def reset_food_database(self, recipe_text_data):
        os.remove(self.db_path)
        DatabaseCreation().initialize_db(recipe_text_data)
        print(f"CRITICAL: Database has been reset.")