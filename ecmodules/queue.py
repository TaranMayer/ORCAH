"""
Handle queue-related tasks
"""
import eclib.db.queue
import ecsocket
import eclib.apis
import echelpers as ech
import eclib.roles
import ecusers
import string
import random
import csv


async def push_update(db, client=None, user=None):
    """
    Send most current queue data.
    If `client` and `user` are specified, only sends the data to that client (for `get` requests).

    :param db: database object
    :type db: ecdatabase.Database
    :param client: target client (only for `get` requests)
    :type client: websockets.WebSocketCommonProtocol
    :param user: user of target client (only for `get` requests)
    :type user: ecusers.User
    """
    db_result = await db.select(eclib.db.queue.table_, [(eclib.db.queue.time_removed, "==", "0")])
    teams_queue = list()
    volunteers_queue = list()
    stream_queue = list()
    for row in db_result:
        purpose = row[eclib.db.queue.purpose]
        stream_queue.append({eclib.db.queue.team_num: row[eclib.db.queue.team_num], eclib.db.queue.purpose: purpose, eclib.db.queue.referee: row[eclib.db.queue.referee]})
        if purpose == eclib.db.queue.purpose_driving_skills:
            purpose = "Driving Skills"
        elif purpose == eclib.db.queue.purpose_programming_skills:
            purpose = "Programming Skills"
        else:
            purpose = "Inspection"
        teams_queue.append({
            eclib.db.queue.team_num: row[eclib.db.queue.team_num],
            eclib.db.queue.purpose: purpose,
            "ongoing": bool(row[eclib.db.queue.referee])
        })
        volunteers_queue.append({
            eclib.db.queue.team_num: row[eclib.db.queue.team_num],
            eclib.db.queue.purpose: purpose,
            eclib.db.queue.time_queued: ech.timestamp_to_readable(row[eclib.db.queue.time_queued]),
            eclib.db.queue.referee: row[eclib.db.queue.referee]
        })
    teams_msg = {"api": eclib.apis.queue, "operation": "post", "queue": teams_queue}
    volunteers_msg = {"api": eclib.apis.queue, "operation": "postCtrl", "queue": volunteers_queue}

    labels = [None] * len(ecusers.User.rooms)
    upcoming = list()
    for item in stream_queue:
        pickle = {eclib.db.queue.team_num: item[eclib.db.queue.team_num], eclib.db.queue.purpose: item[eclib.db.queue.purpose]}
        if item[eclib.db.queue.referee] and item[eclib.db.queue.purpose] > eclib.db.queue.purpose_inspection:
            for i, referee in enumerate(ecusers.User.rooms):
                if item[eclib.db.queue.referee] == referee.name:
                    labels[i] = pickle
                    break
        elif len(upcoming) < 2 and item[eclib.db.queue.purpose] > eclib.db.queue.purpose_inspection:
            upcoming.append(pickle)
    stream_msg = {"api": eclib.apis.livestream, "labels": labels, "upcoming": upcoming}

    if client is not None and user is not None:  # `get` request
        if user.has_access(eclib.apis.inspection, eclib.apis.skills):
            await ecsocket.send_by_client(teams_msg, client)
        if user.has_access(eclib.apis.inspection_ctrl, eclib.apis.skills_ctrl):
            await ecsocket.send_by_client(volunteers_msg, client)
        if user.has_access(eclib.apis.livestream):
            await ecsocket.send_by_client(stream_msg, client)
    else:  # save operation
        await ecsocket.send_by_access(volunteers_msg, eclib.apis.inspection_ctrl, eclib.apis.skills_ctrl)
        await ecsocket.send_by_access(teams_msg, eclib.apis.inspection, eclib.apis.skills)
        await ecsocket.send_by_access(stream_msg, eclib.apis.livestream)

    # label1 = ""
    # label2 = ""
    # upcoming = ""
    # upcoming_count = 0
    # for item in stream_queue:
    #     if item[eclib.db.queue.referee] == "Nathan" and item[eclib.db.queue.purpose] > eclib.db.queue.purpose_inspection:
    #         label1 = "Team " + item[eclib.db.queue.team_num] + "&ensp;<i class='fas fa-"
    #         if item[eclib.db.queue.purpose] == eclib.db.queue.purpose_driving_skills:
    #             label1 += "gamepad"
    #         elif item[eclib.db.queue.purpose] == eclib.db.queue.purpose_programming_skills:
    #             label1 += "laptop-code"
    #         label1 += "'></i>"
    #     elif item[eclib.db.queue.referee] == "Gene" and item[eclib.db.queue.purpose] > eclib.db.queue.purpose_inspection:
    #         label2 = "Team " + item[eclib.db.queue.team_num] + "&ensp;<i class='fas fa-"
    #         if item[eclib.db.queue.purpose] == eclib.db.queue.purpose_driving_skills:
    #             label2 += "gamepad"
    #         elif item[eclib.db.queue.purpose] == eclib.db.queue.purpose_programming_skills:
    #             label2 += "laptop-code"
    #         label2 += "'></i>"
    #     elif upcoming_count < 2 and item[eclib.db.queue.purpose] > eclib.db.queue.purpose_inspection:
    #         if upcoming_count == 1:
    #             upcoming += "&emsp;&bull;&emsp;"
    #         upcoming += item[eclib.db.queue.team_num] + "&ensp;<i class='fas fa-"
    #         if item[eclib.db.queue.purpose] == eclib.db.queue.purpose_driving_skills:
    #             upcoming += "gamepad"
    #         elif item[eclib.db.queue.purpose] == eclib.db.queue.purpose_programming_skills:
    #             upcoming += "laptop-code"
    #         upcoming += "'></i>"
    #         upcoming_count += 1
    # if upcoming_count == 0:
    #     upcoming = "No teams in queue for Skills"
    # else:
    #     upcoming = "Up Next:&emsp;" + upcoming
    # await ecsocket.send_by_access(json.dumps({"api": apis.livestream, "labels": [label1, label2], "upcoming": upcoming}), apis.meeting_ctrl)


async def team_queue(purpose, client, team, db):
    """
    Add team to queue.
    Executed by team.

    :param purpose: queue purpose
    :type purpose: int
    :param client: client that sent request
    :type client: websockets.WebSocketCommonProtocol
    :param team: team in question
    :type team: ecusers.User
    :param db: database object
    :type db: ecdatabase.Database
    """
    db_result = await db.select(eclib.db.queue.table_, [(eclib.db.queue.team_num, "==", team.name), (eclib.db.queue.time_removed, "==", 0)])
    if len(db_result) == 0:
        if purpose in (eclib.db.queue.purpose_driving_skills, eclib.db.queue.purpose_programming_skills):
            if not ech.SKILLS_OPEN:
                await ech.send_error(client, "Skills is currently closed.")
                return
            elif ech.SKILLS_ATTEMPTS[team.name][purpose - 1] >= 3:
                await ech.send_error(client, "You have exceeded your allowed " + ("Driving" if purpose == eclib.db.queue.purpose_driving_skills else "Programming") + " Skills attempts.")
                return
            elif team.name not in ech.INSPECTED_TEAMS:
                await ech.send_error(client, "You have not passed inspection.")
                return
        elif purpose == eclib.db.queue.purpose_inspection:
            if not ech.INSPECTION_OPEN:
                await ech.send_error(client, "Inspection is currently closed.")
                return
        else:
            await ech.send_error(client)
            return
        await db.insert(eclib.db.queue.table_, {eclib.db.queue.team_num: team.name, eclib.db.queue.purpose: purpose, eclib.db.queue.time_queued: ech.current_time()})
        await push_update(db)
    else:
        await ech.send_error(client, "You must leave the queue before you can queue again!")


async def team_unqueue(team, db):
    """
    Remove team from queue.
    Executed by team.

    :param team: team in question
    :type team: ecusers.User
    :param db: database object
    :type db: ecdatabase.Database
    """
    await db.update(eclib.db.queue.table_, [(eclib.db.queue.team_num, "==", team.name), (eclib.db.queue.time_removed, "==", 0)], {
        eclib.db.queue.removed_by: team.name,
        eclib.db.queue.time_removed: ech.current_time()
    })
    await push_update(db)

async def save_passwd(room, pwd):
    passcodes = {
        "r1":"",
        "r2":"",
        "r3":"",
        "r4":""
    }
    with open("passcodes.csv", newline='') as f:
        reader = csv.reader(f)
        for num, row in enumerate(reader, start=1):
            passcodes[f'r{num}'] = row[1]
    passcodes[f'r{room}'] = pwd
    with open("passcodes.csv", 'w', newline='') as f:
        reader = csv.writer(f)
        reader.writerow(['Room1', passcodes["r1"]])
        reader.writerow(['Room2', passcodes["r2"]])
        reader.writerow(['Room3', passcodes["r3"]])
        reader.writerow(['Room4', passcodes["r4"]])

async def ctrl_invite(payload, client, user, db):
    """
    Invite team to meeting room.
    Executed by referee.

    :param payload: received payload
    :type payload: dict[str, Any]
    :param client: client that sent request
    :type client: websockets.WebSocketCommonProtocol
    :param user: team in question
    :type user: ecusers.User
    :param db: database object
    :type db: ecdatabase.Database
    :return: whether operation was successful
    :rtype: bool
    """
    if (team_num := await ech.safe_extract(client, payload, {eclib.db.queue.team_num: str})) is not None and user.role == eclib.roles.referee:
        db_result = await db.select(eclib.db.queue.table_, [(eclib.db.queue.referee, "==", user.name), (eclib.db.queue.time_removed, "==", 0)])
        if len(db_result) > 0:
            if db_result[0][eclib.db.queue.team_num] != team_num:
                await ech.send_error(client, "You can only invite one team at a time!")
                return False
        db_result = await db.select(eclib.db.queue.table_, [(eclib.db.queue.team_num, "==", team_num), (eclib.db.queue.time_removed, "==", 0)])
        if len(db_result) == 0:
            await ech.send_error(client)
            return False
        if db_result[0][eclib.db.queue.referee] in ("", user.name):
            await db.update(eclib.db.queue.table_, [(eclib.db.queue.team_num, "==", team_num), (eclib.db.queue.time_removed, "==", 0)], {
                eclib.db.queue.time_invited: ech.current_time(),
                eclib.db.queue.referee: user.name
            })
            password = (''.join(random.choice(string.digits) for _ in range(4)))
            await ecsocket.send_by_access({"api": eclib.apis.meeting_ctrl, "room": user.room, "password": password}, eclib.apis.meeting_ctrl)
            team_msg = {"api": eclib.apis.main, "modal":
                        "<p>You are invited to join the video call:</p>" +
                        "<p><a href=\"https://meet.orcah.org/room" + str(user.room) + "\" target=\"_blank\">" +
                        "https://meet.orcah.org/room" + str(user.room) + "</a></p>" +
                        "<p>Password: <big><strong><tt>" + password + "</tt></strong></big></p>"
                        }
            await ecsocket.send_by_user(team_msg, ecusers.User.find_user(team_num))
            await push_update(db)
            await save_passwd(str(user.room), password)
            return True
    return False


async def ctrl_remove(payload, client, user, db):
    """
    Remove team from queue.
    Executed by referee or event partner.

    :param payload: received payload
    :type payload: dict[str, Any]
    :param client: client that sent request
    :type client: websockets.WebSocketCommonProtocol
    :param user: team in question
    :type user: ecusers.User
    :param db: database object
    :type db: ecdatabase.Database
    """
    if (team_num := await ech.safe_extract(client, payload, {eclib.db.inspection.team_num: str})) is not None:
        db_result = await db.select(eclib.db.queue.table_, [(eclib.db.queue.team_num, "==", team_num), (eclib.db.queue.time_removed, "==", 0)])
        if len(db_result) == 0:
            await ech.send_error(client)
            return
        if user.name == db_result[0][eclib.db.queue.referee] or user.role == eclib.roles.event_partner:
            await db.update(eclib.db.queue.table_, [(eclib.db.queue.team_num, "==", team_num), (eclib.db.queue.time_removed, "==", 0)], {
                eclib.db.queue.removed_by: user.name,
                eclib.db.queue.time_removed: ech.current_time()
            })
            await push_update(db)
        else:
            await ech.send_error(client)
