import base64
from time import time
import models
from fastapi.responses import HTMLResponse
from database import Database
import utils
import perms
import accounts

def get_top_100() -> HTMLResponse:

    db = Database(assoc=True)
    query = "SELECT username, ID, secret_coins, user_coins, icon, colors, icon_type, special, stars, creator_points, demons, diamonds FROM accounts WHERE banned = 0 AND stars > 0 ORDER BY stars DESC LIMIT 100"

    db.cursor.execute(query)

    leaders = db.cursor.fetchall()
    leaders_list = []
    place = 0
    for leader in leaders:
        arr = {
            '1': leader['username'],
            '2': leader['ID'],
            '13': leader['secret_coins'],
            '17': leader['user_coins'],
            '6': place + 1,
            '9': leader['icon'],
            '10': leader['colors'].split(',')[0],
            '11': leader['colors'].split(',')[1],
            '14': leader['icon_type'],
            '15': leader['special'],
            '16': leader['ID'],
            '3': leader['stars'],
            '8': leader['creator_points'],
            '4': leader['demons'],
            '7': leader['ID'],
            '46': leader['diamonds']
        }
        leaders_list.append(models.construct_array(arr))
    return HTMLResponse(models.construct_pipe_list(leaders_list))

def get_top_100_creators() -> HTMLResponse:
    db = Database(assoc=True)
    query = "SELECT username, ID, secret_coins, user_coins, icon, colors, icon_type, special, stars, creator_points, demons, diamonds FROM accounts WHERE banned = 0 AND creator_points > 0 ORDER BY creator_points DESC LIMIT 100"

    db.cursor.execute(query)

    leaders = db.cursor.fetchall()
    leaders_list = []
    place = 0
    for leader in leaders:
        arr = {
            '1': leader['username'],
            '2': leader['ID'],
            '13': leader['secret_coins'],
            '17': leader['user_coins'],
            '6': place + 1,
            '9': leader['icon'],
            '10': leader['colors'].split(',')[0],
            '11': leader['colors'].split(',')[1],
            '14': leader['icon_type'],
            '15': leader['special'],
            '16': leader['ID'],
            '3': leader['stars'],
            '8': leader['creator_points'],
            '4': leader['demons'],
            '7': leader['ID'],
            '46': leader['diamonds']
        }
        leaders_list.append(models.construct_array(arr))
    return HTMLResponse(models.construct_pipe_list(leaders_list))