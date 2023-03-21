from flask.json import JSONEncoder


class Dish:
    def __init__(self, name: str, ID: int, cal: float, size: float, sodium: float, sugar: float):
        self.name = name
        self.ID = ID
        self.cal = cal
        self.sodium = sodium
        self.size = size
        self.sugar = sugar

    # def drive(self):
    #     print(f"The {self.year} {self.make} {self.model} is driving.")


class DishEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

#
# my_car = Car("Honda", "Civic", 2022)
# my_car.drive()  # Output: The 2022 Honda Civic is driving.
