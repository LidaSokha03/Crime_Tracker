class Filter:
    def __init__(self, location=None, date=None, weapon=None, victims=None, type=None):
        self.location = location
        self.date = date
        self.weapon = weapon
        self.victims = victims
        self.type = type
        self.__dict = {'location': self.location,
                    'date': self.date,
                    'weapon': self.weapon,
                    'victims': self.victims,
                    'type': self.type}

    @property
    def filters(self):
        for val in self.__dict.values():
            if val:
                return self.__dict
        return {}
