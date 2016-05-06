#Command
# -*- coding: utf-8 -*-
# by Mathtin and Plaguedo

import engine as vk
import random, json
from urllib.request import urlopen
from urllib.parse import urlencode

PREFIX = '#!'

class react_cmd(vk.reaction):

    key = 'cmd'

    def __init__(self, allowed_users):
        vk.reaction.__init__(self, allowed_users)
        self.description = {}
        self.description["about_cmd"] = "Command format: #!command [args]\n\
Example: #!help\n\
Choose section\n\
Example: #!help basic\n\
Available sections: all"
        self.description["basic"] = "Basic:\n\
#!help [section] - about [section]\n\
#!version - show version\n\
#!getanswer - test command\n\
#!rand A - generate random integer modulo A\n\
#!rand A B - generate random integer between A and B (A<=B)"
        self.description["useful"] = "Useful:\n\
#!weather [city] - show current weather [city], default - Moscow (by OpenWeatherMap)\n\
#!kuantan - recieve IP-adress of kuantan\n"

    def check_update(self, bot, update):
        if not(self.is_allowed(bot,update)) or\
            update['type'] != vk.NEWMESSAGE or\
            bot.has_flag("OUTBOX", update) or\
            update['message'][:2] != PREFIX:
            return False
        msg = update['message'][2:]
        userID = update['user_id']
        chatID = update['chat_id']
        #Parsing quots
        temp = msg.split("&quot;")
        argv = []
        for i in range(len(temp)):
            if (i + 1) % 2 == 1:
                array = temp[i].split(" ")
                for arg in array:
                    if arg: argv.append(arg)
            elif temp[i]: 
                argv.append(temp[i])
        argc = len(argv)
        bot.log("cmd \"" + str(argv[0]) + "Args" + str(argv[1:]), 2)
        args = (bot, argv, userID, chatID)
        kwargs = {}
        if self.call_ext( args, kwargs ): return True
        #Commands with arguments
        #WEATHER
        #bot.send_message("", to = chatID)
        if argv[0] == "weather":
            if argc == 1:
                bot.send_message(currentWeather("Moscow"), to = chatID)
            else:
                bot.send_message(currentWeather(argv[1]), to = chatID)
        #AHTUNG
        elif argv[0] == "ahtung" or argv[0] == "aht":
            if argc < 3:
                bot.send_message("Statement expected, usage: #!aht[ung] group \"message\"", to = chatID)
            else:
                user_list = []
                if argv[1] == "corrupted":
                    user_list = vk.__team_ids__
                elif argv[1] == "stars":
                    user_list = vk.__team_ids__
                elif argv[1] == "root":
                    user_list = bot.get_root_list()
                else:
                    bot.send_message("Nothing matches to " + argv[1], to = chatID)
                if not(userID in user_list):
                    bot.send_message("You are not a member of " + argv[1], to = chatID)
                    return True
                bot.log("Important message: " + argv[2], 1)
                bot.log("For users: " + ",".join(str(x) for x in user_list), 1)
                bot.log("Group: " + argv[1], 1)
                bot.send_message("<АХТУНГ, " + argv[1] + ">\n" + argv[2] + "\n</АХТУНГ>", to = user_list)
        #RANDOM
        elif argv[0] == "rand":
            if argc == 1:
                bot.send_message("Statement expected", to = chatID)
            elif argc == 2:
                if not(argv[1].isdigit()):
                    bot.send_message("Number expected", to = chatID)
                else:
                    bot.log("request for RAND: \"" + msg + "\"", 1)
                    bot.send_message( random.randint(0, int(argv[1])), to = chatID)
            else:
                if not(argv[1].isdigit()) or not(argv[2].isdigit()):
                    bot.send_message("Numbers expected", to = chatID)
                elif int(argv[1]) > int(argv[2]):
                    bot.send_message("Wrong range", to = chatID)
                else:
                    bot.log("request for RAND: \"" + msg + "\"", 1)
                    bot.send_message( random.randint(int(argv[1]), int(argv[2])), to = chatID)
        #Commands with no arguments
        elif argv[0] =="getanswer":
            bot.send_message("Na tebe answer D:<", to = chatID)
        elif argv[0] == "killyourself":
            bot.send_message("Noooooooooo!!!", to = chatID)
        elif argv[0] == "lukeiamyourfather":
            bot.send_message("I love you too, Daddy <3", to = chatID)
        elif argv[0] == "kuantan":
            bot.send_message(bot.getIP(), to = chatID)
        elif argv[0] == "version":
            bot.send_message("Best Chat Bot Ever by Plaguedo and Mathtin " + vk.__version__ + "\n\
Bot Name " + bot.get_name() + "\n\
Coded for Python 3.4.3\n\
Special thanks to Alexey Kuhtin", to = chatID)
        elif argv[0] == "help":
            help = bot.get_descriptions()
            if argc == 1:
                msg = self.description["about_cmd"]
                for s in help:
                    if s != "none" and s != "about_cmd":
                        msg += ", " + s 
                bot.send_message(msg, to = chatID)
            else:
                if argv[1] == "all":
                    desc = ""
                    for s in help:
                        if s == "about_cmd": continue
                        if help[s][-1] != "\n": help[s] += "\n"
                        desc += help[s]
                    bot.send_message(desc, to = chatID)
                elif argv[1] in help:
                        bot.send_message(help[argv[1]], to = chatID)
                else: bot.send_message("No such section", to = chatID)
        elif argv[0] == "song":
            msg = ""
            if bot.is_root(userID):
                msg = "Послушай это:"
            else:
                msg = "Лови"
            audio = bot.recommended_audio(userID)
            if not(audio):
                bot.send_message("Похоже ты скрыл от меня свои предпочтения", to = chatID)
            else:
                bot.send_message("Похоже ты скрыл от меня свои предпочтения",
                    to = chatID,
                    attachment = audio
                )
        else:
            bot.send_message("No such command", to = chatID)
        return True

#OpenWeatherMap API
def currentWeather(city="Moscow"):
    method = "weather?%s"
    onsend = {
        'q': city,
        'appid' : "62f1e3d3433316a591fce9a975a037c5"
    }
    paramsonsend = urlencode(onsend)
    f = urlopen("http://api.openweathermap.org/data/2.5/" + method % paramsonsend)
    wt = json.loads(f.read().decode('utf-8'))
    wt_str = 'Current temperature ' + str(int(wt["main"]["temp"] - 273)) + ' °C ' + str(wt["weather"][0]["description"]) + '\nAtmospheric Pressure ' + str(int(wt["main"]["pressure"])) + ' mm\nHumanity ' + str(wt["main"]["humidity"]) + '%\nCity: ' + str(wt["name"])
    return wt_str
