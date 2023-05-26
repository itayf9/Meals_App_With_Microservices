# from flask.json import JSONEncoder


class Diet:
    def __init__(self, name: str, cal: float, sodium: float, sugar: float):
        self.name = name
        self.cal = cal
        self.sodium = sodium
        self.sugar = sugar

    def asdict(self):
        return {'name': self.name, 'cal': self.cal, 'sodium': self.sodium, 'sugar': self.sugar}



# class DishEncoder(JSONEncoder):
#     def default(self, o):
#         return o.__dict__

