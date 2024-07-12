from dataclasses import dataclass


@dataclass
class Settings:
    website_dict = {
        'google': "http://google.com",
    }
    file_save_path = ''
    http_handling_path = './http_handling_policies.json'
    disable_safety = True #disable https cert validation and safety warnings