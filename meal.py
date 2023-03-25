from flask.json import JSONEncoder
class Meal:
    def __init__(self, name: str, ID: int,appetizer: int, main: int,dessert: int,cal: int,sodium: int,sugar: int) :
        self.name = name
        self.ID = ID
        self.appetizer = appetizer
        self.main = main
        self.dessert = dessert
        self.cal = cal
        self.sodium = sodium
        self.sugar = sugar

    def asdict(self):
        return {'name': self.name, 'ID': self.ID,
                'appetizer': self.appetizer, 'main': self.main, 'dessert': self.dessert,
                'cal': self.cal, 'sodium': self.sodium, 'sugar': self.sugar}

class MealEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
