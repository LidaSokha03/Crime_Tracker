'''
class User
'''
class User:
    '''
    ...
    '''
    def __init__(self, name, surname, email, phone_number):
        self.name = name
        self.surname = surname
        self.email = email
        self.phone_number = phone_number

class Specialist(User):
    '''
    ...
    '''
    def __init__(self, name, surname, email, phone_number, specialisation, exp, workplace, position, document):
        super().__init__(name, surname, email, phone_number)
        self.specialisation = specialisation
        self.exp = exp
        self.workplace = workplace
        self.position = position
        self.doc = document


class Default(User):
    '''
    ...
    '''
    def __init__(self, name, surname, email, phone_number, location, type_of_feeder, workplace = None):
        super().__init__(name, surname, email, phone_number)
        self.location = location
        self.type_of_feeder = type_of_feeder
        self.workplace = workplace
