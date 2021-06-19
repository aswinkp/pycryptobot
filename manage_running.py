import json

class Running:

    def __init__(self, name):
        self.file_name = "running.json"
        self.name = name

    def get_data(self):
        with open(self.file_name) as f:
            data = json.load(f)
            f.close()
            return data

    def get_current_obj(self):
        data = self.get_data()
        running_crypto = data["names"][self.name]
        return running_crypto

    def get_quote(self):
        current_obj = self.get_current_obj()
        return current_obj['quote']

    def get_current_market(self):
        current_obj = self.get_current_obj()
        return current_obj['current_market']

    def set_current_market_for_name(self, running):
        data = self.get_data()
        data["names"][self.name]['current_market'] = running
        json.dump(data, open("running.json", "w"), indent=4)
