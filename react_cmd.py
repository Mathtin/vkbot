#Command
# -*- coding: utf-8 -*-
# by Mathtin and Plaguedo

import engine
import random, json
from urllib.request import urlopen
from urllib.parse import urlencode

class react_cmd(engine.reaction):
    def __init__(self, allowed_users):
        engine.reaction.__init__(self, allowed_users)
        
    def get_key(self): return 'cmd'
    
    def rule(self, sender, update):
        if update['type'] == 4 and not(update['flags']['out']) and update['message'][:2] == '#!':
            return True
        return False

    def pars_func(self, sender, update):
        msg_struct = sender.createMsgStruct(update)
        msg = update['message']
        userID = update['user_id']
        chatID = update['chat_id']
        #Parsing quots
        temp=msg.split("&quot;")
        command=[]
        for i in range(len(temp)):
            if (i + 1) % 2 == 1:
                array = temp[i].split(" ")
                for arg in array:
                    if arg != "":
                        command.append(arg)
            else:
                command.append(temp[i])
        command_len=len(command)
        if sender.get_log_level()  >= 2:
            for i in range(command_len):
                if command[i] == "": 
                    del command[i]
                    i -= 1
                    command_len -= 1
                else: sender.get_shouter()("Arg[" + str(i) + "]=\"" + command[i] + "\"")
        #Commands with arguments
        #WEATHER
        if command[0] == "#!weather":
            if command_len == 1:
                msg_struct["message"] = currentWeather("Moscow")
            else:
                msg_struct["message"] = currentWeather(command[1])
        #AHTUNG
        elif command[0] == "#!ahtung" or command[0] == "#!aht":
            if command_len < 3:
                msg_struct["message"] = "Statement expected, usage: #!aht[ung] group message"
            else:
                user_list = []
                if command[1] == "corrupted":
                    user_list = [ '24799071', '185952294' ]
                elif command[1] == "stars":
                    user_list = [ '24799071', '185952294' ]
                elif command[1] == "root":
                    user_list = [ '24799071', '185952294' ]
                else:
                    msg_struct["message"] = "Nothing matches to " + command[1]
                    return msg_struct
                sender.get_shouter()("To group: " + command[1] + '\n')
                command = command[2:]
                if 'user_id' in msg_struct: del msg_struct['user_id']
                elif 'chat_id' in msg_struct: del msg_struct['chat_id']
                msg = " ".join(command)
                sender.get_shouter()("Important message: " + msg + '\n')
                sender.get_shouter()("To users: " + ",".join(user_list) + '\n')
                msg_struct['user_ids'] = ",".join(user_list)
                msg_struct["message"] = u'[АХТУНГ]\n' + msg + u'\n[/АХТУНГ]'
        #RANDOM
        elif command[0] == "#!rand":
            if command_len == 1:
                msg_struct["message"] = "Statement expected"
            elif command_len == 2:
                if not(command[1].isdigit()):
                    msg_struct["message"] = "Number expected"
                else:
                    if sender.get_log_level() >= 1:
                        sender.get_shouter()("request for RAND: \"" + msg + "\"")
                    msg_struct["message"] = str(random.randint(0, int(command[1])))
            elif command_len == 3:
                if not(command[1].isdigit()) or not(command[2].isdigit()):
                    msg_struct["message"] = "Numbers expected"
                elif int(command[1]) > int(command[2]):
                    msg_struct["message"] = "Wrong range"
                else:
                    if sender.get_log_level() >= 1:
                        sender.get_shouter()("request for RAND: \"" + msg + "\"")
                    msg_struct["message"] = random.randint(int(command[1]), int(command[2]))
            else:
                msg_struct["message"] = "Too much statements"
        #Commands with no arguments
        elif command[0] =="#!getanswer":
            msg_struct["message"] = "Na tebe answer D:<"
        elif command[0] == "#!killyourself":
            msg_struct["message"] = "Noooooooooo!!!"
        elif command[0] == "#!lukeiamyourfather":
            msg_struct["message"] = "I love you too, Daddy <3"
        elif command[0] == "#!kuantan":
            msg_struct["message"] = sender.getIP()
        elif command[0] == "#!version":
            msg_struct["message"] = "Best Chat Bot Ever by Plaguedo and Mathtin " + engine.ver() + "\n\
Bot Name " + sender.get_name() + "\n\
Coded for Python 3.4.3\n\
Special thanks to Alexey Kuhtin"
        elif command[0] == "#!help":
            msg_struct["message"] =  "Command format: #!command [args]\n\
Example: #!help\n\
Basic:\n\
#!help - show this message\n\
#!version - show version\n\
#!getanswer - test command\n\
#!rand A - generate random integer modulo A\n\
#!rand A B - generate random integer between A and B (A<=B)\n\
Useful:\n\
#!weather [city] - show current weather [city], default - Moscow (by OpenWeatherMap)\n\
#!kuantan - recieve IP-adress of kuantan\n"
        elif command[0] == "#!song":
            if sender.is_root(userID):
                msg_struct["message"] = "Послушай это:"
            else:
                msg_struct["message"] = "Лови"
            attachment = sender.attachRecommendedAudio(userID)
            if not(attachment):
                msg_struct["message"] = "Похоже ты скрыл от меня свои предпочтения"
            else: 
                msg_struct["attachment"] = attachment
        else:
            msg_struct["message"] = "No such command"
        return msg_struct

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
