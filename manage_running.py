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

    def put_data(self, data):
        json.dump(data, open("running.json", "w"), indent=4)

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

    def set_current_market_for_name(self, current_market):
        from models.config import binanceParseMarket
        data = self.get_data()
        data["names"][self.name]['current_market'] = current_market
        market, base_currency, quote_currency = binanceParseMarket(current_market)
        data["names"][self.name]['base'] = base_currency
        data["names"][self.name]['should_sell'] = False
        self.put_data(data)

    def update_current_market(self, **kwargs):
        # current_margin, buy_price, current_price, sarima_1, sarima_3
        obj = self.get_current_obj()
        obj['current_margin'] = kwargs['current_margin']
        obj['buy_price'] = kwargs['buy_price']
        obj['current_price'] = kwargs['current_price']
        obj['last_buy_high'] = kwargs['last_buy_high']
        obj['last_buy_low'] = kwargs['last_buy_low']
        obj['sarima_3_margin'] = kwargs['sarima_3_margin']
        obj['sarima_1_margin'] = kwargs['sarima_1_margin']
        data = self.get_data()
        data["names"][self.name] = obj
        self.put_data(data)


    def remove_current_market_for_name(self):
        current_obj = self.get_current_obj()
        data = self.get_data()
        data["names"][self.name] = {
            'quote':  current_obj['quote'],
            'current_market': None
        }
        self.put_data(data)

    def is_base_currently_running(self, coin_pair):
        from models.config import binanceParseMarket
        market, base_currency, quote_currency = binanceParseMarket(coin_pair)
        data = self.get_data()
        for k,running_obj in data['names'].items():
            if 'base' in running_obj and running_obj["base"] == base_currency:
                return True
        return False

    def should_sell_current(self):
        current_obj = self.get_current_obj()
        if 'should_sell' in current_obj and current_obj['should_sell']:
            return True
        return False