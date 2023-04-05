import json
from dataclasses import dataclass


with open('nintendo/countries.json') as file:
    COUNTRIES = json.load(file)


@dataclass
class Birthdate:
    year: int
    month: int
    day: int

    def __str__(self):
        return f'{self.day}-{self.month}-{self.year}'


@dataclass
class Profile:
    obfuscated_id: str
    nickname: str
    birthdate: Birthdate
    country_id: int
    gender: str
    is2fa_enabled: bool

    @property
    def country_code(self):
        return COUNTRIES[str(self.country_id)]