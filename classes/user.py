'''
class User
'''
class User:
    '''
    ...
    '''
    def __init__(self, full_name, email, phone_number):
        self.full_name = full_name
        self.email = email
        self.phone_number = phone_number
        self._password = None

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = password



class Lawyer(User):
    '''
    ...
    '''
    def __init__(self, full_name, email, phone_number, specialization, region, experience_years, position, qualification_document):
        super().__init__(full_name, email, phone_number)
        self.specialization = specialization
        self.region = region
        self.experience_years = experience_years
        self.position = position
        self.doc = qualification_document
        self.password = None
    
    def to_dict(self):
        return {
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone_number,
            "specialization": self.specialization,
            "region": self.region,
            "experience_years": self.experience_years,
            "position": self.position,
            "qualification_document": self.doc
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
