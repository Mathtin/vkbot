# VK Bot Engine Source File
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
    
#ARBUZZZZ
__author__      = "Mathtin, Plaguedo"
__date__        = "$05.11.2015 17:43:27$"
__version__     = "4.1.0c"
__mathtin_id__  = 24799071
__plaguedo_id__ = 185952294
__team_ids__    = [__mathtin_id__, __plaguedo_id__]
__vkapi__       = "https://api.vk.com/method/"

#import standart modules
from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError
import json, copy, time

NEWMESSAGE = 4

class VKBot:
    def __init__(self, reactions, bot_name, token, root_list = [], vk_group_id = 101594097, log_to = lambda *args: None):
        log_to("Creating bot " + bot_name)
        self.__reactions = reactions
        self.__name = bot_name
        self.__access_token = token
        self.__root_list = copy.copy(root_list)
        self.__vkgroup = vk_group_id
        #Long Poll Connection Info
        self.__longpoll = {
            'key': "",
            'server': "",
            'ts': 0
        }
        #Debug print function (usually print)
        self.__shout = log_to
        #Debug amount of info (lower level - less info)
        self.__log_level = 0
        self.__connected = False
        self.__active = False
        self.last_updates = []
            
    def get_root_list(self):
        return copy.copy(self.__root_list)
    def get_vkgroup(self):
        return self.__vkgroup
    def get_name(self):
        return self.__name
    def get_log_level(self):
        return self.__log_level
    def log(self, log_msg, log_lvl = 0):
        if self.__log_level >= log_lvl:
            self.__shout(log_msg)
    def get_root_list(self):
        return copy.copy(self.__root_list)
        
    def get_descriptions(self):
        description = {}
        for react in self.__reactions:
            for section in react.description:
                if section != "none":
                    description[section] = react.description[section]
        return description
        
    def is_root(self, id):
        return id in self.__root_list
        
    def is_connected(self):
        return self.__connected
        
    def is_active(self):
        return self.__active
    
    #Define amount of debug info and change print function
    def set_logger(self, callback = None, log_level = None):
        if callback: self.__shout = callback
        if log_level: self.__log_level = log_level
        
    #Server Connection
    def connect(self, reconnect = False):
        method = "messages.getLongPollServer?%s"
        onsend = {
            'use_ssl': 1,
            'access_token': self.__access_token
        }
        paramsonsend = urlencode(onsend)
        if not(reconnect): self.__shout("Connecting to Longpoll server...")
        f = urlopen(__vkapi__ + method % paramsonsend)
        answer = f.read().decode("utf-8")
        longpoll_info = json.loads(answer)
        #Updating long poll server info
        self.__longpoll['key'] = longpoll_info["response"]["key"]
        self.__longpoll['server'] = longpoll_info["response"]["server"]
        self.__longpoll['ts'] = longpoll_info["response"]["ts"]
        self.__lp_server = "https://" + self.__longpoll['server'] + "?%s"
        self.__lp_request = {
            'act': "a_check",
            'key': self.__longpoll['key'],
            'ts': self.__longpoll['ts'],
            'wait': 20,
            'mode': 2
        }
        self.__connected = True
        if not(reconnect):
            if self.__log_level >= 2: 
                self.__shout("connection: " + answer)
            else: 
                self.__shout("Connected to " + self.__longpoll['server'] + " with ts " + str(self.__longpoll['ts']))
        return answer

    def a_check(self):
        if not( self.__connected ):
            raise Exception("NO CONNECTION")
        paramsonsend = urlencode(self.__lp_request)
        server = "https://" + self.__longpoll['server'] + "?%s"
        f = None
        try: 
            f = urlopen(server % paramsonsend)
        except HTTPError:
            self.connect( reconnect = True )
            return self.a_check()
        answer = f.read().decode("utf-8")
        self.log("LongPoll: " + answer, 3)
        if not( is_json(answer) ): 
            self.__connected = False
            self.__active = False
            raise ConnectionResetError('VK Long Poll server dropped')
        dec = json.loads(answer)
        if "failed" in dec:
            if dec["failed"] == 1:
                self.__longpoll['ts'] = dec["ts"]
            elif dec["failed"] == 2 or dec["failed"] == 3:
                self.connect( reconnect = True )
                return self.a_check()
            else:
                self.__connected = False
                self.__active = False
                raise ConnectionResetError('Something went wrong')
        return answer
        
    def listen(self):
        if not( self.__connected ):
            raise Exception("NO CONNECTION")
        self.__active = True
        while self.__active:
            answer = self.a_check()
            self.parse_answer(answer)
            try:
                self.send_last_updates()
            except ManualDrop:
                self.__active = False
                self.log("Manual Drop")
            

    #Message Manipulation
    def parse_answer(self, answer):
        decoded_string = json.loads(answer)
        #Updating TS
        self.__longpoll['ts'] = decoded_string["ts"]
        self.__lp_request['ts'] = self.__longpoll['ts']
        self.last_updates = []
        #Creating list of updates
        for update_raw in decoded_string["updates"]:
            update = { 
                'type': update_raw[0],    #type of update
                'raw': update_raw,        #raw data
                'flags': update_raw[2]    #data flags
            }
            if update['type'] == 4:
                update['message'] = update_raw[6]
                chatID = update_raw[3]
                userID = chatID
                if chatID >= 2000000000:
                    userID = int(update_raw[7]["from"])
                update['chat_id'] = chatID
                update['user_id'] = userID
                if not( self.has_flag("OUTBOX", update) ) and self.__log_level >= 2:
                    self.__shout('Message "' + update['message'] + '" recieved from ' + str(userID))
                if self.has_flag("OUTBOX", update) and self.__log_level >= 1:
                    self.__shout("Message sent")
            self.last_updates.append(update)
        
    def send_last_updates(self):
        for r in self.__reactions:
            r(self, self.last_updates)
        
        
    flags = {
        'CONFERENCE' : 2**13,
        'MEDIA'      : 2**9,
        'FIXED'      : 2**8,
        'DELЕTЕD'    : 2**7,
        'SPAM'       : 2**6,
        'FRIENDS'    : 2**5,
        'CHAT'       : 2**4,
        'IMPORTANT'  : 2**3,
        'REPLIED'    : 2**2,
        'OUTBOX'     : 2**1,
        'UNREAD'     : 2**1
    }
        
    @staticmethod
    def has_flag(flag, update):
        if not(flag in VKBot.flags):
            return False
        return update["flags"] == update["flags"] | VKBot.flags[flag]
    
    def send_msg_struct(self, msg_struct):
        method = "messages.send?%s"
        paramsonsend = urlencode(msg_struct)
        self.log("Sending message...", 1)
        f = urlopen(__vkapi__ + method % paramsonsend)
        answer = f.read().decode("utf-8")
        self.log("Sending:" + answer, 2)
        time.sleep(0.334)
        if is_json(answer) and "error" in answer:
            decoded_string = json.loads(answer)
            self.log("Server: " + decoded_string["error"]["error_msg"], 1)
            if decoded_string["error"]["error_code"] == 9:
                self.log("Editing message...", 1)
                msg_struct["message"] = "Oх...\n" + msg_struct["message"]
                self.send_msg_struct(msg_struct)
        return json.loads(answer)
        
    def send_message(self, msg, to, attachment = None):
        msg_struct = {
            'message': msg,
            'access_token': self.__access_token
        }
        if attachment:
            msg_struct["attachment"] = attachment
        if not( isinstance(to, str) or isinstance(to, int) or isinstance(to, list) ):
            raise TypeError("WRONG TYPE OF ARGUMENT 'to'")
        if isinstance(to, str) and to.isdigit():
            to = int(to)
        if isinstance(to, list):
            for id in to:
                if not( isinstance(id, str) or isinstance(id, int) ):
                    raise TypeError("WRONG TYPE(S) OF ID(S) IN 'to'")
            msg_struct['user_ids'] = ",".join(str(x) for x in to)
        elif isinstance(to, str):
            user_info = self.get_user_info(to)
            if "error" in user_info:
                raise Exception(user_info["error"]["error_msg"])
            msg_struct['user_id'] = user_info["uid"]
        elif to > 2000000000:
            msg_struct['chat_id'] = to - 2000000000
        else:
            msg_struct['user_id'] = to
        return self.send_msg_struct(msg_struct)
        
    @staticmethod
    def get_user_info(id_from):
        method = "users.get?%s"
        paramsonsend = urlencode({ 'user_ids': id_from, 'fields': "domain" })
        #self.log("Getting user info...", 2)
        f = urlopen(__vkapi__ + method % paramsonsend)
        answer = f.read().decode("utf-8")
        decoded_string = json.loads(answer)
        if "error" in decoded_string:
            return decoded_string
        return decoded_string["response"][0]
        
    @staticmethod
    def get_group_info(id_from):
        method = "groups.getById?%s"
        paramsonsend = urlencode({ 'group_ids': id_from })
        #self.log("Getting user info...", 2)
        f = urlopen(__vkapi__ + method % paramsonsend)
        answer = f.read().decode("utf-8")
        decoded_string = json.loads(answer)
        if "error" in decoded_string:
            return decoded_string
        return decoded_string["response"][0]
        
    #Extensions
    #Get Attachments
    def recommended_audio(self, id_from):
        method = "audio.getRecommendations?%s"
        onsend = {
            'user_id': id_from,
            'offset': 2,
            'count': 50,
            'shuffle': 1,
            'access_token': self.__access_token
        }
        paramsonsend = urlencode(onsend)
        self.log("Getting recommendations...", 1)
        f = urlopen(__vkapi__ + method % paramsonsend)
        answer = f.read().decode("utf-8")
        self.log("recommended_audio: " + answer, 2)
        decoded_string = json.loads(answer)
        if "error" in answer:
            self.log("Server: " + decoded_string["error"]["error_msg"], 1)
            return None
        else:
            print (decoded_string["response"])
            owner = decoded_string["response"][0]["owner_id"]
            id = decoded_string["response"][0]["aid"]
            attachment = "audio" + str(owner) + "_" + str(id)
            return attachment

    #VK API (Kuantan IP)
    def getIP(self):
        method = "status.get?%s"
        onsend = {
            'group_id': self.__vkgroup,
            'access_token': self.__access_token
        }
        self.log("Getting IP of kuantan...", 1)
        paramsonsend = urlencode(onsend)
        f = urlopen(__vkapi__ + method % paramsonsend)
        answer = f.read().decode("utf-8")
        self.log("getIP: " + answer, 2)
        if not(is_json(answer)):
            return "Error"
        decoded_string = json.loads(answer)
        if "error" in decoded_string:
            self.log("Server: " + decoded_string["error"]["error_msg"], 1)
            return "Error"
        else:
            return decoded_string["response"]["text"]
        
        
class reaction:
    
    description = {'none': 'nothing'}
    
    def __getitem__(self, index):
        return getattr(self, index)
        
    def __init__(self, allowed_users):
        self.__users = allowed_users
        self.__ext = []
        
    def is_allowed(self, bot, update):
        return self.__users == "all" or\
            (self.__users == "friends" and VKBot.has_flag("FRIENDS", update)) or\
            (self.__users == "root"    and bot.is_root(update['user_id']))
            
    def add_extension(self, ext):
        if not( isinstance(ext, react_ext) ):
            raise Exception("IS NOT INSTANCE OF REACTION EXTENSION")
        elif ext.ext_for != self.get_key():
            raise Exception("UNFIMILIAR EXTENSION")
        self.__ext.append(ext)
        ext.connect(self)
        for section in ext.description:
            if section != 'none':
                self.description[section] = ext.description[section]
        
    @classmethod
    def get_key(cls): return cls.key
        
    def get_allowed_users(self):
        return self.__users
        
    def get_ext():
        return copy.copy(self.__ext)
        
    def __call__(self, bot, updates):
        for update in updates:
            self.check_update(bot, update)
        
    def check_update(self, bot, update):
        return self.check_update_ext(bot, update)
        
    def check_update_ext(self, bot, update):
        res = False
        for ext in self.__ext:
            if ext(bot, update):
                res = True
        return res
        
    def call_ext(*args, **kwargs):
        self = args[0]
        args = args[1:]
        res = False
        for ext in self.__ext:
            if ext(*args, **kwargs):
                res = True
        return res
        
class react_ext(reaction):
    def __init__(self, allowed_users):
        reaction.__init__(self, allowed_users)
    
    def connect(self, r_inst):
        self.r_inst = r_inst
    
    @classmethod
    def ext_for(cls): return cls.ext_for

class ManualDrop(Exception):
    def __init__(self):
        Exception.__init__(self, "Manual Drop")
    
#Basic
def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError:
        return False
    return True
