import threading
import base64
import utils
import os
from typing import Mapping, Optional
from fastapi import BackgroundTasks, Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse
import models
import accounts
import comments
import levels
import songs
import mods
import relationships
import messages
import leaderboards

app = FastAPI()

@app.exception_handler(models.GenericError)
async def generic_error_handler(request: Request, exc: models.GenericError):
    return HTMLResponse(str(exc.code))

entry:str = '/database/gmdapi'

async def gjp_check(accountID: int = Form(), gjp: str = Form()):
    utils.add_activity()
    if utils.is_banned(accountID):
        raise models.PermanentBanError
    if not utils.check_gjp(accountID, gjp):
        raise models.GenericError
    

@app.get("/")
async def main():
    return HTMLResponse(content = "Redirecting to RLTGDPS Telegram Channel...", headers={'Location': 'https://t.me/RLTGDPS'}, status_code=308)

@app.get(entry)
async def main_point():
    return HTMLResponse("Main point")

@app.post(f"{entry}/accounts/loginGJAccount.php", response_class=HTMLResponse)
async def login(userName: str = Form(), password: str = Form(), udid: str = Form(), sid: str = Form(default="NotSteam")):
    return accounts.login(userName, password, udid, sid)

@app.post(f"{entry}/accounts/registerGJAccount.php", response_class=HTMLResponse)
async def register(userName: str = Form(), password: str = Form(), email: str = Form()):
    return accounts.register(userName, password, email)

@app.get(f"{entry}/accounts/accountManagement.php", response_class=HTMLResponse)
async def account_management_page():
    return HTMLResponse(content = "", headers={'Location': 'https://t.me/rltgdps_bot'}, status_code=308)

@app.post(f"{entry}/database/accounts/backupGJAccountNew.php", response_class=HTMLResponse)
async def backup_account(userName:str = Form(), password:str = Form(), saveData:str = Form()):
    account_id = accounts.login_raw(userName, str(password))
    return accounts.backup_save(account_id, password, saveData)

@app.post(f"{entry}/database/accounts/syncGJAccountNew.php", response_class=HTMLResponse)
async def backup_account(userName:str = Form(), password:str = Form()):
    account_id = accounts.login_raw(userName, str(password))
    return accounts.sync_save(account_id, password)

@app.post(f"{entry}/getAccountURL.php", response_class=HTMLResponse)
async def get_account_url():
    return "http://rltgdps.tk/database/gmdapi"

@app.post(f"/testgjp", response_class=HTMLResponse, dependencies=[Depends(gjp_check)])
async def test_gjp():
    return HTMLResponse("SUCCESS")

@app.post(f"{entry}/getGJUserInfo20.php", response_class=HTMLResponse, dependencies=[Depends(gjp_check)])
async def get_user_info(accountID:int = Form(), targetAccountID: int = Form()):
    return accounts.get(accountID, targetAccountID)

@app.post(f"{entry}/getGJUsers20.php", response_class=HTMLResponse)
async def get_user_info(str:str = Form(), page:int = Form()):
    return accounts.get_users(str, page)

@app.post(f"{entry}/updateGJUserScore22.php", response_class=HTMLResponse, dependencies=[Depends(gjp_check)])
async def update_user_info(accountID:int = Form(), stars:int = Form(), demons:int = Form(), diamonds:int = Form(), icon:int = Form(), iconType:int = Form(), coins:int = Form(), userCoins:int = Form(), accIcon:int = Form(), accShip:int = Form(), accBall:int = Form(), accBird:int = Form(), accDart:int = Form(), accRobot:int = Form(), accGlow:int = Form(), accSpider:int = Form(), accExplosion:int = Form(), seed2:str = Form(), color1:int = Form(), color2:int = Form(), special:int = Form()):
    accounts.update(accountID, stars, demons, diamonds, icon, iconType, coins, userCoins, accIcon, accShip, accBall, accBird, accDart, accRobot, accGlow, accSpider, accExplosion, seed2, color1, color2, special)
    return HTMLResponse(accountID.__str__())

@app.post(f"{entry}/updateGJAccSettings20.php", response_class=HTMLResponse, dependencies=[Depends(gjp_check)])
async def update_user_info(accountID:int = Form(), mS:int = Form(), frS:int = Form(), cS:int = Form(), yt:str = Form(default=""), twitter:str = Form(default=""), twitch:str = Form(default="")):
    return accounts.update_bio(accountID, mS, frS, cS, yt, twitter, twitch)

@app.post(f"{entry}/getGJAccountComments20.php", response_class=HTMLResponse)
async def get_account_comments(accountID:int = Form(), page:int = Form(default=0)):
    return comments.get_account_comments(accountID, page)

@app.post(f"{entry}/uploadGJAccComment20.php", response_class=HTMLResponse, dependencies=[Depends(gjp_check)])
async def upload_account_comment(accountID:int = Form(), comment:str = Form()):
    text = base64.b64decode(comment.encode()).decode()
    return comments.upload_account_comment(accountID, text)

@app.post(f"{entry}/deleteGJAccComment20.php", response_class=HTMLResponse, dependencies=[Depends(gjp_check)])
async def upload_account_comment(commentID:int = Form()):
    return comments.delete_account_comment(commentID)

@app.post(f"{entry}/likeGJItem211.php", response_class=HTMLResponse, dependencies=[Depends(gjp_check)])
async def like_item(itemID:int = Form(), type:int = Form(), accountID:int = Form(), like:int = Form(default=1)):
    if type == 3:
        return comments.like_account_comment(itemID, like, accountID)
    elif type == 2:
        return comments.like_comment(itemID, like, accountID)
    elif type == 1:
        return levels.like_level(itemID, like, accountID)

@app.post(f"{entry}/uploadGJLevel21.php", response_class=HTMLResponse, dependencies=[Depends(gjp_check)])
async def upload_level(accountID:int = Form(), levelID:int = Form(default=0), levelName:str = Form(), levelDesc:str = Form(default=''), levelVersion:int = Form(default=1), levelLength:int = Form(), audioTrack:int = Form(), auto:int = Form(default=0), password:int = Form(default=0), original:int = Form(default=0), twoPlayer:int = Form(default=0), songID:int = Form(default=0), objects:int = Form(default=0), coins:int = Form(default=0), requestedStars:int = Form(default=0), unlisted:int = Form(default=0), ldm:int = Form(default=0), levelString:str = Form(), seed2:str = Form()):
    return levels.upload_level(accountID, levelID, levelName, levelDesc, levelVersion, levelLength, audioTrack, auto, password, original, twoPlayer, songID, objects, coins, requestedStars, unlisted, ldm, levelString, seed2)

@app.post(f"{entry}/getGJLevels21.php", response_class=HTMLResponse)
async def get_levels(req: Request):
    # parsing robtop illegally hehe
    rowbody = await req.body()
    req_str = rowbody.decode()
    print(req_str)
    f = {}
    for field in req_str.split("&"):
        f[field.split("=")[0]] = field.split("=")[1]
    return levels.get_levels(f["type"], f["str"], int(f["page"]))

@app.post(f"{entry}/getGJDailyLevel.php", response_class=HTMLResponse)
async def get_daily_level():
    return levels.get_daily()

@app.post(f"{entry}/downloadGJLevel22.php", response_class=HTMLResponse)
async def get_levels(levelID:int = Form()):
    return levels.download_level(levelID)

@app.post(f"{entry}/deleteGJLevelUser20.php", response_class=HTMLResponse, dependencies=[Depends(gjp_check)])
async def upload_comment(levelID:int = Form()):
    return levels.delete_level(levelID)

@app.post(f"{entry}/getGJSongInfo.php", response_class=HTMLResponse)
async def get_song(songID:int = Form()):
    print(songID)
    return songs.get(songID)

@app.post(f"{entry}/getGJComments21.php", response_class=HTMLResponse)
async def get_comments(levelID:int = Form(), page:int = Form(default=0), mode:int = Form(default=0)):
    return comments.get_comments(levelID, page, mode)

@app.post(f"{entry}/getGJCommentHistory.php", response_class=HTMLResponse)
async def get_comments(userID:int = Form(), page:int = Form(default=0), mode:int = Form(default=0)):
    return comments.get_comments(0, page, mode, userID=userID)

@app.post(f"{entry}/uploadGJComment21.php", response_class=HTMLResponse, dependencies=[Depends(gjp_check)])
async def upload_comment(accountID:int = Form(), levelID:int = Form(), comment:str = Form(), percent:int = Form(default=0)):
    comment = base64.b64decode(comment.encode()).decode()
    return comments.upload_comment(accountID, levelID, comment, percent)

@app.post(f"{entry}/deleteGJComment20.php", response_class=HTMLResponse, dependencies=[Depends(gjp_check)])
async def delete_comment(commentID:int = Form()):
    return comments.delete_comment(commentID)

@app.post(f"{entry}/requestUserAccess.php", response_class=HTMLResponse, dependencies=[Depends(gjp_check)])
async def upload_comment(accountID:int = Form()):
    return mods.request_user_access(accountID)

@app.post(f"{entry}/suggestGJStars20.php", response_class=HTMLResponse, dependencies=[Depends(gjp_check)])
async def upload_comment(accountID:int = Form(), levelID:int = Form(), stars:int = Form(), feature:int = Form()):
    return mods.suggest_level(accountID, levelID, stars, feature)

@app.post(f"{entry}/uploadFriendRequest20.php", response_class=HTMLResponse, dependencies=[Depends(gjp_check)])
async def send_friend_request(accountID:int = Form(), toAccountID:int = Form(), comment:str = Form(default="")):
    return relationships.send_friend_request(accountID, toAccountID, comment)

@app.post(f"{entry}/getGJFriendRequests20.php", response_class=HTMLResponse, dependencies=[Depends(gjp_check)])
async def get_friend_requests(accountID:int = Form(), page:int = Form(default=0), getSent:int = Form(default=0)):
    print(relationships.get_friend_requests(accountID, page, getSent).body)
    return relationships.get_friend_requests(accountID, page, getSent)

@app.post(f"{entry}/acceptGJFriendRequest20.php", response_class=HTMLResponse, dependencies=[Depends(gjp_check)])
async def accept_friend_request(accountID:int = Form(), requestID:int = Form()):
    return relationships.accept_friend_request(requestID)

@app.post(f"{entry}/removeGJFriend20.php", response_class=HTMLResponse, dependencies=[Depends(gjp_check)])
async def accept_friend_request(accountID:int = Form(), targetAccountID:int = Form()):
    return relationships.remove_friend(accountID, targetAccountID)

@app.post(f"{entry}/getGJUserList20.php", response_class=HTMLResponse, dependencies=[Depends(gjp_check)])
async def get_user_list(accountID:int = Form(), type:int = Form()):
    return relationships.get_friends(accountID) if type == 0 else ""

@app.post(f"{entry}/uploadGJMessage20.php", response_class=HTMLResponse, dependencies=[Depends(gjp_check)])
async def send_message(accountID:int = Form(), subject:str = Form(), body:str = Form(), toAccountID:int = Form()):
    return messages.send_message(accountID, toAccountID, subject, body)

@app.post(f"{entry}/getGJMessages20.php", response_class=HTMLResponse, dependencies=[Depends(gjp_check)])
async def send_message(accountID:int = Form(), getSent:int = Form(default=0), page:int = Form(default=0)):
    return messages.get_messages(accountID, getSent, page)

@app.post(f"{entry}/downloadGJMessage20.php", response_class=HTMLResponse, dependencies=[Depends(gjp_check)])
async def send_message(messageID:int = Form(), isSender:int = Form(default=0)):
    return messages.download_message(messageID, isSender)

@app.post(f"{entry}/getGJScores20.php", response_class=HTMLResponse, dependencies=[Depends(gjp_check)])
async def get_leaderboards(type:str = Form()):
    if type == "top":
        return leaderboards.get_top_100()
    if type == "creators":
        return leaderboards.get_top_100_creators()

