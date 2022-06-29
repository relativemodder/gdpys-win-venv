import base64
from time import time
import models
from fastapi.responses import HTMLResponse
from database import Database
import utils
import perms
import accounts

def send_friend_request(me:int, to:int, comment:str) -> HTMLResponse:
    db = Database(assoc=True)

    target = utils.get_user_assoc(to)

    if target['friends_state'] == 1:
        raise models.GenericError

    query = "INSERT INTO relationships (ID, person1, person2, friend_state, blocked, comment, timestamp) VALUES (NULL, %s, %s, %s, %s, %s, %s)"
    params = (me, to, 0, 0, comment, time())
    db.cursor.execute(query, params)
    db.connection.commit()
    return HTMLResponse("1")
def accept_friend_request(requestID:int) -> HTMLResponse:
    db = Database(assoc=True)
    query = "UPDATE relationships SET friend_state = 1 WHERE ID = %s"
    params = (requestID,)
    db.cursor.execute(query, params)
    db.connection.commit()
    return HTMLResponse("1")
def remove_friend(me:int, target:int) -> HTMLResponse:
    db = Database(assoc=True)
    query = f"DELETE FROM relationships WHERE (person1 = {me} AND person2 = {target}) OR (person1 = {target} AND person2 = {me})"
    db.cursor.execute(query)
    db.connection.commit()
    return HTMLResponse("1")

def get_friend_requests(me:int, page:int, get_sent:int) -> HTMLResponse:
    db = Database(assoc=True)
    person = 2 if get_sent == 0 else 1
    person_affected = 1 if get_sent == 0 else 2
    db.cursor.execute(f"SELECT * FROM relationships WHERE person{person} = %(me)s AND friend_state = 0 ORDER BY timestamp DESC LIMIT 10 OFFSET %(offset)s", {'me': me, 'offset':page*10})
    friendreqs = db.cursor.fetchall()
    reqsstring_list = []
    for request in friendreqs:
        user = utils.get_user_assoc(request[f'person{person_affected}'])
        arr = {
            '1': user['username'],
            '2': user['ID'],
            '9': user['icon'],
            '10': user['colors'].split(',')[0],
            '11': user['colors'].split(',')[1],
            '14': user['icon_type'],
            '15': user['special'],
            '16': user['ID'],
            '32': request['ID'],
            '35': request['comment'],
            '41': 0,
            '37': utils.make_time_string(int(time())-request['timestamp'])
        }
        reqsstring_list.append(models.construct_array(arr))
    return HTMLResponse(f"{models.construct_pipe_list(reqsstring_list)}#9999:{page*10}:10")

def get_friends(me:int) -> HTMLResponse:
    db = Database(assoc=True)
    
    usersselector_list = []
    users_list = []
    db.cursor.execute("SELECT * FROM relationships WHERE (person1 = %s OR person2 = %s) AND friend_state = 1", (me,me))
    relationships = db.cursor.fetchall()
    for relationship in relationships:
        if relationship['person1'] == me:
            usersselector_list.append(relationship['person2'])
            continue
        usersselector_list.append(relationship['person1'])
    for user_id in usersselector_list:
        user = utils.get_user_assoc(user_id)
        arr = {
            '1': user['username'],
            '2': user['ID'],
            '9': user['icon'],
            '10': user['colors'].split(',')[0],
            '11': user['colors'].split(',')[1],
            '14': user['icon_type'],
            '15': user['special'],
            '16': user['ID'],
            '18': '0',
            '41': '0'
        }
        users_list.append(models.construct_array(arr))
    usersstring = models.construct_pipe_list(users_list)
    return HTMLResponse(usersstring)