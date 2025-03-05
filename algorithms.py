

class ParseFile:
    def __init__(self):
        self.recipe_txt_path = "recipes.txt"
        self.week_plan_path = "meal-plan.txt"

    '''
    DESCRIBE THE RULES FOR TEXT FILE
    '''
    def parse_recipe_text_file(self):
        with open(self.recipe_txt_path) as recipe_file:
            recipe_lines = [line.strip() for line in recipe_file]

        recipes = []
        recipe_start_index = 0

        '''
        The code above seperates the lines of the recipes.txt file
        into a list, then divides the list by each recipe. The recipes
        list is converted into a list of lists.
        '''
        for index, line in enumerate(recipe_lines):
            if line == "" and recipe_lines[index - 1] == "":
                recipes.append(recipe_lines[recipe_start_index:index - 1])
                recipe_start_index = index + 1
        
        if recipe_start_index < len(recipe_lines):
            recipes.append(recipe_lines[recipe_start_index:])

        '''Seperates the recipes list by recipe.'''
        recipes_data = {
            recipe[0].lower(): [recipe[1], recipe[3:]]
            for recipe in recipes
        }

        '''
        Iterates over every ingredient within the recipes list and
        seperates them by quantity, unit and name.
        '''
        for recipe_details in recipes_data.values():
            for index, ingredient in enumerate(recipe_details[1]):
                ingredient_quantity = ""
                ingredient_unit = ""
                ingredient_name = ""

                for char in ingredient:
                    if char.isnumeric() or char == ".":
                        ingredient_quantity += char

                    elif ingredient_unit.strip() in ['g', 'tbsp', 'ml', 'tsp', 'slices']:
                        ingredient_name += char

                    elif not ingredient_name:
                        ingredient_unit += char

                ingredient_quantity = float(ingredient_quantity)
                ingredient_unit = ingredient_unit.strip()
                ingredient_name = ingredient_name.strip()

                recipe_details[1][index] = [ingredient_quantity, ingredient_unit, ingredient_name] if ingredient_name else [ingredient_quantity, ingredient_name, ingredient_unit]

        # Data format: {Meal Name: [Portion, [[Ingredient amount, unit, name], [Ingredient amount, unit, name]]}
        return recipes_data

    def parse_meal_plan_text_file(self):
        with open(self.week_plan_path) as meal_plan_file:
            meal_plan_content = meal_plan_file.read().strip()

        weekly_meal_plan = {}

        '''
        Multiple nested for loops and if/else statements which
        convert the parsed data into a nested dictionary.
        '''
        for week_block in meal_plan_content.split('\n\n\n'):
            week_lines = week_block.replace(':', '').split('\n')
            week_name = week_lines[0]
            
            for day_meal_entry in week_lines[1:]:
                day_name, meals_string = day_meal_entry.split(" ", 1)
                meals = meals_string.split(" | ")

                if week_name not in weekly_meal_plan:
                    weekly_meal_plan[week_name] = {}

                if day_name not in weekly_meal_plan[week_name]:
                    weekly_meal_plan[week_name][day_name] = {}

                for meal in meals:
                    meal_name = meal.split()[0]
                    meal_details = meal[len(meal_name):].strip()

                    if meal_details[-2].isnumeric():
                        meal_portions = int(meal_details[-2])
                        meal_details = meal_details[:-3]

                    else:
                        meal_portions = 0

                    weekly_meal_plan[week_name][day_name][meal_name] = [meal_details, meal_portions]

        # Data format: {Week: {Day: {Breakfast: [Recipe, Portions], Lunch: [Recipe, Portions], Dinner: [Recipe, Portions]}}}
        return weekly_meal_plan

class FileManipulation:
    def __init__(self):
        self.recipe_txt_path = "recipes.txt"
        self.week_plan_path = "meal-plan.txt"
        self.shopping_list_path = "shopping-list.txt"

    def generate_weekly_meal_plan(self, week_number):
        return [
            [meal[0].lower(), meal[1]]
            for daily_plan in ParseFile().parse_meal_plan_text_file()[f'Week {week_number}'].values()
            for meal in daily_plan.values()
            if meal[0] not in ('N/A', 'Eating Out') and 'leftover' not in meal[0].lower()
            ]

    def write_shopping_list_text_file(self, ingredient_dict):
        with open(self.shopping_list_path, "w") as fw:
            for key, value in ingredient_dict.items():
                fw.write((f"{key}: {value[0]} {value[1]}\n"))

    def add_to_recipe_text_file(self, recipe_name, portions, ingredients):
        
        '''Forces all strings to be lower case'''
        recipe_name = recipe_name.lower()

        for ingredient in ingredients:
            ingredient[2] = ingredient[2].lower()

        recipe_data = ParseFile().parse_recipe_text_file()

        '''Appends the parameters to the dictionary.'''
        if portions == 1:
            recipe_data[recipe_name] = [f'{portions} portion', ingredients]
        else:
            recipe_data[recipe_name] = [f'{portions} portions', ingredients]

        '''
        Rewrites the updated dictionary into the text file
        according to all the rule specified in the comment before
        the 'parse_recipe_text_file' function.
        '''
        with open(self.recipe_txt_path, "w") as recipe_file:
            for meal_name, (portion, ingredients) in recipe_data.items():
                recipe_file.write(f"{meal_name}\n")

                recipe_file.write(f"{portion}\n")

                recipe_file.write("\n")

                for ingredient in ingredients:
                    quantity, unit, name = ingredient

                    if unit in ['g', 'ml']:
                        ingredient_line = f"{quantity}{unit} {name}"
                    elif unit:
                        ingredient_line = f"{quantity} {unit} {name}"
                    else:
                        ingredient_line = f"{quantity} {name}"

                    recipe_file.write(f"{ingredient_line.strip()}\n")

                recipe_file.write("\n\n")

    def delete_recipe_from_recipe_file(self, recipe_name):
        recipe_data = ParseFile().parse_recipe_text_file()

        '''Deletes the key-value pair from the dictionary.'''
        del recipe_data[recipe_name]
        with open(self.recipe_txt_path, "w") as recipe_file:
            for meal_name, (portion, ingredients) in recipe_data.items():
                recipe_file.write(f"{meal_name}\n")

                recipe_file.write(f"{portion}\n")

                recipe_file.write("\n")

                for ingredient in ingredients:
                    quantity, unit, name = ingredient

                    if unit in ['g', 'ml']:
                        ingredient_line = f"{quantity}{unit} {name}"
                    elif unit:
                        ingredient_line = f"{quantity} {unit} {name}"
                    else:
                        ingredient_line = f"{quantity} {name}"

                    recipe_file.write(f"{ingredient_line.strip()}\n")

                recipe_file.write("\n\n")