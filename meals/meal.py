# from flask.json import JSONEncoder
from dishes import all_dishes

class Meal:
    def __init__(self, name: str, _id: int, appetizer: int, main: int, dessert: int, cal: int, sodium: int, sugar: int):
        self.name = name
        self._id = _id
        self.ID = str(_id)
        self.appetizer = appetizer
        self.main = main
        self.dessert = dessert
        self.cal = cal
        self.sodium = sodium
        self.sugar = sugar

    def update_meal(self, new_meal_name: str, new_meal_appetizer_id: int, new_meal_main_id: int, new_meal_dessert_id: int):

        # replaces name, appetizer, main, dessert with new values, if changed any
        if self.name != new_meal_name:
            self.name = new_meal_name

        if self.appetizer != new_meal_appetizer_id:
            self.appetizer = new_meal_appetizer_id

        if self.main != new_meal_main_id:
            self.main = new_meal_main_id

        if self.dessert != new_meal_dessert_id:
            self.dessert = new_meal_dessert_id

        # fetched the appetizer, main, dessert dishes
        new_appetizer_dish = all_dishes.dishes.get(new_meal_appetizer_id)
        new_main_dish = all_dishes.dishes.get(new_meal_main_id)
        new_dessert_dish = all_dishes.dishes.get(new_meal_dessert_id)

        # updates the calories, sodium, sugar values
        self.cal = new_appetizer_dish.cal + new_main_dish.cal + new_dessert_dish.cal
        self.sodium = new_appetizer_dish.sodium + new_main_dish.sodium + new_dessert_dish.sodium
        self.sugar = new_appetizer_dish.sugar + new_main_dish.sugar + new_dessert_dish.sugar


    def asdict(self):
        return {'name': self.name, '_id': self._id, 'ID': self.ID,
                'appetizer': self.appetizer, 'main': self.main, 'dessert': self.dessert,
                'cal': self.cal, 'sodium': self.sodium, 'sugar': self.sugar}

# class MealEncoder(JSONEncoder):
#     def default(self, o):
#         return o.__dict__
