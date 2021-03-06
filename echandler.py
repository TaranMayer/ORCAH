# Original code authored by and copyright 18x18az

# Changes made by and copyright Taran Mayer:
# Updated if/else logic in the echandle function to account for the 5 additonal APIs I have added


"""
Handle messages received over WebSocket connections
"""
import json
import websockets
import ecusers
import ecsocket
import eclib.apis
import echelpers as ech
import ecmodules.chat
import ecmodules.event_control
import ecmodules.inspection
import ecmodules.queue
import ecmodules.skills
import ecmodules.tech_support
import ecmodules.match_list
import ecmodules.set_match
import ecmodules.rankings
import ecmodules.elims

db = None


def find_user_from_client(client):
    """
    Find user associated with a client

    :param client: client
    :type client: websockets.WebSocketCommonProtocol
    :return: corresponding user
    :rtype: ecusers.User
    """
    for user in ecusers.User.userlist:
        if client in user.clients:
            return user


async def echandle(client, user, api, operation, payload):
    """
    Perform relevant operation based on API specified in received payload.
    For logged-in users only.

    :param client: client that sent payload
    :type client: websockets.WebSocketCommonProtocol
    :param user: user that sent payload
    :type user: ecusers.User
    :param api: API specified in payload
    :type api: str
    :param operation: operation specified in payload
    :type operation: str
    :param payload: received payload, or `None` for automatically triggered 'get' requests
    :type payload: dict[str, Any] | None
    """
    global db
    if (user.has_access(api) and operation.startswith("get")) or (user.has_perms(api) and payload is not None):
        if payload is not None:
            pass
            #print(user.name + ": " + str(payload))
        if api == eclib.apis.chat:
            await ecmodules.chat.handler(client, user, operation, payload, db)
        elif api == eclib.apis.inspection:
            await ecmodules.inspection.team_handler(client, user, operation, payload, db)
        elif api == eclib.apis.stream:
            pass
        elif api == eclib.apis.match_list:
            await ecmodules.match_list.update(user, db, client)
        elif api == eclib.apis.rankings:
            await ecmodules.rankings.sort_and_push(db, user)
        elif api == eclib.apis.inspection_ctrl:
            await ecmodules.inspection.ctrl_handler(client, user, operation, payload, db)
        elif api == eclib.apis.set_match:
            await ecmodules.set_match.match_handler(client, user, operation, payload, db)
        elif api == eclib.apis.skills:
            await ecmodules.skills.team_handler(client, user, operation, payload, db)
        elif api == eclib.apis.skills_ctrl:
            await ecmodules.skills.ctrl_handler(client, user, operation, payload, db)
        elif api == eclib.apis.skills_scores:
            await ecmodules.skills.scores_handler(client, user, operation, payload, db)
        elif api == eclib.apis.tech_support:
            await ecmodules.tech_support.handler(client, user, operation, payload, db)
        elif api == eclib.apis.elims:
            await ecmodules.elims.handler(db,user,operation)
        elif api == eclib.apis.event_ctrl:
            await ecmodules.event_control.handler(client, user, operation, payload, db)
        elif api == eclib.apis.meeting_ctrl:
            if operation == "init":
                await ecsocket.send_by_client({"api": eclib.apis.meeting_ctrl, "rooms": len(ecusers.User.rooms)}, client)
        else:
            await ech.send_error(client)
    elif api == eclib.apis.main and operation == "get":
        tablist = user.get_tablist()
        await ecsocket.send_by_client({"api": eclib.apis.main, "name": user.name, "role": user.role, "tablist": tablist}, client)
        for api in user.get_apis():
            await echandle(client, user, api, "get", None)
        await ecmodules.queue.push_update(db, client, user)
    else:
        await ech.send_error(client)


async def handler(client, _path):
    """
    Immediate function called when WebSocket payload received

    :param client: client that sent payload
    :type client: websockets.WebSocketCommonProtocol
    :type _path: str
    """
    try:
        async for message in client:
            try:
                payload = json.loads(message)
            except json.JSONDecodeError:
                await ech.send_error(client)
                return
            if (extracted := await ech.safe_extract(client, payload, {"api": str, "operation": str})) is not None:
                if extracted["api"] == eclib.apis.login and extracted["operation"] == "login":
                    if (passcode := await ech.safe_extract(client, payload, {"accessCode": str})) is not None:
                        success = False
                        for user in ecusers.User.userlist:
                            if passcode == user.passcode:
                                success = True
                                print("[LOGIN] " + user.name)
                                ecsocket.unregister(client)
                                ecsocket.register(client, user)
                                await echandle(client, user, eclib.apis.main, "get", None)
                                break
                        if not success:
                            await ecsocket.send_by_client({"api": eclib.apis.login, "failure": True}, client)
                else:
                    if (user := find_user_from_client(client)) is not None:
                        await echandle(client, user, extracted["api"], extracted["operation"], payload)
                    else:
                        await ech.send_error(client)
                        return
    except websockets.ConnectionClosed:
        pass
    finally:
        ecsocket.unregister(client)
