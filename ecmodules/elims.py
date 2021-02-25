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
import ecmodules.rankings


async def generate(db,user):
    await db.delete_special("DELETE FROM matches WHERE matchNum LIKE 'e%'")
    rankings = await ecmodules.rankings.sort_and_push(db,user)
    if(len(rankings) < 9):
        return
    round1 = []
    round1.append([rankings[7][0], rankings[8][0]])
    round1.append([rankings[3][0], rankings[4][0]])
    round1.append([rankings[1][0], rankings[6][0]])
    round1.append([rankings[2][0], rankings[5][0]])

    for num, match in enumerate(round1, start=1):
        row = {
            eclib.db.matches.match_num: f"e{num}",
            eclib.db.matches.team_red: match[0],
            eclib.db.matches.team_blue: match[1],
            eclib.db.matches.red_score: 0,
            eclib.db.matches.blue_score: 0,
            eclib.db.matches.red_auto: 0,
            eclib.db.matches.blue_auto: 0,
            eclib.db.matches.red_wp: 0,
            eclib.db.matches.blue_wp: 0,
            eclib.db.matches.winner: "NONE",
            eclib.db.matches.scored: "FALSE"
        }
        await db.insert(eclib.db.matches.table_, row)
    for x in range(12):
        row = {
            eclib.db.matches.match_num: f"e{x+5}",
            eclib.db.matches.team_red: "TBD",
            eclib.db.matches.team_blue: "TBD",
            eclib.db.matches.red_score: 0,
            eclib.db.matches.blue_score: 0,
            eclib.db.matches.red_auto: 0,
            eclib.db.matches.blue_auto: 0,
            eclib.db.matches.red_wp: 0,
            eclib.db.matches.blue_wp: 0,
            eclib.db.matches.winner: "NONE",
            eclib.db.matches.scored: "FALSE"
        }
        await db.insert(eclib.db.matches.table_, row)

async def check_schedule(num1, num2,list):
    checker = 0
    for match in list:
        if match['matchNum'] == num1 and match['scored'] == 'TRUE':
            checker += 1
        if match['matchNum'] == num2 and match['scored'] == 'TRUE':
            checker += 1
    if(checker == 2):
        return(True)
    else:
        return(False)

async def update_elims(db,user):
    matches = await db.select_special("SELECT * FROM matches WHERE matchNum LIKE 'e%'")
    rankings = await ecmodules.rankings.sort_and_push(db,user)
    if(len(rankings) < 9):
        return
    winners = {}
    for match in matches:
        num = match['matchNum']
        if match['scored'] == "TRUE":
            if match['team'] == match['teamRed']:
                winners[f'win_{num}'] = match['teamRed']
                winners[f'lose_{num}'] = match['teamBlue']
            elif match['team'] == match['teamBlue']:
                winners[f'win_{num}'] = match['teamBlue']
                winners[f'lose_{num}'] = match['teamRed']
            else:
                winners[f'win_{num}'] = "TBD"
                winners[f'lose_{num}'] = "TBD"
        else:
            winners[f'win_{num}'] = "TBD"
            winners[f'lose_{num}'] = "TBD"


    teams_needed = {
        "e5":[rankings[0][0],winners['win_e1']],
        "e6":[winners['lose_e4'],winners['lose_e1']],
        "e7":[winners['lose_e2'],winners['lose_e5']],
        "e8":[winners['lose_e3'],winners['win_e6']],
        "e9":[winners['win_e3'],winners['win_e4']],
        "e10":[winners['win_e5'],winners['win_e2']],
        "e11":[winners['lose_e9'],winners['win_e7']],
        "e12":[winners['lose_e10'],winners['win_e8']],
        "e13":[winners['win_e12'],winners['win_e11']],
        "e14":[winners['win_e10'],winners['win_e9']],
        "e15":[winners['lose_e14'],winners['win_e13']],
        "e16":[winners['win_e14'],winners['win_e15']]
    }


    prereqs = {
        "e5":['e1','e1'],
        "e6":['e4','e1'],
        "e7":['e2','e5'],
        "e8":['e3','e6'],
        "e9":['e3','e4'],
        "e10":['e5','e2'],
        "e11":['e9','e7'],
        "e12":['e10','e8'],
        "e13":['e11','e12'],
        "e14":['e10','e9'],
        "e15":['e14','e13'],
        "e16":['e14','e15']
    }
    for match in matches:
        num = match['matchNum']
        scored = match['scored']
        if num not in ["e1", "e2", "e3", "e4"]:
            ready = await check_schedule(prereqs[num][0], prereqs[num][1], matches)
            if ready == True and scored != "TRUE":
                red_needed = teams_needed[num][0]
                blue_needed = teams_needed[num][1]
                row = {
                    eclib.db.matches.match_num: num,
                    eclib.db.matches.team_red: red_needed,
                    eclib.db.matches.team_blue: blue_needed,
                    eclib.db.matches.red_score: 0,
                    eclib.db.matches.blue_score: 0,
                    eclib.db.matches.red_auto: 0,
                    eclib.db.matches.blue_auto: 0,
                    eclib.db.matches.red_wp: 0,
                    eclib.db.matches.blue_wp: 0,
                    eclib.db.matches.winner: "NONE",
                    eclib.db.matches.scored: "FALSE"
                }
                await db.update(eclib.db.matches.table_, [("matchNum", "==", num)], row)

async def handler(db, user, operation):
    if operation == "generate":
        await generate(db,user)
    elif operation == "update":
        await update_elims(db,user)
