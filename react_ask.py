#Ask
# -*- coding: utf-8 -*-
# by Mathtin and Plaguedo

import engine
import random
import re

class react_ask(engine.reaction):
    def __init__(self, allowed_users):
        engine.reaction.__init__(self, allowed_users)
        
    def get_key(self): return 'ask'
    
    def rule(self, sender, update):
        if update['type'] != 4 or update['flags']['out']:
            return False
        arr_msg = list(update['message'])
        question = arr_msg[-1] == "?"
        appeal = sender.get_name() in update['message']
        if question and (update['user_id'] == update['chat_id'] or appeal):
            return True
        else:
            return False

    def pars_func(self, sender, update):
        msg_struct = sender.createMsgStruct(update)
        msg = update['message']
        random.seed(msg)
        if (u'Почему' in msg) or (u'почему' in msg) or (u'Why' in msg) or (u'why' in msg):
            msg = ["Так сложились звезды", "Потому что гладиолус", "Это очевидно", "Догодайся", "Откуда я знаю?", "Обратись к знающим", "Ты в курсе"]
        elif (u'Где' in msg) or (u'где' in msg) or (u'Where' in msg) or (u'where' in msg):
            msg = ["Не здесь", "Где-то далеко", "Там же, где и истина", "Там", "Тут", "В Караганде", "Столь далеко, что близко. Столь высоко, что низко..."]
        else:
            msg = ["Безусловно это правда", "Такого не может быть", "Да", "Нет", "Может быть", "Не уверена", "Соглашусь с тобой", "Не могу с тобой согласиться", "Возможно", "Вряд ли", "Я промолчу"]
        g = random.randint(0, len(msg) - 1)
        msg_struct["message"] = msg[g]
        return msg_struct
