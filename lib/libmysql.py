class Database:
    def __init__(self, database):
        self.database = database

    def inaccounts(self, card):
        cursor = self.database.cursor()
        cursor.execute(f"select * from wallets where card='{card}'")
        result = cursor.fetchone()
        if result:
            return True
        else:
            return False

    def balance(self, card):
        if self.inaccounts(card):
            cursor = self.database.cursor()
            cursor.execute(f"select balance from wallets where card='{card}'")
            result = cursor.fetchone()
            return result[0]
        else:
            return 'E'
        
    def transfer(self, from_card, to_card, amount):
        from_balance = self.balance(from_card)
        to_balance = self.balance(to_card)
        if from_balance == 'E' or to_balance == 'E':
            return False
        if amount > from_balance:
            return False
        val = {'from' : (from_balance - amount), 'to': (to_balance + amount)}
        cursor = self.database.cursor()
        cursor.execute(f"update wallets set balance = {val['from']} " + 'where card="' + from_card + '"')
        cursor.execute(f"update wallets set balance = {val['to']} " + 'where card="' + to_card + '"')
        self.database.commit()
        return True

