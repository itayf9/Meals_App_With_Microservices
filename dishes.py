from dish import Dish


class Dishes:
    def __init__(self):
        self.dishes = []
        self.dish_counter = 1

    def add_dish(self, dish: Dish):
        self.dishes.append(dish)

    def create_new_dish_from_ninja(self, ninja_json: dict):
        print(type(ninja_json))
        new_dish = Dish(ninja_json["name"], self.dish_counter, ninja_json["calories"],
                        ninja_json["serving_size_g"], ninja_json["sodium_mg"],
                        ninja_json["sugar_g"])


        self.dish_counter += 1
        return new_dish

    def remove_dish(self, dish: Dish):
        self.dishes.remove(dish)
