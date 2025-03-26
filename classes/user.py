'''
class User
'''
import re
import bcrypt

class User:
    '''
    ...
    '''
    def __init__(self, name, surname, email, phone_number, password):
        self.name = name.strip()
        assert self.validate_name(), 'Некоректне імʼя'
        self.surname = surname.strip()
        assert self.validate_surname(), 'Некоректне прізвище'
        self.email = email.strip()
        assert self.validate_email(), 'Некоректний email'
        self.phone_number = phone_number.strip()
        assert self.validate_phone(), 'Некоректний номер телефону'
        assert len(password) >= 8, 'Пароль повинен містити не менше 8 символів'
        self.password = self.hash_password(password)

    def validate_name(self):
        ''' validates name '''
        pattern = r'^[A-ZА-Я][a-zа-я]{1,29}(-[A-ZА-Я][a-zа-я]{1,29}){0,3}$'
        return bool(re.match(pattern, self.name))

    def validate_surname(self):
        ''' validates surname '''
        pattern = r'^[A-ZА-Я][a-zа-я]{1,29}(-[A-ZА-Я][a-zа-я]{1,29}){0,3}$'
        return bool(re.match(pattern, self.surname))

    def validate_email(self):
        ''' validates email '''
        pattern = r"^[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]{1,63}(?:\.[a-zA-Z0-9!\
#$%&'*+/=?^_`{|}~-]{1,63})*@[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(com|org|edu|gov|net|ua)$"
        return bool(re.match(pattern, self.email))

    def validate_phone(self):
        ''' validates phone number '''
        pattern1 = r'^\+[0-9]{9,12}$'
        pattern2 = r'^\+[0-9]{2} \([0-9]{3}\) [0-9]{3}-[0-9]{2}-[0-9]{2}$'
        return bool(re.match(pattern1, self.phone_number) or re.match(pattern2, self.phone_number))

    def hash_password(self, password):
        ''' hashes password '''
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        return hashed.decode()



class Specialist(User):
    '''
    ...
    '''
    def __init__(self, name, surname, email, phone_number, password, specialisation, exp, workplace, position, document):
        super().__init__(name, surname, email, phone_number, password)
        self.specialisation = specialisation
        self.exp = exp
        self.workplace = workplace
        self.position = position
        self.doc = document


class Default(User):
    '''
    ...
    '''
    def __init__(self, name, surname, email, phone_number, password, location, type_of_feeder, workplace = None):
        super().__init__(name, surname, email, phone_number, password)
        self.location = location
        self.type_of_feeder = type_of_feeder
        self.workplace = workplace
