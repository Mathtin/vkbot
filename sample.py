#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###################################################
#........../\./\...___......|\.|..../...\.........#
#........./..|..\/\.|.|_|._.|.\|....|.c.|.........#
#......../....../--\|.|.|.|i|..|....\.../.........#
#        Mathtin (c)                              #
###################################################
#	Author: Daniil [Mathtin] Shigapov             #
#	Contributors: Plaguedo                        #
#   Copyright (c) 2017 <wdaniil@mail.ru>          #
#   This file is released under the MIT license.  #
###################################################
    
__author__ = "Mathtin, Plaguedo"
__date__ = "$05.11.2015 17:43:27$"

import sys, time
from http.client import BadStatusLine
#Import main engine and extensions
from engine      import VKBot
from react_cmd   import react_cmd, PREFIX
from react_ask   import react_ask
from react_sign  import react_sign

@react_cmd.command("send")
def send_cmd(cmd_handler, argc, argv, bot, userID, chatID):
    USAGE = "{0}send [reciever id] \"MESSAGE\"".format(PREFIX)
    if argc < 3:
        bot.send_message(USAGE, to = chatID)
    else:
        reciever = bot.get_user_info(argv[1])
        if "error" in reciever:
            bot.send_message("Failed: " + reciever["error"]["error_msg"], to = chatID)
        else:
            answer = bot.send_message( argv[2], to = argv[1] )
            if "error" in answer:
                bot.send_message("Failed: " + answer["error"]["error_msg"], to = chatID)
            else:
                bot.send_message("Message for {fn} {ln} sent".format(
                    fn=reciever["first_name"], ln=reciever["last_name"] ), to = chatID)
    return True
react_cmd.description["useful"] += "{0}send [reciever id] \"MESSAGE\" - send anon message to reciever by bot\n".format(PREFIX)

@react_cmd.command("myid")
def myid_cmd(cmd_handler, argc, argv, bot, userID, chatID):
    bot.send_message("Your id: " + str(userID), to = chatID)
    return True
react_cmd.description["useful"] += "{0}myid - return your VK id!\n".format(PREFIX)

def log(message):
    print(time.strftime('%H:%M:%S ') + message)

def main():
    #Setting up
    root_list = [
        24799071
    ]
    #Sequential list of reaction
    reactions = [
        react_cmd ( allowed_users = "all" ),  #1. Command
        react_ask ( allowed_users = "all" ),  #2. Ask y/n
        react_sign( allowed_users = "all" )   #3. Signature
    ]
    #Access token
    smtoken = "000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
    #Initialising Bot
    bb = VKBot(reactions, "Big Brother", smtoken, root_list, log_to = log)
    #Increase amount of debug data
    bb.set_logger(log_level = 1)
    #Requesting for Long Poll Server
    bb.connect()
    bb.listen()
    print ("Closing program")
	
if __name__ == "__main__":
    main()
