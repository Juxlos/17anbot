#   JuxRPGBot
#   Version 0.0.0.1 (9 December 2017)
#   Initially developed for Indonesian Independence celebration on 17-Aug-2018
#   In /r/Indonesia Discord Server (http://discord.gg/indonesia)
#   Replace Indonesian language script in this file and rpg_stats.json as needed
#   For weapon accuracy, see {put link here}


import random
import math
import json
import time
import matplotlib.pyplot as plt
import discord
import asyncio
import configid


bot = discord.Client()


#   Imports user information and datasets (damage, weapons, scripts, etc)
with open("rpg_stats.json") as w:
    rpg_stats = json.load(w)


with open("users.json") as u:
    users = json.load(u)


#   Variables from the json dics
weapons_base = rpg_stats["weapons_base"]


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


#   To be invoked whenever the variable users need to be updated semi-permanently
#   e.g. completing missions, getting killed, buying things, etc.
def write_user_data():
    with open("users.json", "w") as u:
        json.dump(users, u, indent=4, separators=(', ',': '))


def weightedpick(dictionary):
    r = random.uniform(0, sum(dictionary.values()))
    s = 0.0
    for k, w in dictionary.items():
        s += w
        if r < s: return k
    return k


def damage(weapon, target, distance):
    #   Fairly accurate as long as distance below range
    #   After that drops off
    hit_chance = (0.5*(math.tanh(math.exp(0.9)-(distance/weapon["range"]))+1))**4
    mod = int(100000*hit_chance)
    #   Either shoot bullets as defined or shoot what's left
    hit_count = min([random.choice(weapon["hits"]), weapon["ammo"]])
    hits = []
    shots_fired = 0
    while shots_fired < hit_count:
        if random.randint(0, 100000) < mod:
            hits.append(weapon["damage_to_human"])
        else:
            hits.append(0)
        shots_fired += 1
    return hits


def get_word(weapon):
    if weapons_base[weapon]['type'] is not "MELEE":
        verb = ["Menembak", "tembak", "Tembakan"]
    else:
        verb = ["Menyerang", "serang", "Serangan"]
    return verb


async def combat_phase(message, stage):
    #   Stage stats
    ststats = rpg_stats['stages'][stage]
    target = weightedpick(ststats["enemies"])
    #   Random distance between proximity_max and 2 times that - most likely 1.5 times
    distance = int(random.triangular(ststats["proximity_max"], 2*ststats["proximity_max"]))
    await bot.send_message(message.channel, "Terlihat di jarak {0} meter seorang {1}...".format(str(distance), target))


#   Saves typing it multiple times
def quit_battle(playerid):
    users[playerid]["in_battle"] = False


async def battle(message, time_limit = 150, stage = "default"):
    name = message.author.name
    #   To prevent patrolling... message spam
    already_sent_patrol = False
    player_id = message.author.id
    player = users[message.author.id]
    await bot.send_message(message.channel, '{0} mulai bergerak...'.format(name))
    while time_limit > 0:
        if random.random() < rpg_stats["stages"][stage]["density"]:
            #   10 minutes allocated to encounter and combat
            time_limit -= 10
            already_sent_patrol = False
            await bot.send_message(message.channel, "{0} bertemu musuh!".format(name))
            #   Ambush roll - player shoots first because they're the player but this is the chance to attack undetected
            await combat_phase(message, stage)
        else:
            time_limit -= 6
            if already_sent_patrol is False:
                await bot.send_message(message.channel, "{0} terus berpatroli...".format(name))
                already_sent_patrol = True
        await asyncio.sleep(0.3)
    await asyncio.sleep(0.5)
    await bot.send_message(message.channel, 'Patroli {0} selesai!'.format(name))
    quit_battle(player_id)


@bot.event
async def on_message(message):
    if message.author.id != bot.user.id and message.channel.id in ['339706179213328385', '186588826234257408']:
        #   Synonyms
        if message.content in [';battle', ';enterbattle', ';enter_battle', ';fight', ';war']:
            if message.author.id not in list(users.keys()):
                users[message.author.id] = {
                    "in_battle": True,
                    "weapons":  {
                        "RIFLE": "Arisaka 38",
                        "PISTOL": "Nambu Type 14",
                        "MELEE": "Bambu Runcing"
                    },
                    #   [Current, Max]
                    "HP":   [100, 100],
                    "magazines":    {
                        "PISTOL": 5,
                        "MELEE": 9999999999999
                    },
                    "last_patrol": 0
                }
                await bot.send_message(message.channel, '{0} telah menerima senjata.'.format(message.author.name))
            await battle(message)
            users[message.author.id]['last_patrol'] = time.time()
            write_user_data()

@bot.event
async def on_ready():
    #   Ensures all in_battle is False
    for u in list(users.keys()):
        users[u]["in_battle"] = False
    write_user_data()
    print(bot.user.name)
    print(bot.user.id)

bot.run(configid.old_token)
