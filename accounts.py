import base64
from hashlib import md5
from random import randint
import models
from fastapi.responses import HTMLResponse
from database import Database
import re
import utils
import telegrum

def validate_email(email: str) -> bool:
    regex = '^[a-z0-9]+[\._]?[ a-z0-9]+[@]\w+[. ]\w{2,3}$'
    if(re.search(regex,email)):
        return True
    return False

def login(username: str, password: str, udid: str, sid: str) -> HTMLResponse:
    db = Database()
    db.cursor.execute("SELECT * FROM accounts WHERE userName LIKE %s", (username,))
    results = db.cursor.fetchall()
    if len(results) == 0:
        raise models.GenericError
    account = results[0]

    if account[2] != md5(password.encode()).hexdigest():
        utils.notify_user(account[0], "Была произведена попытка входа в твой аккаунт. Это был ты?")
        raise models.GenericError

    db.cursor.execute("""UPDATE accounts SET udid = %s WHERE ID = %s""", (udid,account[0]))
    db.cursor.execute("""UPDATE accounts SET sid = %s WHERE ID = %s""", (sid,account[0]))
    db.connection.commit()

    db.close()

    utils.notify_user(account[0], "Произведён вход в твой аккаунт.")

    return models.construct_comma_delta_response([account[0], account[0]])

def login_raw(username: str, password: str) -> int:
    db = Database()
    db.cursor.execute("SELECT * FROM accounts WHERE userName LIKE %s", (username,))
    results = db.cursor.fetchall()
    if len(results) == 0:
        raise models.GenericError
    account = results[0]
    db.close()
    return account[0]

def checkNewMessages(me:int):
    return 0
def checkNewFriRequests(me:int):
    return 0
def checkNewFriends(me:int):
    return 0

def get_mod_level(me:int) -> int:
    db = Database(assoc=True)
    db.cursor.execute("SELECT mod_level FROM accounts WHERE ID = %s", (me,))
    return db.cursor.fetchone()['mod_level']

def get_users(str_:str, page:int) -> HTMLResponse:
    db = Database(assoc=True)
    offset = page*10
    db.cursor.execute("SELECT username, ID, secret_coins, user_coins, icon, colors, icon_type, special, stars, creator_points, demons FROM accounts WHERE ID = %(str)s OR username LIKE CONCAT('%', %(str)s, '%') ORDER BY stars DESC LIMIT 10 OFFSET %(offset)s", {'str': str_, 'offset': offset})
    users = db.cursor.fetchall()
    if users.__len__() == 0:
        raise models.GenericError
    userscount = 0
    if str_.isdigit():
        userscount = 1
    else:
        db.cursor.execute("SELECT count(*) FROM accounts WHERE username LIKE CONCAT('%', %(str)s, '%')", {'str': str_})
        userscount = db.cursor.fetchone()['count(*)']
    userstring_list:list = []
    for user in users:
        arr = {
            '1': user['username'],
            '2': user['ID'],
            '13': user['secret_coins'],
            '17': user['user_coins'],
            '9': user['icon'],
            '10': user['colors'].split(",")[0],
            '11': user['colors'].split(",")[1],
            '14': user['icon_type'],
            '15': user['special'],
            '16': user['ID'],
            '3': user['stars'],
            '8': user['creator_points'],
            '4': user['demons']
        }
        userstring_list.append(models.construct_array(arr))
    userstring = models.construct_pipe_list(userstring_list)
    return HTMLResponse(f"{userstring}#{userscount}:{offset}:10")

def get(me:int, targetAccountID: int) -> HTMLResponse:
    db = Database()
    db.cursor.execute("SELECT * FROM accounts WHERE ID = %s", (targetAccountID,))
    
    target = db.cursor.fetchone()
    if target == None:
        raise models.GenericError
    
    username = target[1]
    userID = target[0]
    accountID = target[0]
    stars = target[6]
    diamonds = target[7]
    demons = target[8]
    secret_coins = target[9]
    user_coins = target[10]
    icon = target[11]
    colors:str = target[12]
    icon_type = target[13]
    cube = target[14]
    ship = target[15]
    ball = target[16]
    ufo = target[17]
    wave = target[18]
    robot = target[19]
    spider = target[20]
    glow = target[21]
    explosion = target[22]
    banned = target[23]
    cp = target[24]
    youtube = target[25]
    twitch = target[26]
    twitter = target[27]
    messages_state = target[29]
    friends_state = target[30]
    mod_level = target[31]
    special = target[32]

    friend_state = utils.is_friends(me, targetAccountID)

    db.close()

    return models.construct_account_model_response(username, userID, stars, demons, 0, userID, cp, icon, colors, secret_coins, icon_type, special, accountID, user_coins, messages_state, friends_state, youtube, cube, ship, ball, ufo, wave, robot, 1, glow, 1, 0, friend_state, checkNewMessages(me), checkNewFriRequests(me), checkNewFriends(me), utils.int2bool(False), "", spider, twitter, twitch, diamonds, explosion, mod_level, 0)

def update_bio(me:int, mS:int, frS:int, cS:int, yt:str, twitter:str, twitch:str) -> HTMLResponse:
    db = Database(assoc=True)
    db.cursor.execute("UPDATE accounts SET messages_state = %s WHERE ID = %s", (mS, me))
    db.cursor.execute("UPDATE accounts SET friends_state = %s WHERE ID = %s", (frS, me))
    db.cursor.execute("UPDATE accounts SET youtube = %s WHERE ID = %s", (yt, me))
    db.cursor.execute("UPDATE accounts SET twitch = %s WHERE ID = %s", (twitch, me))
    db.cursor.execute("UPDATE accounts SET twitter = %s WHERE ID = %s", (twitter, me))
    db.connection.commit()
    return HTMLResponse("1")

def update(me:int, stars:int, demons:int, diamonds:int, icon:int, iconType:int, coins:int, userCoins:int, accIcon:int, accShip:int, accBall:int, accBird:int, accDart:int, accRobot:int, accGlow:int, accSpider:int, accExplosion:int, seed2:str, color1:int, color2:int, special:int):
    db = Database()
    db.cursor.execute("""UPDATE accounts SET stars = %s WHERE ID = %s""", (stars,me))
    db.cursor.execute("""UPDATE accounts SET demons = %s WHERE ID = %s""", (demons,me))
    #db.cursor.execute("""UPDATE accounts SET diamonds = %s WHERE ID = %s""", (diamonds,me))
    db.cursor.execute("""UPDATE accounts SET icon = %s WHERE ID = %s""", (icon,me))
    db.cursor.execute("""UPDATE accounts SET icon_type = %s WHERE ID = %s""", (iconType,me))
    db.cursor.execute("""UPDATE accounts SET secret_coins = %s WHERE ID = %s""", (coins,me))
    db.cursor.execute("""UPDATE accounts SET user_coins = %s WHERE ID = %s""", (userCoins,me))
    db.cursor.execute("""UPDATE accounts SET cube = %s WHERE ID = %s""", (accIcon,me))
    db.cursor.execute("""UPDATE accounts SET ship = %s WHERE ID = %s""", (accShip,me))
    db.cursor.execute("""UPDATE accounts SET ball = %s WHERE ID = %s""", (accBall,me))
    db.cursor.execute("""UPDATE accounts SET ufo = %s WHERE ID = %s""", (accBird,me))
    db.cursor.execute("""UPDATE accounts SET wave = %s WHERE ID = %s""", (accDart,me))
    db.cursor.execute("""UPDATE accounts SET robot = %s WHERE ID = %s""", (accRobot,me))
    db.cursor.execute("""UPDATE accounts SET glow = %s WHERE ID = %s""", (bool(accGlow),me))
    db.cursor.execute("""UPDATE accounts SET spider = %s WHERE ID = %s""", (accSpider,me))
    db.cursor.execute("""UPDATE accounts SET explosion = %s WHERE ID = %s""", (accExplosion,me))
    db.cursor.execute("""UPDATE accounts SET colors = %s WHERE ID = %s""", (",".join([color1.__str__(),color2.__str__()]),me))
    db.cursor.execute("""UPDATE accounts SET special = %s WHERE ID = %s""", (special,me))

    db.connection.commit()

    db.close()

def backup_save(account_id:int, password:str, save_data:str) -> HTMLResponse:
    db = Database(assoc=True)
    query:str = """UPDATE accounts SET saves = %(saves)s WHERE ID = %(id)s"""
    db.cursor.execute(query, {"saves": save_data.encode(), "id": account_id})
    db.connection.commit()
    return HTMLResponse("1")

def sync_save(account_id:int, password:str) -> HTMLResponse:
    db = Database(assoc=True)
    db.cursor.execute("SELECT saves FROM accounts WHERE ID = %s", (account_id,))
    raw_saves:bytes = db.cursor.fetchone()['saves']
    print(raw_saves)
    saves_de = f"{base64.b64decode(raw_saves).decode()}" if raw_saves.decode().startswith("SDRz") else raw_saves

    return HTMLResponse(f"{saves_de};21;30;a;a")

def register(username: str, password: str, email: str):
    db = Database()
    db.cursor.execute("SELECT * FROM accounts WHERE userName LIKE %s", (username,))
    results = db.cursor.fetchall()
    if len(results) > 0:
        raise models.TakenUsernameError
    db.cursor.execute("SELECT * FROM accounts WHERE email LIKE %s", (email,))
    results = db.cursor.fetchall()
    if len(results) > 0:
        raise models.TakenEmailError
    if not validate_email(email):
        raise models.InvalidEmailError
    db.cursor.execute("""INSERT INTO accounts (`ID`, `username`, `password`, `email`, `udid`, `sid`, `stars`, `icon`, `colors`, `icon_type`, `cube`, `ship`, `ball`, `ufo`, `wave`, `robot`, `spider`, `glow`, `explosion`, `banned`, `creator_points`, `youtube`, `twitch`, `twitter`, `saves`)
        VALUES (NULL, %s, %s, %s, NULL, NULL, '0', '0', NULL, '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0', NULL, NULL, NULL, NULL);""", (username, md5(password.encode()).hexdigest(), email))
    
    db.connection.commit()

    db.cursor.execute("UPDATE accounts SET diamonds = %s WHERE ID = %s", (randint(500, 1000), db.cursor.lastrowid))

    db.connection.commit()

    db.close()
    return HTMLResponse("1")