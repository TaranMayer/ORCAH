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
import eclib.db.skills



async def sort_and_push(db, user):
    ranks = {}
    db_result = await db.select(eclib.db.matches.table_, [(eclib.db.matches.scored, "==", "TRUE")])
    d_skills = {}
    skills_db_driver = await db.select(eclib.db.skills.table_, [(eclib.db.skills.skills_type, "==", 1)])
    for row in skills_db_driver:
        if row['teamNum'] not in d_skills.keys():
            d_skills[row['teamNum']] = row['score']
        else:
            if row['score'] > d_skills[row['teamNum']]:
                d_skills[row['teamNum']] = row['score']
    p_skills = {}
    skills_db_prog = await db.select(eclib.db.skills.table_, [(eclib.db.skills.skills_type, "==", 2)])
    for row in skills_db_prog:
        if row['teamNum'] not in p_skills.keys():
            p_skills[row['teamNum']] = row['score']
        else:
            if row['score'] > p_skills[row['teamNum']]:
                p_skills[row['teamNum']] = row['score']

    combined = {}
    for team in d_skills.keys():
        combined[team] = d_skills[team]
    for team in p_skills.keys():
        if team in combined.keys():
            combined[team] += p_skills[team]
        else:
            combined[team] = p_skills[team]
    for row in db_result:
        match_num = row['matchNum']
        if "e" not in str(match_num):
            winner = row['team']
            r_team = row['teamRed']
            b_team = row['teamBlue']
            r_auto = int(row['redAuton'])
            b_auto = int(row['blueAuton'])

            if winner != "TIE" and winner != "NONE":
                if r_team == winner and "*" not in winner:
                    if r_team not in ranks:
                        ranks[r_team] = [2,0,0]
                    else:
                        ranks[r_team][0] += 2
                    if b_team not in ranks:
                        ranks[b_team] = [0,0,0]
                    else:
                        ranks[b_team][0] += 0
                if b_team == winner and "*" not in winner:
                    if b_team not in ranks:
                        ranks[b_team] = [2,0,0]
                    else:
                        ranks[b_team][0] += 2
                    if r_team not in ranks:
                        ranks[r_team] = [0,0,0]
                    else:
                        ranks[r_team][0] += 0
            elif winner == "TIE":
                if r_team not in ranks:
                    ranks[r_team] = [1,0,0]
                else:
                    ranks[r_team][0] += 1
                if b_team not in ranks:
                    ranks[b_team] = [1,0,0]
                else:
                    ranks[b_team][0] += 1

            r_wp = row['redWinPoint']
            b_wp = row['blueWinPoint']

            if(r_wp == 1):
                r_wp_winner = row['teamRed']
                if r_wp_winner not in ranks and "*" not in r_wp_winner:
                    ranks[r_wp_winner] = [1,0,0]
                elif "*" not in r_wp_winner:
                    ranks[r_wp_winner][0] += 1
            if(b_wp == 1):
                b_wp_winner = row['teamBlue']
                if b_wp_winner not in ranks and "*" not in b_wp_winner:
                    ranks[b_wp_winner] = [1,0,0]
                elif "*" not in b_wp_winner:
                    ranks[b_wp_winner][0] += 1
            if(r_auto > b_auto):
                if "*" not in r_team:
                    if r_team not in ranks:
                        ranks[r_team] = [0,6,0]
                    else:
                        ranks[r_team][1] += 6
            elif(r_auto < b_auto):
                if "*" not in b_team:
                    if b_team not in ranks:
                        ranks[b_team] = [0,6,0]
                    else:
                        ranks[b_team][1] += 6
            elif(r_auto == b_auto):
                if "*" not in r_team:
                    if r_team not in ranks:
                        ranks[r_team] = [0,3,0]
                    else:
                        ranks[r_team][1] += 3
                if "*" not in b_team:
                    if b_team not in ranks:
                        ranks[b_team] = [0,3,0]
                    else:
                        ranks[b_team][1] += 3
            if r_team in combined.keys():
                if r_team not in ranks:
                    ranks[r_team] = [0,0,combined[r_team]]
                else:
                    ranks[r_team][2] = combined[r_team]
            if b_team in combined.keys():
                if b_team not in ranks:
                    ranks[b_team] = [0,0,combined[b_team]]
                else:
                    ranks[b_team][2] = combined[b_team]



    print(combined)
    ranks_items = list(ranks.items())
    rank_items_new = []
    for team in ranks_items:
        print(team)
        rank_items_new.append([team[0], team[1][0], team[1][1], team[1][2]])
    orderedRanks = sorted(rank_items_new, key = lambda t: (t[1], t[2], t[3]), reverse=True)
    rankingDict = {}
    for num, listing in enumerate(orderedRanks, start=1):
        team = listing[0]
        wp = listing[1]
        ap = listing[2]
        skills = listing[3]
        rank = num
        rankingDict[rank] = {"rank":rank, "team":team, "wp":wp, "ap":ap, "skills":skills}
    msg = {"api": eclib.apis.rankings, "operation": "return_data", "list":rankingDict}
    await ecsocket.send_by_user(msg, user)
    return orderedRanks
