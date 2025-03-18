from user import User
class Crime:
    '''
    ...
    '''
    def __init__(self, applicant: User, date, description, files, weapon_type = None, victims = None, vict_info = None):
        self.applicant = applicant
        self.date = date
        self.description = description
        self.files = files
        self.weapon_type = weapon_type
        self.victims = victims
        self.vict_info = vict_info
