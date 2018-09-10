import re
import string
import time
import yaml
import json
import requests
import sqlite3

bridge_server = 'irc.snt.utwente.nl'
room_format = '#_ircnet_.+:irc.snt.utwente.nl'
appservice_user = '@ircnet:irc.snt.utwente.nl'

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

access_token = cfg['token']
homeserver = cfg['server']

# find all rooms that have an alias matching given room format
rooms = requests.get(
        "{}/_matrix/client/r0/joined_rooms".format(homeserver),
        params={
            'access_token':access_token
        }).json()['joined_rooms']
print("Joined rooms: {}".format(rooms))

def is_ircnet_channel(room_id):
    try:
        aliases = requests.get(
                "{}/_matrix/client/r0/rooms/{}/state/m.room.aliases/{}".format(homeserver, room_id, bridge_server),
                params={
                    'access_token':access_token
                }).json()['aliases']
    except KeyError:
        return False
    for alias in aliases:
        if re.match(room_format, alias):
            return True
    return False

rooms = [room for room in rooms if is_ircnet_channel(room)]
print("IRCNet channels: {}".format(rooms))

# get all users in all those rooms that have IDs matching @_telegram_.+:hacklab.fi
ircnet_users = {}
for room in rooms:
    members = requests.get(
            "{}/_matrix/client/r0/rooms/{}/joined_members".format(homeserver, room),
            params={
                'access_token':access_token
                }).json()['joined']
    for member in members:
        if re.match('@_telegram_.+:hacklab.fi', member):
            ircnet_users[member] = members[member]
print("IRCNet users from Telegram: {}".format(ircnet_users))

## Change IRC nick:
def change_irc_nick(user, membership):
    print("Changing IRC nick for {} {}".format(user, membership))
    rooms = requests.get(
            "{}/_matrix/client/r0/joined_rooms".format(homeserver),
            params={
                'access_token': access_token,
                'user_id': user
            }).json()['joined_rooms']

    def is_ircnet_admin_room(room_id, user):
        members = requests.get(
                "{}/_matrix/client/r0/rooms/{}/joined_members".format(homeserver, room_id),
                params={
                    'access_token': access_token,
                    'user_id': user
                }).json()['joined']
        return user in members and appservice_user in members and len(members)==2

    ircnet_admin_rooms = [room for room in rooms if is_ircnet_admin_room(room, user)]
    print("Previous IRCNet admin rooms for {}: {}".format(user, ircnet_admin_rooms))

    if len(ircnet_admin_rooms) != 1:
        for room in ircnet_admin_rooms:
            # just leave all the previous admin rooms if they exist
            requests.post(
                    "{}/_matrix/client/r0/rooms/{}/leave".format(homeserver, room),
                    params={
                        'access_token': access_token,
                        'user_id': user
                    })
        adminroom = requests.post(
                "{}/_matrix/client/r0/createRoom".format(homeserver),
                params={
                    'access_token': access_token,
                    'user_id': user
                },
                # this payload is just copied straight from Riot
                json={
                    'preset':'trusted_private_chat',
                    'visibility':'private',
                    'invite':[appservice_user],
                    'is_direct':True,
                    'initial_state':[{
                        'content':{'guest_access':'can_join'},
                        'type':'m.room.guest_access',
                        'state_key':''
                    }]})
        room_id = adminroom.json()['room_id']
    else:
        print("Reusing admin room")
        room_id = ircnet_admin_rooms[0]

    time.sleep(2)
    while appservice_user not in requests.get("{}/_matrix/client/r0/rooms/{}/joined_members".format(homeserver, room_id), params={'access_token': access_token, 'user_id': user}).json()['joined']:
        requests.post(
                "{}/_matrix/client/r0/rooms/{}/invite".format(homeserver, room_id),
                params={
                    'access_token': access_token,
                    'user_id': user
                },
                json={
                    'user_id': appservice_user
                })
        time.sleep(2)
    tgid = int(re.match('^@_telegram_([-0123456789]+):hacklab\.fi$', user)[1])
    txnid = str(time.time())
    requests.put(
            "{}/_matrix/client/r0/rooms/{}/send/m.room.message/{}".format(homeserver, room_id, txnid),
            params={
                'access_token': access_token,
                'user_id': user
            },
            json={
                'msgtype': 'm.text',
                'body': "!nick {}".format(ircify_displayname(get_telegram_name(tgid, membership['display_name'])))
            })             

def get_telegram_name(tgid, displayname):
    conn = sqlite3.connect(cfg['mautrix_telegram_db'])
    username = conn.execute('select username from puppet where id=?', (tgid,)).fetchone()[0]
    print("Username for {} is {}".format(tgid, username))
    if username == None:
        return re.sub(' \[TG\]$', '', displayname)
    else:
        return username

## ircify displayname
# take Matrix displayname and remove all invalid IRC characters
def ircify_displayname(displayname):
    print("ircifying name {}".format(displayname))
    allowed = string.ascii_letters+string.digits+'_-\[]{}^`|'
    ircified = "".join(list(filter(allowed.__contains__, displayname)))
    ircified = ircified.lstrip('-0123456789')

    ircified = ircified[:12]
    ircified += '[t]'
    print("ircified name is {}".format(ircified))

    return ircified

# for each of those users: change IRC nick to ircified telegram displayname
for user, membership in ircnet_users.items():
    change_irc_nick(user, membership)
