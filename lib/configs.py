import json
import requests
import base64


def load_configs():
    with open('data\\config.json', 'r') as f:
        return json.loads(f.read())


def save_configs(configs: dict):
    with open('data\\config.json', 'w') as f:
        f.write(json.dumps(configs))


class Pointers:
    file = 'data\\pointers.json'

    @staticmethod
    def get_pointers_online():
        response = requests.get('https://api.github.com/repos/xle00/pointers/contents/gifts.json')
        decoded = base64.b64decode(response.json()['content']).decode('utf-8')

        with open(Pointers.file, 'w') as f:
            f.write(decoded)

        return Pointers.get_pointers()

    @staticmethod
    def get_pointer_by_name(name):
        with open(Pointers.file, 'r') as f:
            module, base, offsets = json.loads(f.read())[name]
        base = int(base, 16)
        offsets = [int(i, 16) for i in offsets.split()]
        return module, base, offsets

    @staticmethod
    def save_pointers(name, values):
        with open(Pointers.file, 'r') as f:
            pointers = json.loads(f.read())

        pointers[name] = values

        with open(Pointers.file, 'w') as f:
            f.write(json.dumps(pointers))

    @staticmethod
    def get_pointers_offline():
        return Pointers.get_pointers()

    @staticmethod
    def get_pointers():
        with open(Pointers.file, 'r') as f:
            _json = json.loads(f.read())

        formatted = {}
        for name, items in _json.items():
            module, base, offsets = items
            base = int(base, 16)
            offsets = [int(i, 16) for i in offsets.split()]
            formatted.update({name: [module, base, *offsets]})
        return formatted
