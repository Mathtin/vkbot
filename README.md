# VKBot
Modular VK Bot, wich works on "reactions"

##Basic usage example
import every thing you downloaded
```
from engine import VKBot
import react_cmd, react_ask, react_sign
```
Add access token and create sequential list of reaction modules
```
smtoken = "00000....000"
reactions = [
    react_cmd.react_cmd(   allowed_users = "all" ),
    react_ask.react_ask(   allowed_users = "all" ),
    react_sign.react_sign( allowed_users = "all" )
]
```
Finally initialise bot and start listen for updates
```
Shrek = VKBot(reactions, "Shrek", smtoken, log_to = print)
Shrek.connect()
Shrek.listen()
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
root_list = [ 24799071, 185952294 ]
...
Shrek = VKBot(reactions, "Shrek", smtoken, root_list, log_to = print)
```

##Logging
Debug print function (usually print).  
You can increase amount of debug data: `Shrek.set_logger(log_level = 1)`  
Also change print function: `Shrek.set_logger(donkey)`  
All in all: `Shrek.set_logger(donkey, 1)`

##Creating own reaction
Instructions will be added soon. You can still write your own reaction using react_ask.py or react_sign.py as example.
