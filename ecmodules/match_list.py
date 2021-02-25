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

# matches = [["red","blue","num","score"], ["5090X","EZ",1,"0-0"], ["169E","6030J",2,"0-0"]]

matches = {}

matches_obj = json.dumps(matches)

async def update(team, db, client=None):
    matches = {}
    db_result = await db.select(eclib.db.matches.table_, [])
    for num, match in enumerate(db_result,start=1):
        matches[num] = {'red':match['teamRed'],'blue':match['teamBlue'],'num':match['matchNum'],'r_score':match['redScore'],'b_score':match['blueScore'], 'r_auto':match['redAuton'], 'b_auto':match['blueAuton'], 'r_wp':match['redWinPoint'], 'b_wp':match['blueWinPoint']}
    matches_obj = json.dumps(matches)
    msg = {"api": eclib.apis.match_list, "operation": "update", "list":matches_obj}
    await ecsocket.send_by_user(msg, team)
