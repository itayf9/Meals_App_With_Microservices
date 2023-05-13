from dish import Dish


class Dishes:
    def __init__(self):
        self.dishes = {}
        self.dish_counter = 1

    def add_dish(self, dish: Dish):
        self.dishes.update({dish.ID: dish})

    def convert_dictionary_to_array(self):
        dish_array_to_return = []

        for dish_id, dish_object in self.dishes.items():
            dish_array_to_return.append({"_id": dish_id, "dish": dish_object})

        return dish_array_to_return

    def create_new_dish_from_ninja(self, new_dish_name: str,  ninja_json: list):

        calories = 0
        sodium = 0
        sugar = 0
        size = 0

        for small_dish in ninja_json:
            calories+= small_dish["calories"]
            sodium +=small_dish["sodium_mg"]
            sugar +=small_dish["sugar_g"]
            size += small_dish["serving_size_g"]

        new_dish = Dish(new_dish_name, self.dish_counter, calories,size, sodium, sugar)

        self.dish_counter += 1
        return new_dish

    def remove_dish_by_id(self, dishID: int):
        self.dishes.pop(dishID)



all_dishes = Dishes()
