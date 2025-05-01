from datetime import datetime
import re

class Crime:
    '''
    ...
    '''
    def __init__(self, applicant, applicant_number, region, location, date, description,
             files=None, weapon_type=None, victims=None, vict_info=None):
        self.applicant = applicant
        assert self.validate_applicant(), 'Некоректне ПІБ'
        self.applicant_number = applicant_number
        assert self.validate_phone(), 'Номер повинен складатись з 10 цифр (0123456789)'
        self.region = region
        self.location = location
        self.date = date
        self.description = description
        self.files = files
        self.weapon_type = weapon_type
        self.victims = victims
        assert self.validate_victims(), 'Відʼємна кількість жертв'
        self.vict_info = vict_info

    @property
    def date(self):
        return self._date
    @date.setter
    def date(self, value):
        self._date = datetime.strptime(value, "%Y-%m-%d")

    def to_dict(self):
        return {
            'applicant': self.applicant,
            'applicant_number': self.applicant_number,
            'location': self.location,
            'region': self.region,
            'date': self.date,
            'description': self.description,
            'files': self.files,
            'weapon_type': self.weapon_type,
            'victims': self.victims,
            'vict_info': self.vict_info
        }

    def validate_applicant(self):
        accepted = 'ЙЦУКЕНГШЩЗХЇФІВАПРОЛДЖЄЯЧСМИТЬБЮҐйцукенгшщзхїфівапролджєячесмитьбюґ -'
        name_ = self.applicant
        for char in name_:
            if char not in accepted:
                return False
        if len(self.applicant) < 3 or len(self.applicant) > 50:
            return False
        return True

    def validate_phone(self):
        ''' validates phone number '''
        pattern = r'^[0-9]{10}'
        return re.match(pattern, self.applicant_number)
    
    def validate_victims(self):
        if int(self.victims) < 0:
            return False
        return True
