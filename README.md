# vkbot
Modular VK Bot, wich works on "reactions"

##Basic usage example
import every thing you downloaded
```
from engine import vkbot
import react_cmd, react_ask
```
Add access token and create sequential list of reaction modules
```
smtoken = "00000....000"
reactions = [
    react_cmd.react_cmd(allowed_users = "all"),
    react_ask.react_ask(allowed_users = "all")
]
```
Finally initialise bot and start listen for updates
```
Shrek = vkbot(reactions, "Shrek", smtoken, shout_to = print)
Shrek.startLongPollServer()
while Shrek.active:
    try:
        server_answer = Shrek.LongPollListen()
        update_list = Shrek.parsAnswer(server_answer)
        for update in update_list:
            action_struct = Shrek.getActionStruct(update)
            if action_struct: Shrek.applyAction(action_struct)
    except KeyboardInterrupt:
            Shrek.active = False
    except Exeption:
        #Could be problems with internet connection
        Shrek.startLongPollServer()
```

##Allowed users
Current existing groups: **all**, **friends**, **root**

##Root
If you want to protect some reactions, change allowed_users and create list of root ids
```
...
reaction = [
    ...
    react_XXX.react_XXX(alowed_users = "root"),
    ...
]
...
root_list = [ 24799071, 18595229 ]
...
Shrek = vkbot(reactions, "Shrek", smtoken, root_list, shout_to = print)
```

##Shout to
Debug print function (usually print). You can increase amount of debug data `Shrek.subscribe(log_level = 1)`
Also change print function `Shrek.subscribe(shout_to = donkey)`
    
##We can correct surface actions before applying
```
...
            if action_struct:
                if action_struct['type'] == "message":
                    if update['user_id'] == 24799071: 
                        action_struct["message"] = action_struct["message"] + "\nYour pleasure, greatest King Daniil IV"
                    elif update['user_id'] == 18595229: 
                        action_struct["message"] = action_struct["message"] + "\nTea is ready, Senpai"
...
```

##Creating own reaction
Instructions will be added soon. You can still write your own reaction using react_ask.py or react_cmd.py as example.
