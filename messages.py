import base64
from time import time
import models
from fastapi.responses import HTMLResponse
from database import Database
import utils
import perms
import accounts

def send_message(me:int, to:int, subject:str, body:str) -> HTMLResponse:
    db = Database(assoc=True)
    target = utils.get_user_assoc(to)
    if target['messages_state'] == 1:
        if utils.is_friends(me,to) != 1:
            raise models.GenericError
    query = "INSERT INTO messages VALUES (NULL, %(me)s, %(subject)s, %(body)s, %(target)s, %(ts)s)"
    params = {
        'me': me,
        'subject': subject,
        'body': body,
        'target': to,
        'ts': time()
    }
    db.cursor.execute(query, params)
    db.connection.commit()
    return HTMLResponse("1")
def get_messages(me:int, get_sent:int, page:int):
    db = Database(assoc=True)
    query = f"SELECT * FROM messages WHERE author_account_id = {me}" if get_sent == 1 else f"SELECT * FROM messages WHERE to_account_id = {me}"
    query += f" ORDER BY timestamp DESC LIMIT 10 OFFSET {page*10}"
    db.cursor.execute(query)
    msgstr_list = []
    messages = db.cursor.fetchall()
    for message in messages:
        user = utils.get_user_assoc(message['to_account_id']) if get_sent == 0 else utils.get_user_assoc(message['author_account_id'])
        arr = {
            '6': user['username'],
            '3': user['ID'],
            '2': user['ID'],
            '1': message['ID'],
            '4': message['subject'],
            '8': 1,
            '9': get_sent.__str__(),
            '7': utils.make_time_string(int(time())-message['timestamp'])
        }
        msgstr_list.append(models.construct_array(arr))
    return HTMLResponse(f"{models.construct_pipe_list(msgstr_list)}#9999:{page*10}:10")
def download_message(messageID:int, is_sender:int):
    db = Database(assoc=True)
    query = "SELECT * FROM messages WHERE ID = %s"
    params = (messageID,)
    db.cursor.execute(query, params)
    message = db.cursor.fetchone()
    user = message['to_account_id'] if is_sender == 1 else message['author_account_id']
    user = utils.get_user_assoc(user)
    arr = {
        '6': user['username'],
        '3': user['ID'],
        '2': user['ID'],
        '1': message['ID'],
        '4': message['subject'],
        '8': 1,
        '9': is_sender,
        '5': message['body'],
        '7': utils.make_time_string(int(time())-message['timestamp'])
    }
    return models.construct_array(arr)