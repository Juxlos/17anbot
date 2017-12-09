#   JuxRPGBot
#   Version 0.0.0.1 (9 December 2017)
#   Initially developed for Indonesian Independence celebration on 17-Aug-2018
#   In /r/Indonesia Discord Server (http://discord.gg/indonesia)
#   Replace Indonesian language script in this file and rpg_stats.json as needed
#   For weapon accuracy, see {put link here}


import random
import math
import json
import matplotlib.pyplot as plt
import discord
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
        
async def attack(message, target, weapon):
    verb = get_word(weapon)
    await bot.send_message(message.channel, "{1} dengan senjata {0}...".format(weapon, verb[0]))
    weapon = weapons_base[weapon]
    a = damage(weapon, 'a', weapon['range'])
    print(a)
    if len(a) == 0:
        msg = "Peluru anda habis!"
    elif max(a) == 0:
        msg = "{0} anda meleset!".format(verb[2])
    else:
        msg = "{1} kena {0} kali!".format(len(a), verb[2])
    await bot.send_message(message.channel, msg)
    return a
    

@bot.event
async def on_message(message):
    if message.author.id != bot.user.id and message.channel.id in ['339706179213328385', '186588826234257408']:
        #   Synonyms
        if message.content in [';battle', ';enterbattle', ';enter_battle', ';fight', ';war']:
            if message.author.id in list(users.keys()):
                pass
            else:
                await bot.send_message(message.channel, '{0}, tolong daftar dulu')


@bot.event
async def on_ready():
    print(bot.user.name)
    print(bot.user.id)
    

bot.run(configid.old_token)
