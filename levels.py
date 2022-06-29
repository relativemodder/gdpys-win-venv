from base64 import b64decode
import base64
import gzip
from time import time

import models
from fastapi.responses import HTMLResponse
from database import Database
import utils
import songs

def like_level(level_id:int, like:int, invoker:int) -> HTMLResponse:
    db = Database()
    db.cursor.execute("SELECT count(*) FROM actions WHERE item = %s AND item_type = 1 AND invoker = %s", (level_id,invoker))
    if (db.cursor.fetchone()[0] > 0):
        raise models.GenericError
    if like == 1:
        db.cursor.execute("UPDATE levels SET likes = likes + 1 WHERE ID = %s", (level_id,))
    else:
        db.cursor.execute("UPDATE levels SET likes = likes - 1 WHERE ID = %s", (level_id,))
    
    db.cursor.execute("""INSERT INTO actions (`ID`, `item`, `invoker`, `item_type`)
        VALUES (NULL, %s, %s, 1);""", (level_id, invoker))
    db.connection.commit()

    db.close()
    return HTMLResponse("1")

def dl_level(level_id:int) -> HTMLResponse:
    db = Database()
    db.cursor.execute("UPDATE levels SET downloads = downloads + 1 WHERE ID = %s", (level_id,))
    db.connection.commit()

    db.close()
    return HTMLResponse("1")

def delete_level(levelID:int) -> HTMLResponse:
    db = Database(assoc=True)
    query = "DELETE FROM levels WHERE ID=%s"
    db.cursor.execute(query, (levelID,))
    db.connection.commit()
    return HTMLResponse("1")

def get_daily() -> HTMLResponse:
    db = Database(assoc=True)
    query = "SELECT * FROM `daily_line` WHERE 1 ORDER BY timestamp LIMIT 1"
    db.cursor.execute(query)
    daily = db.cursor.fetchone()
    timestamp = daily['timestamp']
    fea_id = daily['ID']
    return HTMLResponse(f"{fea_id}|{timestamp}")

def upload_level(accountID:int, levelID:int, levelName:str, levelDesc:str, levelVersion:int, levelLength:int, audioTrack:int, auto:int, password:int, original:int, twoPlayer:int, songID:int, objects:int, coins:int, requestedStars:int, unlisted:int, ldm:int, levelString:str, seed2:str) -> HTMLResponse:
    db = Database()

    db.cursor.execute("SELECT count(*) FROM levels WHERE (ID=%s OR name=%s) AND author_account_id = %s", (levelID, levelName, accountID))

    if db.cursor.fetchone()[0] == 0:
        query:str = """INSERT INTO levels
            (`ID`, `name`, `description`, `level_version`, `level_length`, `audio_track`, `password`, `original`, `song_id`, `objects`, `coins`, `requested_stars`, `extra_string`, `level_info`, `downloads`, `likes`, `unlisted`, `ldm`, `author_account_id`, `uploaded_timestamp`, `updated_timestamp`, `auto`, `is_demon`, `is_auto`, `stars`, `coins_verified`, `is_featured`, `is_epic`, `is_hall`, `demon_difficulty`, `star_difficulty`, `level_string`, `seed2`)
        VALUES (NULL, %s,    %s,              %s,               %s,              %s,           %s,         %s,        %s,        %s,       %s,          %s,                %s,            %s,         0,          0,        %s,       %s,         %s,                  %s,                    %s,            %s,       0,          0,        0,            0,             0,            0,         0,            0,                0,                  %s,          %s);"""
        query_args:tuple = (levelName, b64decode(levelDesc.encode()).decode(), levelVersion, levelLength, audioTrack, password, original, songID, objects, coins, requestedStars, "", 0, unlisted, ldm, accountID, time(), time(), auto, levelString.encode(), seed2)
        db.cursor.execute(query, query_args)
        db.connection.commit()
    else:
        query1:str = "UPDATE levels SET level_string = %s, description = %s WHERE (ID=%s OR name=%s) AND author_account_id = %s"
        db.cursor.execute(query1, (levelString, levelDesc, levelID, levelName, accountID))
        db.connection.commit()
    return HTMLResponse(db.cursor.lastrowid.__str__())

def get_levels(type_:int, str_:str, page:int) -> HTMLResponse:
    db = Database(assoc=True)
    type_ = int(type_)
    where = "1"
    

    if type_ == 0 or type_ == 15:
        where = "name LIKE %s" % f"%{str_}%"
        if str_.isdigit():
            id_level = int(str_)
            where = "ID = %s" % id_level
    if type_ == 5:
        where = "author_account_id = %s" % int(str_)
    if type_ == 6:
        where = "is_featured = 1"
    
    is_daily = False

    

    orderby = "ORDER BY `uploaded_timestamp` DESC"

    params = {
        'offset': page * 10
    }
    query:str = "SELECT * FROM levels WHERE "+where+" "+orderby+" LIMIT 10 OFFSET %(offset)s"

    lvlsmultistring_list = []
    lvlstring = ""
    userstring = ""
    songsstring = ""
    db.cursor.execute(query, params)
    print(query % params)
    levels = db.cursor.fetchall()

    for level in levels:
        lvlsmultistring_list.append(level['ID'])
        lvlstring += f"1:{level['ID']}:2:{level['name']}:5:{level['level_version']}:6:{level['author_account_id']}:8:10:9:{level['star_difficulty']}:10:{level['downloads']}:12:{level['audio_track']}:13:21:14:{level['likes']}:17:{level['is_demon']}:43:{level['demon_difficulty']}:25:{level['is_auto']}:18:{level['stars']}:19:{level['is_featured']}:42:{level['is_epic']}:45:{level['objects']}:3:{base64.b64encode(level['description'].encode()).decode()}:15:{level['level_length']}:30:{level['original']}:31:0:37:{level['coins']}:38:{level['coins_verified']}:39:{level['requested_stars']}:46:1:47:2:40:{level['ldm']}:35:{level['song_id']}|"
        if level['song_id'] != 0:
            songsstring += f"{songs.get(level['song_id']).body.decode()}~:~"
        user = utils.get_user_assoc(level['author_account_id'])
        if f"{user['ID']}:{user['username']}:{user['ID']}" not in userstring:
            userstring += f"{user['ID']}:{user['username']}:{user['ID']}|"
    lvlstring = lvlstring[:-1]
    userstring = userstring[:-1]
    songsstring = songsstring[:-3]

    query:str = """SELECT count(*) FROM levels WHERE 1 LIMIT 10 OFFSET %(offset)s"""
    db.cursor.execute(query, {
        'offset': page * 10
    })
    total = db.cursor.fetchone()['count(*)']
    response:str = f"{lvlstring}#{userstring}#{songsstring}#{total}:{page*10}:10#{utils.gen_multi(lvlsmultistring_list)}"

    return HTMLResponse(response)

def download_level(level_id:int) -> HTMLResponse:
    db = Database(assoc=True)
    is_daily = False
    fea_ = ""
    level_daily:dict = {}
    if level_id == -1:
        db.cursor.execute("SELECT * FROM daily_line WHERE 1 ORDER BY timestamp DESC LIMIT 1")
        level_daily = db.cursor.fetchone()
        print(level_daily)
        level_id = level_daily['level_id']
        fea_ = level_daily['ID']
        is_daily = True

    db.cursor.execute("SELECT * FROM levels WHERE ID = %s", (level_id,))

    level = db.cursor.fetchone()

    xor_pass = utils.pass_encode(level['password'].__str__())
    description = base64.b64encode(level['description'].encode()).decode()

    level_string:str = level['level_string'].decode()
    if level_string.startswith("kS1"):
        level_string = base64.b64encode(gzip.compress(level_string.encode())).decode()
        level_string = level_string.replace("/", "_")
        level_string = level_string.replace("+", "-")
    arr = {
        '1': level['ID'],
        '2': level['name'],
        '3': description,
        '4': level_string,
        '5': level['level_version'],
        '6': level['author_account_id'],
        '8': 10,
        '9': level['star_difficulty'],
        '10': level['downloads'],
        '11': '1',
        '12': level['audio_track'],
        '13': 21,
        '14': level['likes'],
        '17': level['is_demon'],
        '43': level['demon_difficulty'],
        '25': level['is_auto'],
        '18': level['stars'],
        '19': level['is_featured'],
        '42': level['is_epic'],
        '45': level['objects'],
        '15': level['level_length'],
        '30': level['original'],
        '31': 1,
        '28': utils.make_time_string(round(time()) -  level['uploaded_timestamp']),
        '29': utils.make_time_string(round(time()) -  level['updated_timestamp']),
        '35': level['song_id'],
        '36': level['extra_string'],
        '37': level['coins'],
        '38': level['coins_verified'],
        '39': level['requested_stars'],
        '46': 1,
        '47': 2,
        '48': 1,
        '40': level['ldm'],
        '27': xor_pass
    }
    if is_daily:
        arr['41'] = level_daily['ID']
    slstring1:str = utils.gen_solo(level_string)

    temp_fea = 0
    if is_daily:
        temp_fea = level_daily['ID']

    somestring:str = f"{level['author_account_id']},{level['stars']},{level['is_demon']},{level['ID']},{level['coins_verified']},{level['is_featured']},{level['password']},{temp_fea}"
    slstring2:str = utils.gen_solo_2(somestring)

    response:str = models.construct_array(arr)

    response += f"#{slstring1}#{slstring2}"
    if is_daily:
        userstring = f"{level['author_account_id']}:{utils.get_username_by_id(level['author_account_id'])}:{level['author_account_id']}"
        response += f"#{userstring}"
    print(response)
    dl_level(level_id)
    return HTMLResponse(response)