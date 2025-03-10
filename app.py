import os
from database import DatabaseCreation, DatabaseManipulation
from algorithms import ParseFile, FileManipulation

def user_input_for_menus(number_of_options):
    while True:
        try:
            num_input_by_user = int(input("\nEnter number here: "))
            if 0 < num_input_by_user <= number_of_options:
                return num_input_by_user
            
            else:
                print(f"Invalid Number! Valid numbers include: [1,..., {number_of_options}]")

        except:
            print(f"Invalid Input! This menu accepts ONLY numbers!")

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def start_program():
    if not os.path.isfile("stock-up.db"):
        DatabaseCreation().initialize_db(ParseFile().parse_recipe_text_file())

    navigate_main_menu()


def navigate_final_menu(previous_menu):
    print("\n-----------------")
    print("1: Previous Menu")
    print("2: Main Menu")

    match user_input_for_menus(2):
        case 1:
            previous_menu()

        case 2:
            navigate_main_menu()

def navigate_main_menu():
    clear_terminal()
    print("|-------- Main Menu --------|\n--Enter one of the following numbers to navigate the menus--\n")
    print("1: View Saved Data")
    print("2: Edit Saved Data")
    print("3: Generate Shopping List")
    print("4: Database Settings")

    match user_input_for_menus(4):
        case 1:
            navigate_view_data_menu()

        case 2:
            navigate_edit_data_menu()

        case 3:
            use_generate_shopping_list()

        case 4:
            navigate_database_settings_menu()

def navigate_view_data_menu():
    clear_terminal()
    print("|------ View Data Menu ------|\n--Enter one of the following numbers to navigate the menus--\n")
    print("1: View Weekly Meal Plan")
    print("2: View Recipe")
    print("3: View Inventory")
    print("4: Previous Menu")

    match user_input_for_menus(4):
        case 1:
            use_view_weekly_meal_plan()
                
        case 2:
            use_view_recipes()

        case 3:
            use_view_inventory()

        case 4:
            navigate_main_menu()

def navigate_edit_data_menu():
    clear_terminal()
    print("|------ Edit Data Menu ------|\n--Enter one of the following numbers to navigate the menus--\n")
    print("1: Recipes")
    print("2: Inventory")
    print("3: Previous Menu")

    match user_input_for_menus(3):
        case 1:
            navigate_edit_recipe_menu()

        case 2:
            navigate_edit_inventory_menu()

        case 3:
            navigate_main_menu()

def use_generate_shopping_list():
    clear_terminal()

    print("| Generate Shopping List Menu |\n-- Which week do you need a shopping list for? --\n")

    for index, week in enumerate(list(ParseFile().parse_meal_plan_text_file().keys())):
        print(f"{index + 1}: {week}")

        final_option_number = index + 2
    
    print(f"{final_option_number}: Previous Menu")

    selected_week = user_input_for_menus(final_option_number)

    if selected_week == final_option_number:
        navigate_main_menu()

    FileManipulation().write_shopping_list_text_file(DatabaseManipulation().fetch_additional_ingredients_for_meal_list(FileManipulation().generate_weekly_meal_plan(selected_week)))

    print(f"INFO: Shopping list for week {selected_week} has been sent to shopping-list.txt file!")
    
    navigate_final_menu(use_generate_shopping_list)

def use_view_weekly_meal_plan():
    clear_terminal()

    weekly_meal_plan = ParseFile().parse_meal_plan_text_file()

    print("| View Weekly Meal Plan Menu |\n-- Which week would you like to view? --\n")
    for index, week in enumerate(list(weekly_meal_plan.keys())):
        print(f"{index + 1}: {week}")

        final_option_number = index + 3

    print(f"{final_option_number - 1}: View All Weeks")

    print(f"{final_option_number}: Previous Menu")

    selected_week = user_input_for_menus(final_option_number)

    total_week_cost = 0

    clear_terminal()

    if 0 < selected_week <= len(weekly_meal_plan.keys()):
        print(f"\n|--- Meal plan for {list(weekly_meal_plan.keys())[selected_week - 1]} ---|\n")

        for day, day_meals in weekly_meal_plan[f"Week {selected_week}"].items():
            for mealTime, meal in day_meals.items():
                if meal[0] in ['N/A', 'Eating Out'] or 'Leftover' in meal[0]:
                    print(f"{day}: {mealTime} - {meal[0]}")

                else:
                    total_week_cost += DatabaseManipulation().fetch_recipe_cost(meal[0], ParseFile().parse_recipe_text_file()) * meal[1]
                    if meal[1] == 1:
                        print(f"{day}: {mealTime} - {meal[1]} portion of {meal[0]}")

                    else:
                        print(f"{day}: {mealTime} - {meal[1]} portions of {meal[0]}")

        print(f"INFO: This week costs £{round(total_week_cost / 100, 2)} with the saved portions and ingredient PPU!")

    elif selected_week == len(weekly_meal_plan.keys()) + 1:
        for week in weekly_meal_plan.keys():
            print(f"\n|--- Meal plan for {week} ---|\n")
                
            for day, day_meals in weekly_meal_plan[f"{week}"].items():
                for mealTime, meal in day_meals.items():
                    if meal[0] in ['N/A', 'Eating Out'] or 'Leftover' in meal[0]:
                        print(f"{day}: {mealTime} - {meal[0]}")

                    else:
                        total_week_cost += DatabaseManipulation().fetch_recipe_cost(meal[0], ParseFile().parse_recipe_text_file()) * meal[1]
                        print(f"{day}: {mealTime} - {meal[1]} portions of {meal[0]}")

            print(f"INFO: This week costs £{round(total_week_cost / 100, 2)} with the saved portions and ingredient PPU!")

    else:
        navigate_view_data_menu()

    navigate_final_menu(use_view_weekly_meal_plan)

def use_view_recipes():
    clear_terminal()

    recipes = ParseFile().parse_recipe_text_file()

    print("|----- View Recipe Menu -----|\n-- Which recipe do you need? --\n")

    for index, recipe in enumerate(list(recipes.keys())):
        print(f"{index + 1}: {recipe.capitalize()}")

        final_option_number = index + 2

    print(f"\n{final_option_number}: Previous Menu")

    selected_recipe = user_input_for_menus(final_option_number)

    if 0 < selected_recipe <= len(recipes.keys()):
        clear_terminal()

        print(f"\n{list(recipes.keys())[selected_recipe - 1].capitalize()}:\n")

        for ingredient_info in list(recipes.items())[selected_recipe - 1][1][1]:
            if ingredient_info[1] == "":
                print(f"{ingredient_info[0]} {ingredient_info[2]}")

            else:    
                print(f"{ingredient_info[0]}{ingredient_info[1]} of {ingredient_info[2]}")
        
        print(f"\nINFO: This recipe costs £{round(DatabaseManipulation().fetch_recipe_cost(list(recipes.keys())[selected_recipe - 1], ParseFile().parse_recipe_text_file()) / 100, 2)} per portion with the saved ingredient PPUs!")

        navigate_final_menu(use_view_recipes)

    else:
        navigate_view_data_menu()

def use_view_inventory():
    clear_terminal()
    print("|--- View Inventory Menu ---|\n")

    for ingredient in DatabaseManipulation().fetch_all_inventory_ingredients():
        if ingredient[2] in ['g', 'ml']:
            print(f"{ingredient[0].capitalize()} - {ingredient[1]}{ingredient[2]}")
        
        else:
            print(f"{ingredient[0].capitalize()} - {ingredient[1]} {ingredient[2]}")
    
    navigate_final_menu(navigate_view_data_menu)

def navigate_edit_recipe_menu():
    clear_terminal()
    print("|---- Edit Recipes Menu ----|\n-- How would you like to alter the recipe text file? --\n")
    print("1: Add Recipe")
    print("2: Remove Recipe")
    print("3: Previous Menu")

    match user_input_for_menus(3):
        case 1:
            edit_recipe_text_file('+')

        case 2:
            edit_recipe_text_file('-')

        case 3:
            navigate_edit_data_menu()

def edit_recipe_text_file(operator):
    clear_terminal()
    match operator:
        case '+':
            print("|---- Add Recipes Menu ----|\n")
            recipe_name = input("Enter the recipe name: ").strip()
            while True:
                try:
                    portions = int(input("How many portions does the recipe serve: "))
                    break
                
                except:
                    pass
                
            ingredients = []
            print("--- Your Ingredients ---\n")
            while True:
                try:
                    ingredient_name = input("Enter the name of the ingredient: ")
                    ingredient_quantity = float(input(f"Enter the quantity of {ingredient_name} needed: "))
                    ingredient_unit = input(f"Enter the unit used for {ingredient_name}: ")

                    ingredients.append([ingredient_quantity, ingredient_unit, ingredient_name])

                    new_ingredient = input("Press 'enter' to add another ingredient or type '#' and press 'enter' to finish: ")
                    if new_ingredient != "":
                        break
        
                except:
                    print(f"ERROR: An error has occured, ingredient addition has been cancelled")


            FileManipulation().add_to_recipe_text_file(recipe_name, portions, ingredients)

            print(f"\nINFO: {recipe_name} added to recipes text file!")

            DatabaseCreation().initialize_db()

        case '-':
            print("|--- Remove Recipes Menu ---|\n")
            recipes = ParseFile().parse_recipe_text_file()
            for index, recipe in enumerate(list(recipes.keys())):
                print(f"{index + 1}: {recipe}")

                final_option_number = index + 2

            print(f"\n{final_option_number}: Previous Menu")

            selected_recipe_index = user_input_for_menus(final_option_number)

            if selected_recipe_index == final_option_number:
                navigate_edit_recipe_menu()

            DatabaseManipulation().delete_recipe(list(recipes.keys())[selected_recipe_index - 1])
                
            FileManipulation().delete_recipe_from_recipe_file(list(recipes.keys())[selected_recipe_index - 1])
            
            print(f"\nINFO: {recipe_name} has been removed from the recipes text file & database!")

    navigate_final_menu(navigate_edit_recipe_menu)

def navigate_edit_inventory_menu():
    clear_terminal()
    print("|--- Edit Inventory Menu ---|\n")
    print("1: Add To Inventory")
    print("2: Remove From Inventory")
    print("3: Add Recipe To Inventory")
    print("4: Remove Recipe From Inventory")
    print("5: Add Week Recipes To Inventory")
    print("6: Remove Week Recipes From Inventory")
    print("7: Edit Ingredient PPU(Price Per Unit)")
    print("8: Previous Menu")

    match user_input_for_menus(8):
        case 1:
            use_edit_inventory('+')
        
        case 2:
            use_edit_inventory('-')

        case 3:
            use_edit_inventory_by_recipe('+')

        case 4:
            use_edit_inventory_by_recipe('-')

        case 5:
            use_edit_inventory_by_week('+')

        case 6:
            use_edit_inventory_by_week('-')

        case 7:
            use_edit_ingredient_price()

        case 8:
            navigate_edit_data_menu()

def use_edit_inventory(operator):
    clear_terminal()

    if operator == '+':
        print("|-- Add To Inventory Menu --|\n-- Which item would you like to adjust the stock level of? --\n")
        ingredient_list = DatabaseManipulation().fetch_all_ingredients()

    else:
        print("| Remove From Inventory Menu |\n-- Which item would you like to adjust the stock level of? --\n")
        ingredient_list = DatabaseManipulation().fetch_all_inventory_ingredients()
        if len(ingredient_list) == 0:
            print("Empty Inventory!")
            final_option_number = 1

    for index, ingredient in enumerate(ingredient_list):
        print(f"{index + 1}: {ingredient[0].capitalize()}")

        final_option_number = index + 2

    print(f"\n{final_option_number}: Previous Menu")

    selected_inventory_ingredient = user_input_for_menus(final_option_number)

    if selected_inventory_ingredient == final_option_number:
        navigate_edit_inventory_menu()

    ingredient_name = ingredient_list[selected_inventory_ingredient - 1][0]
    ingredient_unit = ingredient_list[selected_inventory_ingredient - 1][2]

    try:
        if operator == '+':
            ingredient_quantity_change = float(input(f"\nHow many {ingredient_unit} of {ingredient_name} would you like to add to the inventory: "))

            DatabaseManipulation().edit_ingredient_inventory_stock_level(ingredient_name, '+', ingredient_quantity_change)

            new_ingredient_quantity = list(DatabaseManipulation().fetch_all_ingredients())[selected_inventory_ingredient - 1][1]

        else:
            ingredient_quantity_change = float(input(f"\nHow many {ingredient_unit} of {ingredient_name} would you like to remove from the inventory: "))

            DatabaseManipulation().edit_ingredient_inventory_stock_level(ingredient_name, '-', ingredient_quantity_change)

            for ingredient in DatabaseManipulation().fetch_all_ingredients():
                if ingredient[0] == ingredient_name:
                    new_ingredient_quantity == ingredient[1]

        print(f"\nINFO: The stock level of {ingredient_name} is now {new_ingredient_quantity}!")

    except:
        pass

    navigate_final_menu(navigate_edit_inventory_menu)

def use_edit_inventory_by_recipe(operator):
    clear_terminal()

    recipes = ParseFile().parse_recipe_text_file()

    if operator == '+':
        print("|-- Add Recipe To Inventory Menu --|\n-- Which recipe would you like to adjust the stock level of? --\n")

    for index, recipe in enumerate(list(recipes.keys())):
        print(f"{index + 1}: {recipe.capitalize()}")

        final_option_number = index + 2

    print(f"\n{final_option_number}: Previous Menu")

    selected_recipe = user_input_for_menus(final_option_number)

    if 0 < selected_recipe <= len(recipes.keys()):
        recipe_name = list(recipes.keys())[selected_recipe - 1]
        portions = int(input(f"How many portions of {recipe_name} are you adjusting the inventory by: "))

        DatabaseManipulation().edit_ingredient_inventory_stock_level_per_recipe(operator, recipe_name, portions)

    else:
        navigate_view_data_menu()

    navigate_final_menu(navigate_edit_data_menu)

def use_edit_inventory_by_week(operator):
    clear_terminal()

    weekly_meal_plan = ParseFile().parse_meal_plan_text_file()

    if operator == '+':
        print("| Add Week To Inventory Menu |\n-- Which week would you like to add to the inventory? --\n")

    else:
        print("| Remove Week From Inventory Menu |\n-- Which week would you like to remove from the inventory? --\n")

    for index, week in enumerate(list(weekly_meal_plan.keys())):
        print(f"{index + 1}: {week}")

        final_option_number = index + 2

    print(f"{final_option_number}: Previous Menu")

    selected_week = user_input_for_menus(final_option_number)

    if 0 < selected_week <= len(weekly_meal_plan.keys()):
        DatabaseManipulation().edit_ingredient_inventory_stock_level_per_weekly_shop(operator, DatabaseManipulation().fetch_all_ingredients_for_meal_list(FileManipulation().generate_weekly_meal_plan(selected_week)))

        if operator == '+':
            print(f"INFO: Ingredients for all the recipes within week {selected_week} have been added to the inventory!")

        else:
            print(f"INFO: Ingredients for all the recipes within week {selected_week} have been removed from the inventory!")

    else:
        navigate_view_data_menu()

    navigate_final_menu(navigate_edit_inventory_menu)

def use_edit_ingredient_price():
    clear_terminal()

    print("|-- Edit Ingredient Price Menu --|\n-- Which item would you like to adjust the price of? --\n")
    ingredient_list = DatabaseManipulation().fetch_all_ingredients()

    for index, ingredient in enumerate(ingredient_list):
        print(f"{index + 1}: {ingredient[0].capitalize()}")

        final_option_number = index + 2

    print(f"\n{final_option_number}: Previous Menu")

    selected_inventory_ingredient = user_input_for_menus(final_option_number)

    ingredient_name = ingredient_list[selected_inventory_ingredient - 1][0]
    ingredient_unit = ingredient_list[selected_inventory_ingredient - 1][2]

    if selected_inventory_ingredient == final_option_number:
        navigate_edit_inventory_menu()

    while True:
        try:
            new_price = float(input(f"What is the price of 1 {ingredient_unit} of {ingredient_name} in pence: "))
            break

        except:
            pass

    DatabaseManipulation().edit_ingredient_inventory_cost_per_unit(ingredient_name, new_price)

    print(f"\nINFO: The price of 1 {ingredient_unit} of {ingredient_name} is set to {new_price}!")

    navigate_final_menu(navigate_edit_inventory_menu())

def navigate_database_settings_menu():
    clear_terminal()

    print("|--- Database Settings Menu ---|")
    print("1: Reset Database")
    print("2: Reset Recipes Text File")
    print("3: Reset All")
    print("4: Previous Menu")

    match user_input_for_menus(4):
        case 1:
            use_reset_database()

        case 2:
            use_view_recipes()

        case 3:
            use_reset_database()
            use_reset_recipes()

        case 4:
            navigate_main_menu()

def use_reset_database():
    clear_terminal()

    user_validation = input("CRITICAL: Are you sure you want to reset your entire database(you can not undo this action!) - type 'reset' to confirm: ")

    if user_validation == 'reset':
        DatabaseManipulation().reset_food_database(ParseFile().parse_recipe_text_file())
    
    else:
        print("INFO: Database reset has been aborted!")

    navigate_final_menu(navigate_database_settings_menu)

def use_reset_recipes():
    clear_terminal()

    user_validation = input("CRITICAL: Are you sure you want to reset your entire recipes text file(you can not undo this action!) - type 'reset' to confirm: ").strip()

    if user_validation == 'reset':
        with open("recipes.txt", 'w') as fw:
            fw.write("")
    
    else:
        print("INFO: Recipes text file reset has been aborted!")

    navigate_final_menu(navigate_database_settings_menu)

start_program()