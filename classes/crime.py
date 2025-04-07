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

    def to_dict(self):
        return {
            'applicant': self.applicant,
            'applicant_number': self.applicant_number,
            'location': self.location,
            'date': self.date,
            'description': self.description,
            'files': self.files,
            'weapon_type': self.weapon_type,
            'victims': self.victims,
            'vict_info': self.vict_info
        }

    def change_valid(self):
        self.valid = True