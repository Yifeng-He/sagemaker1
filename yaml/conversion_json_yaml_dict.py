"""
How to do conversion among:
1) python dict, 2) json str, 3) yaml str

refs:
online parser for yaml: http://yaml-online-parser.appspot.com/
lint check for yaml: http://www.yamllint.com/
lint check for json: https://jsonlint.com/
"""

import json
import yaml

dict_data ={
        'name': 'Kackson',
        'age': 20,
        'handles': {
                'facebook': 'Mike',
                'github': 'Ross',
                'youtube': 'Tom'
                },
        'languages': {
                'markup': ['HTML', 'XML', 'AIML'],
                'programming': ['c', 'c++', 'python', 'javascript']
                }
        }

# dict to json
str_json = json.dumps(dict_data, indent=True)
print(str_json)
# json string to dict
dict2 = json.loads(str_json)

# dict to yaml str
str_yaml = yaml.dump(dict2, default_flow_style=False)
print(str_yaml)

# yaml str to python dict
dict3 = yaml.load(str_yaml)
print(dict3)


