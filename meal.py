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

