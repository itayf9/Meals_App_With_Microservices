from pymongo.collection import Collection

from dishes import all_dishes
from meal import Meal
from dish import Dish


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

    def remove_meal_by_id(self, meal_id: int):
        self.meals.pop(meal_id)

    def remove_the_deleted_dish_from_all_meals_that_contains_it(self, id_of_dish_to_remove: int, dish_to_remove: Dish,
                                                                meals_collection: Collection):
        for key, value in self.meals.items():
            if value.appetizer == id_of_dish_to_remove:
                value.appetizer = None
                self.remove_cal_sodium_sugar_from_meal(value, dish_to_remove.cal, dish_to_remove.sodium,
                                                       dish_to_remove.sugar)
            if value.main == id_of_dish_to_remove:
                value.main = None
                self.remove_cal_sodium_sugar_from_meal(value, dish_to_remove.cal, dish_to_remove.sodium,
                                                       dish_to_remove.sugar)
            if value.dessert == id_of_dish_to_remove:
                value.dessert = None
                self.remove_cal_sodium_sugar_from_meal(value, dish_to_remove.cal, dish_to_remove.sodium,
                                                       dish_to_remove.sugar)

            meals_collection.update_one({"_id": key}, {"$set": {"appetizer": value.appetizer,
                                                                "main": value.main,
                                                                "dessert": value.dessert,
                                                                "cal": value.cal,
                                                                "sodium": value.sodium,
                                                                "sugar": value.sugar}})

    def remove_cal_sodium_sugar_from_meal(self, meal: Meal, cal: float, sodium: float, sugar: float):
        """
        updates a specific Meal object to have less cal, sodium and sugar.
        :param meal: the Meal object to update
        :param cal: the cal value to remove
        :param sodium: the sodium value to remove
        :param sugar: the sugar value to remove
        """
        meal.cal -= cal
        meal.sodium -= sodium
        meal.sugar -= sugar


all_meals = Meals()
