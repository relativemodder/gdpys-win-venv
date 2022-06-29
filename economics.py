import time
from database import Database
import utils

class NoEnoughMoneyError(Exception):
    pass

def transfer_money(from_:int, to:int, amount:int):
    db = Database(assoc=True)
    user_from = utils.get_user_assoc(from_)
    user_to = utils.get_user_assoc(to)
    balance_from = user_from['diamonds']
    if balance_from < amount:
        raise NoEnoughMoneyError
    db.cursor.execute("UPDATE accounts SET diamonds = diamonds - %s WHERE ID = %s", (amount, from_))
    db.cursor.execute("UPDATE accounts SET diamonds = diamonds + %s WHERE ID = %s", (amount, to))
    db.cursor.execute("INSERT INTO transactions VALUES (NULL, %s, %s, %s, %s)", (from_, to, amount, time.time()))
    db.connection.commit()
    utils.notify_user(to, f"На ваш баланс поступило {amount} рубинов от игрока {user_from['username']}.")
    utils.notify_user(from_, f"С вашего баланса списано {amount} рубинов и переведено игроку {user_to['username']}")

def get_transactions(account_id:int):
    db = Database(assoc=True)
    db.cursor.execute("SELECT * FROM transactions WHERE account_from = %s OR account_to = %s", (account_id, account_id))
    transactions = db.cursor.fetchall()
    print(transactions)
    return transactions