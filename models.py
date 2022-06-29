from ctypes import Union
import utils
from locale import strcoll
from typing import Optional
from unittest.util import strclass
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, HttpUrl
import base64
import time

def construct_comma_delta_response(data: list) -> HTMLResponse:
    data = [str(x) for x in data]
    return HTMLResponse(",".join(data))
def construct_array(data: dict, separator:str = ":") -> str:
    dat = list(data.items())
    str_rs = []
    for i in range(0, len(dat), 1):
        str_rs.append(str(dat[i][0]) + separator + str(dat[i][1]))
    return separator.join(str_rs)
def construct_pipe_list(data: list):
    return "|".join(data)



def construct_level_model(ID:int, name:str, description:str, levelString:str, version:int, author_account_id:int, difficulty_denominator:int, difficulty_numerator:int, downloads:int, audio_track:int, game_version:int, likes:int, length:int, is_demon:int, stars:int, feature_score:int, is_auto:int, song_id:int, coins:int, verified_coins:int, is_epic:int, demon_difficulty:int) -> str:
    arr = {
        '1': ID,
        '2': name,
        '3': base64.b64encode(description.encode()).decode(),
        '4': levelString,
        '5': version,
        '6': author_account_id,
        '8': difficulty_denominator,
        '9': difficulty_numerator,
        '10': downloads,
        '12': audio_track,
        '13': game_version,
        '14': likes,
        '15': length,
        '17': is_demon,
        '18': stars,
        '19': feature_score,
        '25': is_auto,
        '35': song_id,
        '37': coins,
        '38': verified_coins,
        '42': is_epic,
        '43': demon_difficulty
    }
    return construct_array(arr)

def construct_acccoms_model_response(comments: list) -> HTMLResponse:
    comm_strs = []
    for comment in comments:
        nineth = []
        user_status = utils.get_user_status(comment[1])
        if(user_status != None):
            nineth.append(user_status)
        nineth.append(utils.make_time_string(round(time.time()) - comment[4]))
        user = utils.get_user_assoc(comment[1])
        arr = {
            '2': base64.b64encode(comment[2].encode()).decode(),
            '4': comment[3],
            '9': " // ".join(nineth),
            '6': comment[0],
            '12': user['comment_color']
        }
        comm_strs.append(construct_array(arr, "~"))
    return construct_pipe_list(comm_strs)
def construct_account_model_response(userName:str, userID:int, stars:int, demons:int, ranking:int, accountHighlight:int, creatorPoints:int, iconID:int, playerColors:str, secretCoins:int, iconType:int, special:int, accountID:int, userCoins:int, messageState:int, friendsState:int, youtube:str, cube:int, ship:int, ball:int, ufo:int, wave:int, robot:int, streak:int, glow: bool, isRegistered:int, globalRank:int, friendRelativeState:int, newMessagesCount:int, newFriendRequestsCount:int, newFriendsCount:int, newFriendRequest:bool, age:str, spider:int, twitter:str, twitch:str, diamonds:int, accExplosion:int, modlevel:int, commentHistoryState:int) -> HTMLResponse:
    orig_array = {
        '1': userName,
        '2': userID,
        '3': stars,
        '4': demons,
        '6': ranking,
        '7': accountHighlight,
        '8': creatorPoints,
        '9': iconID,
        '10': int(playerColors.split(",")[0]),
        '11': int(playerColors.split(",")[1]),
        '13': secretCoins,
        '14': iconType,
        '15': special,
        '16': accountID,
        '17': userCoins,
        '18': messageState,
        '19': friendsState,
        '21': cube,
        '22': ship,
        '23': ball,
        '24': ufo,
        '25': wave,
        '26': robot,
        '27': streak,
        '28': utils.int2bool(glow),
        '29': isRegistered,
        '30': globalRank,
        '31': friendRelativeState,
        '38': newMessagesCount,
        '39': newFriendRequestsCount,
        '40': newFriendsCount,
        '41': newFriendRequest,
        '42': age,
        '43': spider,
        '46': diamonds,
        '48': accExplosion,
        '49': modlevel,
        '50': commentHistoryState
    }
    if youtube != None and youtube != "":
        orig_array['20'] = youtube
    if twitch != None and twitch != "":
        orig_array['45'] = twitch
    if twitter != None and twitter != "":
        orig_array['44'] = twitter
    return HTMLResponse(construct_array(orig_array))
class GenericError(Exception):
    code: int = -1
class TakenUsernameError(GenericError):
    code: int = -2
class TakenEmailError(GenericError):
    code: int = -3
class InvalidEmailError(GenericError):
    code: int = -6
class PermanentBanError(GenericError):
    code: int = -10
class AccountLoginRequest(BaseModel):
    userName: str
    password: str
    sid: Optional[str] = "Steam sucks"
    udid: str
    secret: Optional[str] = "Why secret lmao"
