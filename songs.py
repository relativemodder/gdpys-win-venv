from base64 import b64decode
import base64
import gzip
from time import time
from urllib.parse import quote, unquote
import models
from fastapi.responses import HTMLResponse
from database import Database
import utils
import requests

def get_raw(song_id:int) -> dict:
    db = Database(assoc=True)
    db.cursor.execute("SELECT count(*) FROM songs WHERE ID = %s", (song_id,))
    return db.cursor.fetchone()

def get(song_id:int) -> HTMLResponse:
    db = Database(assoc=True)
    db.cursor.execute("SELECT count(*) FROM songs WHERE ID = %s", (song_id,))
    ftcb = db.cursor.fetchone()
    if ftcb['count(*)'] == 0:
        song:dict = get_boomlings_song(song_id)
        db.cursor.execute("""INSERT INTO songs (`ID`, `name`, `url`, `banned`, `size`, `author`)
            VALUES (%s, %s, %s, '0', %s, %s);""", (song_id, song['2'], unquote(song['10']), song['5'], song['4']))
        db.connection.commit()
        return HTMLResponse(models.construct_array(song, "~|~"))
    db.cursor.execute("SELECT * FROM songs WHERE ID = %s", (song_id,))
    song:dict = db.cursor.fetchone()
    arr = {
        '1': song_id,
        '2': song['name'],
        '3': 0,
        '4': song['author'],
        '5': song['size'],
        '10': song['url'],
        '8': 1,
        '6': '0',
        '7': '0'
    }
    return HTMLResponse(models.construct_array(arr, "~|~"))
        
def get_boomlings_song(song_id:int) -> dict:
    data = {
        "secret": "Wmfd2893gb7",
        "songID": song_id
    }
    req = requests.post("http://ptsgdpskonf.7m.pl/database/getGJSongInfo.php", data=data)
    print(req.text)
    song = utils.parse_rob_song(req.text)
    return song