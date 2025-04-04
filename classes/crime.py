from user import User

class Crime:
    '''
    ...
    '''
    def __init__(self, applicant, applicant_number, location, date, description, files=None, weapon_type = None, victims = None, vict_info = None):
        self.applicant = applicant
        self.applicant_number = applicant_number
        self.location = location
        self.date = date
        self.description = description
        self.files = files
        self.weapon_type = weapon_type
        self.victims = victims
        self.vict_info = vict_info
        self.valid = False

    def __dict__(self):
        return dict(self)

    def change_valid(self):
        self.valid = True