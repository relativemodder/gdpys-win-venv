from hashlib import md5, sha1
from itertools import cycle
import time
from database import Database
import telegrum
from database import Database
def xor(data, key):
    return ''.join(chr(a ^ ord(b)) for (a, b) in zip(data, cycle(key)))
import base64

def gjp_encode(password: str) -> str:
    gjp = password.encode()
    gjp = xor(gjp,'37526').encode()
    gjp = base64.b64encode(gjp).decode()
    return str(gjp)

def gen_solo(level_string:str) -> str:
    hash_ = ""
    len_ = level_string.__len__()
    divided_ = len_ // 40
    p = 0
    k = 0
    while k < len_:
        if p > 39: break
        hash_ += level_string[k]
        p += 1
        k += divided_
    return sha1(f"{hash_}xI25fpAapCQg".encode()).hexdigest()

def parse_rob_song(orginal:str) -> dict:
    song = {}
    orig:list = orginal.split("~|~")
    for i in range(0, orig.__len__(), 2):
        song[str(orig[i])] = str(orig[i+1])
    return song

def gen_solo_2(lvlsmultistring:str) -> str:
    return sha1(f"{lvlsmultistring}xI25fpAapCQg".encode()).hexdigest()

def pass_encode(password: str) -> str:
    gjp = password.encode()
    gjp = xor(gjp,'26364').encode()
    gjp = base64.b64encode(gjp).decode()
    return str(gjp)

def gjp_decode(gjp: str) -> str:
    orig = base64.b64decode(gjp)
    orig = xor(orig,'37526')
    return str(orig)

def is_friends(me:int, target:int):
    db = Database(assoc=True)
    db.cursor.execute(f"SELECT * FROM relationships WHERE (person1 = {me} AND person2 = {target}) OR (person1 = {target} AND person2 = {me})")
    rships = db.cursor.fetchall()
    if rships.__len__() == 0:
        return 0
    ship = rships[0]
    if ship['friend_state'] == 0:
        if ship['person1'] == me:
            return 3
        if ship['person2'] == me:
            return 4
    return 1

def add_activity():
    db = Database(assoc=True)
    db.cursor.execute("INSERT INTO activity VALUES (NULL, %s)", (int(time.time()),))
    db.connection.commit()
    db.close()

def is_banned(me:int):
    me = get_user_assoc(me)
    if me['banned'] == 1:
        return True
    return False

def get_level_assoc(levelID:int):
    db = Database(assoc=True)
    db.cursor.execute("SELECT ID, author_account_id, name, stars, is_featured, is_epic FROM levels WHERE ID = %s", (levelID,))
    level = db.cursor.fetchone()
    return level

def notify_author_about_rate(levelID:int):
    level = get_level_assoc(levelID)
    
    acc_id = level['author_account_id']
    author = get_user_assoc(acc_id)
    if author['sub_push_rates'] == 0:
        return
    level_name = level['name']
    notify_user(acc_id, f"Поздравляю, твой уровень {level_name} оценили!")

def notify_user(account_id, notification):
    author = get_user_assoc(account_id)
    if author['telegram_id'] == None:
        return
    telegrum.send_telegram(author['telegram_id'], notification)
def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

def gen_multi(lvlids:list):
    hashd = ""
    db = Database(assoc=True)
    for level_id in lvlids:
        db.cursor.execute("SELECT ID, stars, coins FROM levels WHERE ID=%s", (level_id,))
        row = db.cursor.fetchone()
        str_id:str = row['ID'].__str__()
        hashd += f"{str_id[0]}{str_id[-1]}{row['stars']}{row['coins']}"
    return sha1(f"{hashd}xI25fpAapCQg".encode()).hexdigest()

def int2bool(b:bool) -> int:
    if b:
        return 1
    return 0
def get_username_by_id(account_id: int) -> str:
    db = Database()
    db.cursor.execute("SELECT username FROM accounts WHERE ID = %s", (account_id,))
    return db.cursor.fetchone()[0]
def get_user_assoc(account_id: int) -> dict:
    db = Database(assoc=True)
    db.cursor.execute("SELECT * FROM accounts WHERE ID = %s", (account_id,))
    return db.cursor.fetchone()
def get_user_assoc_by_username(username:str) -> dict:
    db = Database(assoc=True)
    db.cursor.execute("SELECT * FROM accounts WHERE username LIKE %s", (username,))
    return db.cursor.fetchone()
def get_user_assoc_TG(tg_id: int) -> dict:
    db = Database(assoc=True)
    db.cursor.execute("SELECT * FROM accounts WHERE telegram_id = %s", (tg_id,))
    return db.cursor.fetchone()
def make_time_string(delta:int) -> str:
    if delta < 31536000:
        if delta < 2628000:
            if delta < 604800:
                if delta < 86400:
                    if delta < 3600:
                        if delta < 60:
                            return f"{delta} second{'s' if delta!=1 else ''}"
                        return f"{delta//60} minute{'s' if delta//60!=1 else ''}"
                    return f"{delta//3600} hour{'s' if delta//3600!=1 else ''}"
                return f"{delta//86400} day{'s' if delta//86400!=1 else ''}"
            return f"{delta//604800} week{'s' if delta//604800!=1 else ''}"
        return f"{delta//2628000} month{'s' if delta//2628000!=1 else ''}"
    return f"{delta//31536000} year{'s' if delta//31536000!=1 else ''}"

def get_user_status(account_id:int):
    db = Database()
    db.cursor.execute("SELECT status FROM accounts WHERE ID = %s", (account_id,))
    status = db.cursor.fetchone()[0]
    db.close()
    return status

def check_gjp(account_id:int, gjp:str):
    db = Database()
    db.cursor.execute("SELECT password FROM accounts WHERE ID = %s", (account_id,))
    phash:str = db.cursor.fetchone()[0]
    if md5(gjp_decode(gjp).encode()).hexdigest() == phash:
        return True
    return False