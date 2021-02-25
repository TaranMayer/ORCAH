import eclib.db.matches
import ecsocket
import eclib.apis
import echelpers as ech
import eclib.roles
import ecusers
import string
import random
import csv
import json



async def set_match_start(db):
    with open('ecmodules/matches.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            db_add = {
                eclib.db.matches.match_num: row[0],
                eclib.db.matches.team_red: row[1],
                eclib.db.matches.team_blue: row[3],
                eclib.db.matches.red_score: 0,
                eclib.db.matches.blue_score: 0,
                eclib.db.matches.red_auto: 0,
                eclib.db.matches.blue_auto: 0,
                eclib.db.matches.red_wp: 0,
                eclib.db.matches.blue_wp: 0,
                eclib.db.matches.winner: "NONE",
                eclib.db.matches.scored: "FALSE"
            }
            await db.insert(eclib.db.matches.table_, db_add)
        matches_len = await db.select_special("SELECT Count(*) FROM matches")
        print(int(matches_len[0]['Count(*)']))


async def get_match_data(user, match_num, db):
    db_result = await db.select_special("SELECT Count(*) FROM matches")
    matches_len = int(db_result[0]['Count(*)'])
    if(matches_len<2):
        print(matches_len)
        await set_match_start(db)
    match_data = {}
    db_result = await db.select(eclib.db.matches.table_, [("matchNum", "==", match_num)])
    match_data["match"] = {'red':db_result[0]['teamRed'],'blue':db_result[0]['teamBlue'],'num':db_result[0]['matchNum'],'r_score':db_result[0]['redScore'],'b_score':db_result[0]['blueScore'], 'r_auto':db_result[0]['redAuton'], 'b_auto':db_result[0]['blueAuton'], 'r_wp':db_result[0]['redWinPoint'], 'b_wp':db_result[0]['blueWinPoint']}
    msg = {"api": eclib.apis.set_match, "operation": "get_data", "list":match_data}
    await ecsocket.send_by_user(msg, user)

async def set_match_data(user, match_num, red_team, blue_team, red_auto, blue_auto, red_wp, blue_wp, red_score, blue_score, db):
    winner = ""
    try:
        if(int(red_score) > int(blue_score)):
            winner = red_team
        elif(int(red_score) < int(blue_score)):
            winner = blue_team
        else:
            winner = "TIE"
    except:
        winner = "NULL"
    row = {
        eclib.db.matches.match_num: match_num,
        eclib.db.matches.team_red: red_team,
        eclib.db.matches.team_blue: blue_team,
        eclib.db.matches.red_score: red_score,
        eclib.db.matches.blue_score: blue_score,
        eclib.db.matches.red_auto: red_auto,
        eclib.db.matches.blue_auto: blue_auto,
        eclib.db.matches.red_wp: red_wp,
        eclib.db.matches.blue_wp: blue_wp,
        eclib.db.matches.winner: winner,
        eclib.db.matches.scored: "TRUE"
    }
    await db.update(eclib.db.matches.table_, [("matchNum", "==", match_num)], row)
    match_data = {}
    db_result = await db.select(eclib.db.matches.table_, [("matchNum", "==", match_num)])
    match_data["match"] = {'red':db_result[0]['teamRed'],'blue':db_result[0]['teamBlue'],'num':db_result[0]['matchNum'],'r_score':db_result[0]['redScore'],'b_score':db_result[0]['blueScore'], 'r_auto':db_result[0]['redAuton'], 'b_auto':db_result[0]['blueAuton'], 'r_wp':db_result[0]['redWinPoint'], 'b_wp':db_result[0]['blueWinPoint']}
    msg = {"api": eclib.apis.set_match, "operation": "get_data", "list":match_data}
    await ecsocket.send_by_user(msg, user)
async def rm_match_data(user, match_num, red_team, blue_team, red_auto, blue_auto, red_wp, blue_wp, red_score, blue_score, db):
    winner = "NONE"
    row = {
        eclib.db.matches.match_num: match_num,
        eclib.db.matches.team_red: red_team,
        eclib.db.matches.team_blue: blue_team,
        eclib.db.matches.red_score: red_score,
        eclib.db.matches.blue_score: blue_score,
        eclib.db.matches.red_auto: red_auto,
        eclib.db.matches.blue_auto: blue_auto,
        eclib.db.matches.red_wp: red_wp,
        eclib.db.matches.blue_wp: blue_wp,
        eclib.db.matches.winner: winner,
        eclib.db.matches.scored: "FALSE"
    }
    await db.update(eclib.db.matches.table_, [("matchNum", "==", match_num)], row)
    match_data = {}
    db_result = await db.select(eclib.db.matches.table_, [("matchNum", "==", match_num)])
    match_data["match"] = {'red':db_result[0]['teamRed'],'blue':db_result[0]['teamBlue'],'num':db_result[0]['matchNum'],'r_score':db_result[0]['redScore'],'b_score':db_result[0]['blueScore'], 'r_auto':db_result[0]['redAuton'], 'b_auto':db_result[0]['blueAuton'], 'r_wp':db_result[0]['redWinPoint'], 'b_wp':db_result[0]['blueWinPoint']}
    msg = {"api": eclib.apis.set_match, "operation": "get_data", "list":match_data}
    await ecsocket.send_by_user(msg, user)

async def get_matches(db,user):
    db_result = await db.select_special("SELECT Count(*) FROM matches")
    matches_len = int(db_result[0]['Count(*)'])
    if(matches_len<2):
        print(matches_len)
        await set_match_start(db)
    db_result = await db.select(eclib.db.matches.table_, [])
    matches = []
    matchesDict = {}
    for row in db_result:
        if(row['teamRed'] != "TBD" and row['teamBlue'] != "TBD"):
            matches.append(row['matchNum'])
    for num, match in enumerate(matches, start=1):
        matchesDict[num] = match
    msg = {"api": "Update Matches", "operation": "update", "list":matchesDict}
    await ecsocket.send_by_user(msg, user)

async def invite(user, red, blue):
    password = (''.join(random.choice(string.digits) for _ in range(4)))
    await ecsocket.send_by_access({"api": eclib.apis.meeting_ctrl, "room": user.room, "password": password}, eclib.apis.meeting_ctrl)
    team_msg = {"api": eclib.apis.main, "modal":
                "<p>You are invited to join the video call:</p>" +
                "<p><a href=\"https://meet.orcah.org/room" + str(user.room) + "\" target=\"_blank\">" +
                "https://meet.orcah.org/room" + str(user.room) + "</a></p>" +
                "<p>Password: <big><strong><tt>" + password + "</tt></strong></big></p>"
                }
    ref_msg = {"api": eclib.apis.main, "modal":
                "<p>Sent Invite to "+ red +" and "+ blue +"</p>"
                }
    await ecsocket.send_by_user(ref_msg, user)
    await ecsocket.send_by_user(team_msg, ecusers.User.find_user(red))
    await ecsocket.send_by_user(team_msg, ecusers.User.find_user(blue))

async def match_handler(client, user, operation, payload, db):
    if(operation=="get_match_data"):
        match_num=(payload['match'])
        await get_match_data(user, match_num, db)
    elif(operation=="set_match_data"):
        match_num=(payload['num'])
        red_team = payload['r_team']
        blue_team = payload['b_team']
        red_auto = payload['r_auto']
        blue_auto = payload['b_auto']
        red_wp = payload['r_wp']
        blue_wp = payload['b_wp']
        red_score = payload['red']
        blue_score = payload['blue']
        await set_match_data(user, match_num, red_team, blue_team, red_auto, blue_auto, red_wp, blue_wp, red_score, blue_score, db)
    elif(operation=="remove_match_data"):
        match_num=(payload['num'])
        red_team = payload['r_team']
        blue_team = payload['b_team']
        red_auto = payload['r_auto']
        blue_auto = payload['b_auto']
        red_wp = payload['r_wp']
        blue_wp = payload['b_wp']
        red_score = payload['red']
        blue_score = payload['blue']
        await rm_match_data(user, match_num, red_team, blue_team, red_auto, blue_auto, red_wp, blue_wp, red_score, blue_score, db)
    elif(operation=="get_matches"):
        await get_matches(db,user)
    elif operation=="invite":
        red = payload['red']
        blue = payload['blue']
        await invite(user,red,blue)
    else:
        print(operation)
