# Ask Reaction
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

class react_ask(vk.reaction):

    key = 'ask'
    
    description = { 'ask': 'Попробуй задать мне вопрос'}

    def check_update(self, bot, update):
        if update['type'] != vk.NEWMESSAGE or update['message'] == '':
            return False
        question = update['message'][-1] == "?"
        appeal = bot.get_name() in update['message']
        if  bot.has_flag("OUTBOX", update) or\
            not(question) or\
            ( bot.has_flag("CONFERENCE", update) and not(appeal) ):
            return False
        msg = update['message']
        random.seed(msg)
        if (u'Почему' in msg) or (u'почему' in msg) or (u'Why' in msg) or (u'why' in msg):
            msg = ["Так сложились звезды", "Потому что гладиолус", "Это очевидно", "Догодайся", "Откуда я знаю?", "Обратись к знающим", "Ты в курсе"]
        elif (u'Где' in msg) or (u'где' in msg) or (u'Where' in msg) or (u'where' in msg):
            msg = ["Не здесь", "Где-то далеко", "Там же, где и истина", "Там", "Тут", "В Караганде", "Столь далеко, что близко. Столь высоко, что низко..."]
        else:
            msg = ["Безусловно это правда", "Такого не может быть", "Да", "Нет", "Может быть", "Не уверена", "Соглашусь с тобой", "Не могу с тобой согласиться", "Возможно", "Вряд ли", "Я промолчу"]
        g = random.randint(0, len(msg) - 1)
        bot.send_message(msg[g], to = update['chat_id'])
        return True
