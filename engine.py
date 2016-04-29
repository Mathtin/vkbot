#VK Bot Engine Source File
# -*- coding: utf-8 -*-
# by Mathtin and Plaguedo

#import standart modules
from urllib.request import urlopen
from urllib.parse import urlencode
import json, copy

def ver(): return "v3.0.1"
def MathtinID(): return 24799071
def PlaguedoID(): return 185952294
def url(): return "https://api.vk.com/method/"

class VKBot:
    def __init__(self, reactions, bot_name, token, sudoers_id, vk_group_id = 101594097, shout_to = lambda *args: None):
        shout_to("Creating bot " + bot_name)
        self.__reactions = reactions
        self.__name = bot_name
        self.__smtoken = token
        self.__root_list = copy.copy(sudoers_id)
        self.__vkgroup = vk_group_id
        self.__shout = shout_to
        #Long Poll Connection Info
        self.__longpoll = {
            'key': "",
            'server': "",
            'ts': 0
        }
        #Debug print function (usually print)
        self.__shout = shout_to
        #Debug amount of info (lower level - less info)
        self.__log_level = 0
            
    def get_root_list(self):
        return copy.copy(self.__root_list)
    def get_vkgroup(self):
        return self.__vkgroup
    def get_smtoken(self):
        return self.__smtoken
    def get_name(self):
        return self.__name
    def get_log_level(self):
        return self.__log_level
    def get_shouter(self):
        return self.__shout
        
    def get_descriptions(self):
        desc = {}
        for react in self.__reactions:
            for section in react.help:
                if section != "none":
                    desc[section] = react.help[section]
        return desc
        
    def is_root(self, id):
        return id in self.__root_list
    
    #Define amount of debug info and change print function
    def subscribe(self, log_level = None, callback = None):
        if callback: self.__shout = callback
        if log_level: self.__hidden_level = log_level
        if self.__shout: self.__log_level = self.__hidden_level
        
    #Server Connection
    def startLongPollServer(self):
        method = "messages.getLongPollServer?%s"
        onsend = {
            'use_ssl': 1,
            'access_token': self.__smtoken
        }
        paramsonsend = urlencode(onsend)
        if self.__shout: self.__shout("Connecting to Longpoll server...")
        f = urlopen(url() + method % paramsonsend)
        self.active = True
        answer = f.read().decode("utf-8")
        longpoll_info = json.loads(answer)
        #Updating long poll server info
        self.__longpoll['key'] = longpoll_info["response"]["key"]
        self.__longpoll['server'] = longpoll_info["response"]["server"]
        self.__longpoll['ts'] = longpoll_info["response"]["ts"]
        if self.__shout:
            if self.__log_level >= 2: self.__shout("startLongPollServer: " + answer)
            else: self.__shout("Connected to " + self.__longpoll['server'] + " with ts " + str(self.__longpoll['ts']))
        return answer

    def LongPollListen(self):
        server = "https://" + self.__longpoll['server'] + "?%s"
        onsend = {
            'act': "a_check",
            'key': self.__longpoll['key'],
            'ts': self.__longpoll['ts'],
            'wait': 25,
            'mode': 2
        }
        paramsonsend = urlencode(onsend)
        f = urlopen(server % paramsonsend)
        answer = f.read().decode("utf-8")
        if self.__log_level >= 3:
            self.__shout("LongPollConnect: " + answer)
        if not(is_json(answer)): 
            self.active = False
            raise ConnectionResetError('VK Long Poll server dropped')
        dec = json.loads(answer)
        if "failed" in dec:
            if dec["failed"] == 1: self.__longpoll['ts'] = dec["ts"]
            else:
                self.active = False
                raise ConnectionResetError('VK Long Poll server dropped')
        return answer

    #Message Manipulation
    def parsAnswer(self, answer):
        decoded_string = json.loads(answer)
        #Updating TS
        self.__longpoll['ts'] = decoded_string["ts"]
        parsed_updates = []
        #Creating list of updates
        for update_raw in decoded_string["updates"]:
            flags = VKBot.manageFlags(update_raw[2])
            parsed_updates.append({ 
                'type': update_raw[0],    #type of update
                'raw': update_raw,        #raw data
                'flags': flags            #data flags
            })
            if parsed_updates[-1]['type']==4:
                parsed_updates[-1]['message'] = update_raw[6]
                chatID = update_raw[3]
                userID = chatID
                if chatID >= 2000000000: userID = int(update_raw[7]["from"])
                parsed_updates[-1]['chat_id'] = chatID
                parsed_updates[-1]['user_id'] = userID
                if not(flags["out"]) and self.__log_level >= 2:
                    self.__shout('Message "' + parsed_updates[-1]['message'] + '" recieved from ' + str(userID))
                if flags["out"] and self.__log_level >= 1:
                    self.__shout("Message sent")
        return parsed_updates

    def getAction(self, update):
        for reaction in self.__reactions:
            satisfies = reaction.rule(self, update)
            allowed_users = reaction.get_allowed_users()
            allowed = allowed_users == "all"
            allowed = allowed or (allowed_users == "friends" and update['user_id']['flags']['frnd'])
            allowed = allowed or (allowed_users == "root" and self.is_root(update['user_id']))
            if satisfies and allowed:
                action = reaction.pars_func(self, update)
                if self.__log_level >= 2:
                    self.__shout("Action type:\n" + str(answer))
                return action
        return BotAction()
        
    @staticmethod
    def manageFlags(n):
        flags = {
            'conf' : False,
            'media' : False,
            'fix' : False,
            'del' : False,
            'spam' : False,
            'frnd' : False,
            'chat' : False,
            'imp' : False,
            'repl' : False,
            'out' : False,
            'unrd' : False,
        }
        if n >= 8192:
            flags["conf"] = True
            n = n - 8192
        if n >= 512:
            flags["media"] = True
            n = n - 512
        if n >= 256:
            flags["fix"] = True
            n = n - 256
        if n >= 128:
            flags["del"] = True
            n = n - 128
        if n >= 64:
            flags["spam"] = True
            n = n - 64
        if n >= 32:
            flags["frnd"] = True
            n = n - 32
        if n >= 16:
            flags["chat"] = True
            n = n - 16
        if n >= 8:
            flags["imp"] = True
            n = n - 8
        if n >= 4:
            flags["repl"] = True
            n = n - 4
        if n >= 2:
            flags["out"] = True
            n = n - 2
        if n >= 1:
            flags["unrd"] = True
        return flags
    
    def sendMsgStruct(self, msg_struct):
        method = "messages.send?%s"
        paramsonsend = urlencode(msg_struct)
        if self.__log_level >= 1:
            self.__shout("Sending message...")
        f = urlopen(url() + method % paramsonsend)
        answer = f.read().decode("utf-8")
        if self.__log_level >= 2:
            self.__shout("sendMsgStruct:" + answer)
        if is_json(answer) and "error" in answer:
            decoded_string = json.loads(answer)
            if self.__log_level >= 1:
                self.__shout("Server: " + decoded_string["error"]["error_msg"])
            if decoded_string["error"]["error_code"] == 9:
                if self.__log_level >= 1:
                    self.__shout("Editing message...")
                msg_struct["message"] = "Oх...\n" + msg_struct["message"]
                self.sendMsgStruct(msg_struct)
        return answer

    #Extensions
    #Get Attachments
    def attachRecommendedAudio(self, fromid):
        method = "audio.getRecommendations?%s"
        onsend = {
            'user_id': fromid,
            'offset': 2,
            'count': 50,
            'shuffle': 1,
            'access_token': self.__smtoken
        }
        paramsonsend = urlencode(onsend)
        if self.__log_level >= 1:
            self.__shout("Getting recommendations...")
        f = urlopen(url() + method % paramsonsend)
        answer = f.read().decode("utf-8")
        if self.__log_level >= 2:
            self.__shout("attachRecommendedAudio: " + answer)
        decoded_string = json.loads(answer)
        if "error" in answer:
            if self.__log_level >= 1:
                self.__shout("Server: " + decoded_string["error"]["error_msg"])
            return None
        else:
            owner = decoded_string["response"][0]["owner_id"]
            id = decoded_string["response"][0]["aid"]
            attachment = "audio" + str(owner) + "_" + str(id)
            return attachment

    #VK API (Kuantan IP)
    def getIP(self):
        method = "status.get?%s"
        onsend = {
            'group_id': self.__vkgroup,
            'access_token': self.__smtoken
        }
        if self.__log_level >= 1:
            self.__shout("Getting IP of kuantan...")
        paramsonsend = urlencode(onsend)
        f = urlopen(url() + method % paramsonsend)
        answer = f.read().decode("utf-8")
        if self.__log_level >= 2:
            self.__shout("getIP: " + answer)
        if not(is_json(answer)):
            return "Error"
        decoded_string = json.loads(answer)
        if "error" in decoded_string:
            if self.__log_level >= 1:
                self.__shout("Server: " + decoded_string["error"]["error_msg"])
            return "Error"
        else:
            return decoded_string["response"]["text"]
        
class reaction:
    def __getitem__(self, index):
        return getattr(self, index)
    def __init__(self, allowed_users):
        self.__users = allowed_users
        self.help = {'none': 'nothing'}
    def get_key(self):
        return "none"
    def get_allowed_users(self):
        return self.__users
    def rule(self, sender, update):
        return False
    def pars_func(self, sender, update):
        return None

class BotAction:
    def __init__(self, callback = lambda *args: None, type_ = "none"):
        self.callback = callback
        self.type = type_
    def __str__(self):
        return self.type
    def __call__(self):
        return self.callback()

class BotActionWrap:
    def __init__(self, type_ = "none"):
        self.type = type_
    def __call__(self, action):
        return BotAction(action, self.type)

class SendMessage(BotAction):
    def __init__(self, sender, update):
        self.msg_struct = {
            'message': "",
            'access_token': sender.get_smtoken()
        }
        if update['chat_id'] != update['user_id']:
            self.msg_struct['chat_id'] = update['chat_id'] - 2000000000
        else:
            self.msg_struct['user_id'] = update['user_id']
        def callback():
            sender.sendMsgStruct(self.msg_struct)
        BotAction.__init__(self, callback, "message")

#Basic
def is_json(myjson):
    try:
        json_object = json.loads(myjson)
    except ValueError:
        return False
    return True
