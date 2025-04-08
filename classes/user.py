'''
class User
'''
import re

class User:
    '''
    ...
    '''
    def __init__(self, full_name, email, phone_number):
        self.full_name = full_name
        assert self.validate_name(), 'Некоректне імʼя'
        self.email = email.strip()
        assert self.validate_email(), 'Некоректний email'
        self.phone_number = phone_number.strip()
        assert self.validate_phone(), 'Некоректний номер телефону'
        self._password = None

    def validate_name(self):
        ''' validates name '''
        pattern = r'^(([A-ZА-Я][a-zа-я]{1,29})\s{0,})+$'
        return bool(re.match(pattern, self.full_name))

    def validate_email(self):
        ''' validates email '''
        pattern = r"^[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]{1,63}(?:\.[a-zA-Z0-9!\
#$%&'*+/=?^_`{|}~-]{1,63})*@[a-z0-9-]+(?:\.[a-z0-9-]+)*\.(com|org|edu|gov|net|ua)$"
        return bool(re.match(pattern, self.email))
    
    def validate_phone(self):
        ''' validates phone number '''
        pattern = r'^[0-9]{10}'
        return re.match(pattern, self.phone_number)
    
    def to_dict(self):
        return {
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone_number,
        }


class Lawyer(User):
    '''
    ...
    '''
    def __init__(self, full_name, email, phone_number, specialization, region, experience_years, position, qualification_document, submitter_type=None):
        super().__init__(full_name, email, phone_number)
        self.specialization = specialization
        self.region = region
        self.experience_years = experience_years
        assert int(experience_years) >= 0, 'Некоректна кількість років досвіду'
        self.position = position
        self.doc = qualification_document
        self.password = None
        self.submitter_type = submitter_type
    
    def to_dict(self):
        return {
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone_number,
            "specialization": self.specialization,
            "region": self.region,
            "experience_years": self.experience_years,
            "position": self.position,
            "qualification_document": self.doc,
            "submitter_type": self.submitter_type
        }



class Applicant(User):
    '''
    ...
    '''
    def __init__(self, full_name, email, location, phone_number, submitter_type, workplace = None):
        super().__init__(full_name, email, phone_number)
        self.location = location
        self.submitter_type = submitter_type
        self.workplace = workplace
        self.password = None

    def to_dict(self):
        return {
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone_number,
            "location": self.location,
            "submitter_type": self.submitter_type,
            "workplace": self.workplace
        }
