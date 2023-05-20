from dishes import all_dishes
from meal import Meal

class Meals:
    def __init__(self):
        self.meals = {}
        self.meal_counter = 1

    def add_meal(self, meal: Meal):
        self.meals.update({meal._id: meal})

    def create_new_meal_from_dishes(self, new_meal_name, new_meal_appetizer_id, new_meal_main_id, new_meal_dessert_id):
        # fetches the dishes from all dishes map

        appetizer = all_dishes.dishes.get(new_meal_appetizer_id)
        main = all_dishes.dishes.get(new_meal_main_id)
        dessert = all_dishes.dishes.get(new_meal_dessert_id)

        # calculates the calories, sodium and sugar of the meal
        cal = appetizer.cal + main.cal + dessert.cal
        sodium = appetizer.sodium + main.sodium + dessert.sodium
        sugar = appetizer.sugar + main.sugar + dessert.sugar

        new_meal = Meal(new_meal_name, self.meal_counter,
                        new_meal_appetizer_id, new_meal_main_id, new_meal_dessert_id,
                        cal, sodium, sugar)
        self.meal_counter += 1

        return new_meal

    def convert_dictionary_to_array(self):
        meal_array_to_return = []

        for meal_id, meal_object in self.meals.items():
            meal_array_to_return.append(meal_object.asdict())

        return meal_array_to_return

    def remove_meal_by_id(self, mealID: int):
        self.meals.pop(mealID)


all_meals = Meals()
