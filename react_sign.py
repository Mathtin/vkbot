# Sign Reaction
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

__author__  = "Mathtin, Plaguedo"
__date__    = "$05.11.2015 17:43:27$"

import engine as vk
import random
import re

class react_sign(vk.reaction):

    key = 'sign'
    
    def __init__(self, allowed_users):
        vk.reaction.__init__(self, allowed_users)
        self.signatures = {
            vk.__mathtin_id__: "Ваше сеятельство, о великий Император Даниил IV",
            vk.__plaguedo_id__: "Ваш чай готов, Сенпай"
        }
        
    def signature_in(self, msg):
        for id in self.signatures:
            if self.signatures[id] in msg:
                return True
        return False

    def __call__(self, bot, updates):
        for update in updates:
            if update['type'] != vk.NEWMESSAGE or\
                not(bot.has_flag("OUTBOX", update)) or\
                not update['user_id'] in self.signatures or\
                self.signature_in(update['message']):
                continue
            bot.send_message(self.signatures[update['user_id']], to = update['chat_id'])
            return True
        return False
