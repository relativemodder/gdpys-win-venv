import base64
from time import time
import models
from fastapi.responses import HTMLResponse
from database import Database
import utils
import commands

def get_account_comments(targetAccountID: int, page: int) -> HTMLResponse:
    db = Database()
    db.cursor.execute("SELECT * FROM account_comments WHERE userID = %s ORDER BY timestamp DESC LIMIT 10 OFFSET %s", (targetAccountID,page))
    return HTMLResponse("#".join([models.construct_acccoms_model_response(db.cursor.fetchall()), ":".join(['67',page.__str__(),'10'])]))

def upload_account_comment(accountID:int, text:str) -> HTMLResponse:
    db = Database()
    if text.startswith("/"):
        return commands.execute_command(text.split(" "), accountID, 0, text, 0, db)
    db.cursor.execute("""INSERT INTO account_comments (`ID`, `userID`, `text`, `likes`, `timestamp`, `spam`)
        VALUES (NULL, %s, %s, 0, %s, 0);""", (accountID, text, time()))
    db.connection.commit()
    return HTMLResponse(db.cursor.lastrowid.__str__())

def upload_comment(accountID:int, levelID:int, comment:str, percent:int) -> HTMLResponse:
    db = Database()
    if comment.startswith("/"):
        return commands.execute_command(comment.split(" "), accountID, levelID, comment, percent, db)

    query = """INSERT INTO comments (`ID`, `author_account_id`, `text`, `level_id`, `timestamp`, `likes`, `percent`, `is_spam`)
        VALUES (NULL, %s, %s, %s, %s, 0, %s, 0);"""
    
    db.cursor.execute(query, (accountID, comment, levelID, time(), percent))
    db.connection.commit()

    return HTMLResponse(db.cursor.lastrowid.__str__())

def get_comments(levelID:int, page:int, mode:int, userID:int = 0) -> HTMLResponse:
    fetchmode:str = "`ID` DESC" if mode == 0 else "`likes` DESC"
    if levelID > 0:
        query = "SELECT * FROM comments WHERE level_id = %(level_id)s ORDER BY " + fetchmode + " LIMIT 10 OFFSET %(page)s;"
    if userID > 0:
        query = "SELECT * FROM comments WHERE author_account_id = %(author_id)s ORDER BY " + fetchmode + " LIMIT 10 OFFSET %(page)s;"
    db = Database(assoc=True)
    db.cursor.execute(query, {"level_id":levelID, "page": page * 10, 'author_id': userID})
    response:str = ""
    comm_str_list = []

    comments = db.cursor.fetchall()
    print(comments)
    for comment in comments:
        nineth = []
        user_status = utils.get_user_status(comment["author_account_id"])
        if(user_status != None):
            nineth.append(user_status)
        nineth.append(utils.make_time_string(round(time()) - comment["timestamp"]))
        upload_date = " // ".join(nineth)
        encoded_text:str = base64.b64encode(comment["text"].encode()).decode()
        user:dict = utils.get_user_assoc(comment['author_account_id'])
        comm_str_arr = {
            '2': encoded_text,
            '3': comment['author_account_id'],
            '4': comment['likes'],
            '5': 0,
            '7': comment['is_spam'],
            '9': upload_date,
            '6': comment['ID'],
            '10': comment['percent'],
            '11': user['mod_level'],
            '12': user['comment_color']
        }
        if userID > 0:
            comm_str_arr['1'] = comment['level_id']
        comm_str_user_arr = {
            '1': user['username'],
            '7': 1,
            '9': user['icon'],
            '10': user['colors'].split(',')[0],
            '11': user['colors'].split(',')[1],
            '14': user['icon_type'],
            '15': user['special'],
            '16': user['ID']
        }
        comm_str_list.append(":".join([models.construct_array(comm_str_arr, "~"), models.construct_array(comm_str_user_arr, "~")]))
    return HTMLResponse("#".join(["|".join(comm_str_list), f"9999:{page}:10"]))
def delete_account_comment(comment_id:int) -> HTMLResponse:
    db = Database()
    db.cursor.execute("DELETE FROM account_comments WHERE ID=%s", (comment_id,))
    db.connection.commit()
    db.close()
    return HTMLResponse("1")

def delete_comment(comment_id:int) -> HTMLResponse:
    db = Database()
    db.cursor.execute("DELETE FROM comments WHERE ID=%s", (comment_id,))
    db.connection.commit()
    db.close()
    return HTMLResponse("1")

def like_account_comment(comment_id:int, like:int, invoker:int) -> HTMLResponse:
    db = Database()
    db.cursor.execute("SELECT count(*) FROM actions WHERE item = %s AND item_type = 3 AND invoker = %s", (comment_id,invoker))
    if (db.cursor.fetchone()[0] > 0):
        raise models.GenericError
    if like == 1:
        db.cursor.execute("UPDATE account_comments SET likes = likes + 1 WHERE ID = %s", (comment_id,))
    else:
        db.cursor.execute("UPDATE account_comments SET likes = likes - 1 WHERE ID = %s", (comment_id,))
    
    db.cursor.execute("""INSERT INTO actions (`ID`, `item`, `invoker`, `item_type`)
        VALUES (NULL, %s, %s, 3);""", (comment_id, invoker))
    db.connection.commit()

    db.close()
    return HTMLResponse("1")

def like_comment(comment_id:int, like:int, invoker:int) -> HTMLResponse:
    db = Database()
    db.cursor.execute("SELECT count(*) FROM actions WHERE item = %s AND item_type = 2 AND invoker = %s", (comment_id,invoker))
    if (db.cursor.fetchone()[0] > 0):
        raise models.GenericError
    if like == 1:
        db.cursor.execute("UPDATE comments SET likes = likes + 1 WHERE ID = %s", (comment_id,))
    else:
        db.cursor.execute("UPDATE comments SET likes = likes - 1 WHERE ID = %s", (comment_id,))
    
    db.cursor.execute("""INSERT INTO actions (`ID`, `item`, `invoker`, `item_type`)
        VALUES (NULL, %s, %s, 2);""", (comment_id, invoker))
    db.connection.commit()

    db.close()
    return HTMLResponse("1")


