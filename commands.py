import base64
from time import time
import models
from fastapi.responses import HTMLResponse
from database import Database
import utils
import perms
import accounts
import telegrum

def execute_command(command:list, accountID:int, levelID:int, comment:str, percent:int, db:Database):
    mod_level = accounts.get_mod_level(accountID)

    if command[0] == "/help":
        text = """</c><cg>Calm down, it's Help page.</c>
<cy>/setdaily</c> - sets this level as daily level
<cy>/setstatus </c><cj>{status}</c> - sets your account's status.
<cy>/setcolor </c><cj>#{hexcolor}</c> - sets your comments's color.
<cy>/unrate </c> - unrates this level.
Type <cy>/help rate</c> for getting info about <cy>/rate </c>command.
<cg>Have a good day!"""
        if command.__len__() > 1:
            if command.__getitem__(1) == "rate":
                text = """</c>Keys:
<cj>diff:</c> <cp>[auto-demon]</c>
<cj>stars:</c> <cp>[0-10]</c>
<cj>demondiff:</c> <cp>[easy-extreme]</c>
<cj>featured:</c> <cp>[0-1]</c>
<cj>epic:</c> <cp>[0-1]</c>
Example:
<cy>/rate</c> <cj>diff</c>:<cp>demon</c> <cj>demondiff</c>:<cp>extreme</c> <cj>stars</c>:<cp>10</c><cy>"""

        
        return f"temp_0_{text}"
    elif command[0] == "/setdaily":
        if "daily" not in perms.perms[mod_level]:
            raise models.GenericError
        query = "INSERT INTO daily_line (`ID`, `level_id`, `timestamp`) VALUES (NULL, %(level_id)s, %(timestamp)s)"
        db.cursor.execute(query, {'level_id': levelID, 'timestamp': int(time())})
        db.connection.commit()
        return f"temp_0_</c>Not banned, <cg>succesfully set daily level!</c><cy>"
    elif command[0] == "/rate":
        if "rate" not in perms.perms[mod_level]:
            raise models.GenericError
        command_dict = {}
        for part in command:
            if part == "/rate":
                continue
            command_dict[part.split(":")[0]] = part.split(":")[1]
        if "epic" in command_dict.keys():
            query2 = "UPDATE levels SET is_epic = %(epic)s WHERE ID = %(ID)s"
            db.cursor.execute(query2, {'epic': command_dict['epic'], 'ID': levelID})
            query17 = "UPDATE levels SET is_featured = %(featured)s WHERE ID = %(ID)s"
            db.cursor.execute(query17, {'featured': command_dict['epic'], 'ID': levelID})
        if "featured" in command_dict.keys():
            query2 = "UPDATE levels SET is_featured = %(featured)s WHERE ID = %(ID)s"
            db.cursor.execute(query2, {'featured': command_dict['featured'], 'ID': levelID})
        if "stars" in command_dict.keys():
            query2 = "UPDATE levels SET stars = %(stars)s WHERE ID = %(ID)s"
            db.cursor.execute(query2, {'stars': command_dict['stars'], 'ID': levelID})
        if "diff" in command_dict.keys():
            query2 = "UPDATE levels SET star_difficulty = %(diff)s WHERE ID = %(ID)s"
            diff = command_dict['diff']

            diffs = {
                'auto': 50,
                'easy': 10,
                'normal': 20,
                'hard': 30,
                'harder': 40,
                'insane': 50,
                'demon': 50
            }
            
            db.cursor.execute(query2, {'diff': diffs[diff], 'ID': levelID})
            if diff == "auto":
                db.cursor.execute("UPDATE levels SET is_auto = 1 WHERE ID = %(ID)s", {'ID': levelID})
                db.cursor.execute("UPDATE levels SET is_demon = 0 WHERE ID = %(ID)s", {'ID': levelID})
            elif diff == "demon":
                db.cursor.execute("UPDATE levels SET is_auto = 0 WHERE ID = %(ID)s", {'ID': levelID})
                db.cursor.execute("UPDATE levels SET is_demon = 1 WHERE ID = %(ID)s", {'ID': levelID})

                demon_diffs = {
                    'easy': 3,
                    'medium': 4,
                    'hard': 2,
                    'insane': 5,
                    'extreme': 6
                }

                demon_diff = demon_diffs[command_dict['demondiff']]
                db.cursor.execute("UPDATE levels SET demon_difficulty = %(diff)s WHERE ID = %(ID)s", {'diff': demon_diff, 'ID': levelID})
            else:
                db.cursor.execute("UPDATE levels SET is_auto = 0 WHERE ID = %(ID)s", {'ID': levelID})
                db.cursor.execute("UPDATE levels SET is_demon = 0 WHERE ID = %(ID)s", {'ID': levelID})
                
        
        db.connection.commit()
        utils.notify_author_about_rate(levelID)
        return f"temp_0_</c>Not banned, <cg>succesfully rated level!</c><cy>"
    elif command[0] == "/unrate":
        if "rate" not in perms.perms[mod_level]:
            raise models.GenericError
        db.cursor.execute("UPDATE levels SET is_auto = 0 WHERE ID = %(ID)s", {'ID': levelID})
        db.cursor.execute("UPDATE levels SET is_demon = 0 WHERE ID = %(ID)s", {'ID': levelID})
        db.cursor.execute("UPDATE levels SET is_featured = 0 WHERE ID = %(ID)s", {'ID': levelID})
        db.cursor.execute("UPDATE levels SET is_epic = 0 WHERE ID = %(ID)s", {'ID': levelID})
        db.cursor.execute("UPDATE levels SET star_difficulty = %(diff)s WHERE ID = %(ID)s", {'diff': 0, 'ID': levelID})
        db.cursor.execute("UPDATE levels SET stars = %(diff)s WHERE ID = %(ID)s", {'diff': 0, 'ID': levelID})
        db.cursor.execute("UPDATE levels SET demon_difficulty = %(diff)s WHERE ID = %(ID)s", {'diff': 0, 'ID': levelID})

        db.connection.commit()
        return f"temp_0_</c>Not banned, <cg>succesfully unrated level!</c><cy>"
    elif command[0] == "/setstatus":
        command = comment.split(" ", 1)
        text = command[1]
        if "status" not in perms.perms[mod_level]:
            raise models.GenericError
        query = "UPDATE accounts SET status = %s WHERE ID = %s"
        db.cursor.execute(query, (text, accountID))
        db.connection.commit()
        return "1"
    elif command[0] == "/setcolor":
        command = comment.split(" ", 1)
        hexcolor = command[1]
        if "color" not in perms.perms[mod_level]:
            raise models.GenericError
        query = "UPDATE accounts SET comment_color = %s WHERE ID = %s"
        db.cursor.execute(query, (",".join([str(col) for col in utils.hex_to_rgb(hexcolor)]), accountID))
        db.connection.commit()
        return "1"
    elif command[0] == "/tgconfirm":
        user = utils.get_user_assoc(accountID)
        if user['temp_telegram_id'] == None:
            return f"temp_0_</c><cx>Error!</c> Request link first typing <cy>/link</c> command via <cj>RLTGDPS Bot</c> in <cj>Telegram.</c><cy>"
        query = "UPDATE accounts SET telegram_id = %s WHERE ID = %s"
        db.cursor.execute(query, (user['temp_telegram_id'], accountID))
        query = "UPDATE accounts SET temp_telegram_id = NULL WHERE ID = %s"
        db.cursor.execute(query, (accountID,))
        db.connection.commit()
        telegrum.send_telegram(user['temp_telegram_id'], "Аккаунт успешно привязан!")
        telegrum.send_telegram(user['temp_telegram_id'], "На заметку: ты можешь опубликовать в игре на аккаунте пост с командой /subscribe rates:1, чтобы подписаться на новости о рейтах твоих уровней.")
        return f"temp_0_</c><cg>Success!</c><cy>"
    elif command[0] == "/subscribe":
        user = utils.get_user_assoc(accountID)
        if user['telegram_id'] == None:
            return f"temp_0_</c><cx>Error!</c> Request link first typing <cy>/link</c> command via <cj>RLTGDPS Bot</c> in <cj>Telegram.</c><cy>"
        command_dict = {}
        for part in command:
            if part == "/subscribe":
                continue
            command_dict[part.split(":")[0]] = part.split(":")[1]

        if "rates" in command_dict.keys():
            db.cursor.execute("UPDATE accounts SET sub_push_rates = %s WHERE ID = %s", (command_dict['rates'], accountID))

            db.connection.commit()

            telegrum.send_telegram(user['telegram_id'], f"Ты {'подписался на новости' if int(command_dict['rates']) == 1 else 'отписался от новостей'} о рейтах твоих уровней.")
        return f"temp_0_</c><cg>Success!</c><cy>"
    elif command[0] == "/ban":
        level = utils.get_level_assoc(levelID)
        author_id = level['author_account_id']
        db.cursor.execute("UPDATE accounts SET banned = 1 WHERE ID = %s", (author_id,))
        db.connection.commit()
        return f"temp_0_</c><cg>Success!</c><cy>"
    else:
        return f"temp_0_</c>CUMmand not found, type <cg>/help</c> to get help with CUMment CUMmands<cy>"