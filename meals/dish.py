
class Dish:
    def __init__(self, name: str, _id: int, cal: float, size: float, sodium: float, sugar: float):
        self.name = name
        self._id = _id
        self.ID = str(_id)
        self.cal = cal
        self.sodium = sodium
        self.size = size
        self.sugar = sugar

    def asdict(self):
        return {'name': self.name, '_id': self._id, 'ID': self.ID, 'cal': self.cal, 'sodium': self.sodium,
                'size': self.size, 'sugar': self.sugar}
