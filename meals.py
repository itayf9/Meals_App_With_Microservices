from meal import Meal


class Meals:
    def __init__(self):
        self.meals = []
        self.meal_counter = 1

    def add_meal(self, meal: Meal):
        self.meals.append(meal)

    def remove_meal(self, meal: Meal):
        self.meals.remove(meal)
