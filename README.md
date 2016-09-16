# secret-agents
test assignment

## Quick start
**Enable Google Maps Api key: Geocoding and Distancematrix api used in this app**

```
[user@local ~]# git clone https://github.com/afeena/secret-agents
[user@local ~]# cd secret-agents
[user@local secret-agents] pip install -r requirements.txt
[user@local secret-agents] vim config.cfg.example #use any editor to edit config
[user@local secret-agents] mv config.cfg.example config.cfg 
[user@local secret-agents] python server.py
```
In your browser visit **http://localhost:8080** (by default) and enjoy!

OR:

In secret-agent directory, run console client

```
[user@local secret-agents] python cli.py
```

### Console commands

* add Name City - add new agent
* where Name - find agent by name
* help Name - find nearest agent and distance
* load filename.csv - uload the list of the agents
* save filename.csv - save the list of the agents
