from base64 import b64decode
import base64
import gzip
from time import time
import perms
import models
from fastapi.responses import HTMLResponse
from database import Database
import utils

def request_user_access(accountID:int) -> HTMLResponse:
    db = Database(assoc=True)
    query = """SELECT mod_level FROM accounts WHERE ID=%(account_id)s"""
    db.cursor.execute(query, {"account_id": accountID})
    mod_level = db.cursor.fetchone()['mod_level']
    return HTMLResponse(mod_level.__str__())

def suggest_level(accountID:int, levelID:int, stars:int, feature:int) -> HTMLResponse:
    db = Database(assoc=True)
    query = """SELECT mod_level FROM accounts WHERE ID=%(account_id)s"""
    db.cursor.execute(query, {"account_id": accountID})
    mod_level = db.cursor.fetchone()['mod_level']

    if "suggest" in perms.perms[mod_level]:
        with open("suggestions.txt", "a") as fp:
            fp.write(f"Suggestion on level {levelID} from {utils.get_username_by_id(accountID)} - {stars} stars with featured = {feature}\n")
        return HTMLResponse("1")
    if "rate" in perms.perms[mod_level]:

        db.cursor.execute("SELECT author_account_id FROM levels WHERE ID = %s", (levelID,))
        author = utils.get_user_assoc(db.cursor.fetchone()['author_account_id'])

        query1 = "UPDATE levels SET stars = %(stars)s WHERE ID = %(ID)s"
        query2 = "UPDATE levels SET is_featured = %(feature)s WHERE ID = %(ID)s"
        query3 = "UPDATE levels SET star_difficulty = %(star_diff)s WHERE ID = %(ID)s"
        query4 = "UPDATE levels SET is_auto = %(auto)s WHERE ID = %(ID)s"
        query5 = "UPDATE levels SET is_demon = %(demon)s WHERE ID = %(ID)s"

        db.cursor.execute(query1, {"stars": stars, "ID": levelID})
        db.cursor.execute(query2, {"feature": feature, "ID": levelID})

        if stars == 1:
            db.cursor.execute(query3, {"star_diff": 50, "ID": levelID})
            db.cursor.execute(query4, {"auto": 1, "ID": levelID})
            db.cursor.execute(query5, {"demon": 0, "ID": levelID})
        if stars == 2:
            db.cursor.execute(query3, {"star_diff": 10, "ID": levelID})
            db.cursor.execute(query4, {"auto": 0, "ID": levelID})
            db.cursor.execute(query5, {"demon": 0, "ID": levelID})
        if stars == 3:
            db.cursor.execute(query3, {"star_diff": 20, "ID": levelID})
            db.cursor.execute(query4, {"auto": 0, "ID": levelID})
            db.cursor.execute(query5, {"demon": 0, "ID": levelID})
        if stars == 4 or stars == 5:
            db.cursor.execute(query3, {"star_diff": 30, "ID": levelID})
            db.cursor.execute(query4, {"auto": 0, "ID": levelID})
            db.cursor.execute(query5, {"demon": 0, "ID": levelID})
        if stars == 6 or stars == 7:
            db.cursor.execute(query3, {"star_diff": 40, "ID": levelID})
            db.cursor.execute(query4, {"auto": 0, "ID": levelID})
            db.cursor.execute(query5, {"demon": 0, "ID": levelID})
        if stars == 8 or stars == 9:
            db.cursor.execute(query3, {"star_diff": 50, "ID": levelID})
            db.cursor.execute(query4, {"auto": 0, "ID": levelID})
            db.cursor.execute(query5, {"demon": 0, "ID": levelID})
        if stars == 10:
            db.cursor.execute(query3, {"star_diff": 50, "ID": levelID})
            db.cursor.execute(query4, {"auto": 0, "ID": levelID})
            db.cursor.execute(query5, {"demon": 1, "ID": levelID})
        db.cursor.execute("UPDATE accounts SET creator_points = creator_points + %s WHERE ID = %s", (feature + 1, author['ID']))
        db.connection.commit()
        utils.notify_author_about_rate(levelID)
        return HTMLResponse("1")

    raise models.GenericError(code=-2)